"""
Importatore di catalogo prodotti da feed JSON
"""
import json
import os
import requests
from datetime import datetime, timezone
import logging
from typing import Dict, List, Any, Optional

from sqlalchemy.orm import Session
from app.models.models import Product, CatalogSync, ProductChange

# Logger
logger = logging.getLogger("catalog_importer")

class CatalogImporter:
    """
    Classe per importare cataloghi di prodotti da JSON esterno o locale.
    
    Gestisce l'aggiunta di nuovi prodotti, l'aggiornamento di quelli esistenti
    e tiene traccia delle modifiche.
    """
    def __init__(self, db_session: Session, source_url: str = None, json_file: str = None, version_label: str = None):
        """
        Inizializza l'importatore di catalogo.
        
        Args:
            db_session (Session): Sessione del database SQLAlchemy
            source_url (str, optional): URL da cui recuperare il JSON
            json_file (str, optional): Percorso del file JSON locale
            version_label (str, optional): Etichetta versione per il registro di sincronizzazione
        
        Raises:
            ValueError: Se non viene specificato né source_url né json_file
        """
        self.db = db_session
        self.source_url = source_url
        self.json_file = json_file
        
        if not source_url and not json_file:
            raise ValueError("È necessario specificare o source_url o json_file")
            
        self.sync_record = CatalogSync(
            source_url=source_url if source_url else f"file://{os.path.abspath(json_file)}",
            started_at=datetime.now(timezone.utc),
            import_version=version_label
        )
        self.db.add(self.sync_record)
        self.db.commit()
        
        log_message = f"Inizializzato CatalogImporter (sync_id: {self.sync_record.id}"
        if version_label:
            log_message += f", versione: {version_label}"
        log_message += ")"
        logger.info(log_message)
    
    def fetch_catalog(self) -> Optional[List[Dict[str, Any]]]:
        """
        Recupera il catalogo prodotti dalla fonte specificata.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Lista di prodotti in formato dizionario
                                           o None in caso di errore
        """
        try:
            if self.source_url:
                logger.info(f"Recupero catalogo da URL: {self.source_url}")
                response = requests.get(self.source_url, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                logger.info(f"Lettura catalogo da file: {self.json_file}")
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Gestione del formato JSON
            products = data.get("products", data) if isinstance(data, dict) else data
            
            if not isinstance(products, list):
                logger.error("Formato JSON non riconosciuto")
                self._update_sync_record(success=False, error_message="Formato JSON non valido")
                return None
                
            logger.info(f"Catalogo recuperato con successo. {len(products)} prodotti trovati.")
            return products
            
        except Exception as e:
            logger.error(f"Errore durante il recupero del catalogo: {str(e)}")
            self._update_sync_record(success=False, error_message=str(e))
            return None
    
    def import_catalog(self) -> bool:
        """
        Esegue l'importazione completa del catalogo.
        
        Returns:
            bool: True se l'importazione è avvenuta con successo, False altrimenti
        """
        products_data = self.fetch_catalog()
        if not products_data:
            return False
            
        try:
            # Ottieni prodotti esistenti
            existing_products = {p.id: p for p in self.db.query(Product).all()}
            logger.info(f"Prodotti esistenti nel database: {len(existing_products)}")
            
            # Contatori
            stats = {
                'added': 0,
                'updated': 0,
                'unchanged': 0,
                'processed_ids': set()
            }
            
            # Elaborazione prodotti
            for product_data in products_data:
                product_data = self._preprocess_product_data(product_data)
                product_id = product_data.get("id")
                
                if not product_id:
                    logger.warning(f"Prodotto senza ID trovato: {product_data}")
                    continue
                
                stats['processed_ids'].add(product_id)
                
                # Aggiorna o aggiungi prodotto
                if product_id in existing_products:
                    changes = self._update_product(existing_products[product_id], product_data)
                    stats['updated' if changes else 'unchanged'] += 1
                else:
                    self._add_product(product_data)
                    stats['added'] += 1
            
            # Gestione prodotti rimossi
            removed_ids = set(existing_products.keys()) - stats['processed_ids']
            products_removed = len(removed_ids)
            
            # Commit modifiche
            self.db.commit()
            
            # Aggiorna record sincronizzazione
            self._update_sync_record(
                success=True,
                products_total=len(products_data),
                products_added=stats['added'],
                products_updated=stats['updated'],
                products_removed=products_removed
            )
            
            logger.info(
                f"Importazione completata. "
                f"Aggiunti: {stats['added']}, "
                f"Aggiornati: {stats['updated']}, "
                f"Invariati: {stats['unchanged']}, "
                f"Rimossi: {products_removed}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Errore durante l'importazione: {str(e)}")
            self.db.rollback()
            self._update_sync_record(success=False, error_message=str(e))
            return False
    
    def _preprocess_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preelabora i dati del prodotto prima dell'importazione.
        
        Args:
            product_data (Dict[str, Any]): Dati grezzi del prodotto
            
        Returns:
            Dict[str, Any]: Dati preprocessati
        """
        return {
            key: json.dumps(value) if isinstance(value, list) 
            else (value if value is not None else '')
            for key, value in product_data.items()
        }
    
    def _add_product(self, product_data: Dict[str, Any]) -> Product:
        """
        Aggiunge un nuovo prodotto al database.
        
        Args:
            product_data (Dict[str, Any]): Dati del prodotto
            
        Returns:
            Product: Istanza del nuovo prodotto
        """
        # Conversione valori numerici
        price = float(product_data.get("price", 0)) if product_data.get("price") else None
        sale_price = float(product_data.get("sale_price", 0)) if product_data.get("sale_price") else None
        
        # Crea il prodotto con tutti i campi disponibili
        product = Product(
            id=product_data.get("id"),
            item_group_id=product_data.get("item_group_id", ''),
            title=product_data.get("title", ''),
            description=product_data.get("description", ''),
            price=price,
            sale_price=sale_price,
            brand=product_data.get("brand", ''),
            condition=product_data.get("condition", ''),
            availability=product_data.get("availability", ''),
            color=product_data.get("color", ''),
            material=product_data.get("material", ''),
            mpn=product_data.get("mpn", ''),
            availability_date=product_data.get("availability_date", ''),
            google_product_category=product_data.get("google_product_category", ''),
            product_type=product_data.get("product_type", ''),
            link=product_data.get("link", ''),
            mobile_link=product_data.get("mobile_link", ''),
            image_link=product_data.get("image_link", ''),
            additional_image_links=product_data.get("additional_image_links", ''),
            custom_label_1=product_data.get("custom_label_1", ''),
            custom_label_2=product_data.get("custom_label_2", ''),
            custom_label_3=product_data.get("custom_label_3", ''),
            custom_label_4=product_data.get("custom_label_4", ''),
            raw_data=product_data,
            last_synced=datetime.now(timezone.utc)
        )
        
        self.db.add(product)
        return product
    
    def _update_product(self, product: Product, product_data: Dict[str, Any]) -> List[ProductChange]:
        """
        Aggiorna un prodotto esistente e registra le modifiche.
        
        Args:
            product (Product): Prodotto esistente da aggiornare
            product_data (Dict[str, Any]): Nuovi dati del prodotto
            
        Returns:
            List[ProductChange]: Lista delle modifiche effettuate
        """
        changes = []
        update_fields = {
            'title': str,
            'description': str,
            'price': lambda x: float(x) if x else None,
            'sale_price': lambda x: float(x) if x else None,
            'brand': str,
            'condition': str,
            'availability': str,
            'color': str,
            'material': str,
            'mpn': str,
            'availability_date': str,
            'google_product_category': str,
            'product_type': str,
            'link': str,
            'mobile_link': str,
            'image_link': str,
            'additional_image_links': str,
            'custom_label_1': str,
            'custom_label_2': str,
            'custom_label_3': str,
            'custom_label_4': str
        }
        
        for field, converter in update_fields.items():
            if field in product_data:
                new_value = converter(product_data[field])
                old_value = getattr(product, field)
                
                if new_value != old_value:
                    setattr(product, field, new_value)
                    changes.append(
                        ProductChange(
                            product_id=product.id,
                            sync_id=self.sync_record.id,
                            field_name=field,
                            old_value=str(old_value),
                            new_value=str(new_value),
                            changed_at=datetime.now(timezone.utc)
                        )
                    )
        
        if changes:
            self.db.add_all(changes)
        
        product.last_synced = datetime.now(timezone.utc)
        return changes
    
    def _update_sync_record(self, **kwargs):
        """
        Aggiorna il record di sincronizzazione con i risultati.
        
        Args:
            **kwargs: Coppie chiave-valore da aggiornare
        """
        for key, value in kwargs.items():
            setattr(self.sync_record, key, value)
        self.sync_record.completed_at = datetime.now(timezone.utc)
        self.db.commit()
