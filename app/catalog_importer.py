import json
import os
import requests
from datetime import datetime, timezone
import logging
from typing import Dict, List, Any, Optional

from sqlalchemy.orm import Session
from models import Product, CatalogSync, ProductChange
from database import init_db, DatabaseSession

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("catalog_importer")

class CatalogImporter:
    def __init__(self, db_session: Session, source_url: str = None, json_file: str = None, version_label: str = None):
        self.db = db_session
        self.source_url = source_url
        self.json_file = json_file
        
        if not source_url and not json_file:
            raise ValueError("È necessario specificare o source_url o json_file")
            
        # Correzione: rimuovi la chiamata extra a ()
        self.sync_record = CatalogSync(
            source_url=source_url if source_url else f"file://{os.path.abspath(json_file)}",
            started_at=datetime.now(timezone.utc),  # Rimuovi ()
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
        return {
            key: json.dumps(value) if isinstance(value, list) 
            else (value if value is not None else '')
            for key, value in product_data.items()
        }
    
    def _add_product(self, product_data: Dict[str, Any]) -> Product:
        # Conversione valori numerici
        price = float(product_data.get("price", 0)) if product_data.get("price") else None
        sale_price = float(product_data.get("sale_price", 0)) if product_data.get("sale_price") else None
        
        # Non ci sono conversioni speciali da fare per availability_date
                
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
        
        product.last_synced = datetime.now(timezone.utc)
        return changes
    
    def _update_sync_record(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.sync_record, key, value)
        self.sync_record.completed_at = datetime.now(timezone.utc)
        self.db.commit()

# Script principale invariato
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Importatore di catalogo JSON nel database SQLite")
    parser.add_argument("--url", help="URL da cui recuperare il catalogo JSON")
    parser.add_argument("--file", help="File JSON locale da importare")
    parser.add_argument("--init-db", action="store_true", help="Inizializza il database prima dell'importazione")
    
    args = parser.parse_args()
    
    if args.init_db:
        init_db()
    
    if not args.url and not args.file:
        print("Errore: Specificare --url o --file")
        exit(1)
    
    with DatabaseSession() as db:
        importer = CatalogImporter(
            db_session=db,
            source_url=args.url,
            json_file=args.file
        )
        
        success = importer.import_catalog()
        
        if success:
            print("✅ Importazione completata con successo!")
        else:
            print("❌ Errore durante l'importazione")
            exit(1)