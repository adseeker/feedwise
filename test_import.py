#!/usr/bin/env python3
"""
Script per testare l'importazione del catalogo nel database.
"""
from database import init_db, DatabaseSession
from catalog_importer import CatalogImporter
from models import Product, CatalogSync, ProductChange
import logging

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_import")

def run_import_test():
    """
    Esegue un test completo di importazione del catalogo.
    """
    # 1. Inizializza il database (crea le tabelle)
    logger.info("Inizializzazione del database...")
    init_db()
    
    # 2. URL del catalogo da importare
    catalog_url = "https://repository.mobilifiver.com/public/feed/test_json/test.json"
    
    # 3. Importa il catalogo
    logger.info(f"Avvio importazione da {catalog_url}")
    with DatabaseSession() as db:
        importer = CatalogImporter(db_session=db, source_url=catalog_url)
        success = importer.import_catalog()
        
        if not success:
            logger.error("Importazione fallita!")
            return False
        
        # 4. Verifica i risultati
        product_count = db.query(Product).count()
        sync_record = db.query(CatalogSync).order_by(CatalogSync.id.desc()).first()
        changes_count = db.query(ProductChange).count()
        
        logger.info(f"Importazione completata con successo!")
        logger.info(f"- Prodotti nel database: {product_count}")
        logger.info(f"- Prodotti aggiunti: {sync_record.products_added}")
        logger.info(f"- Prodotti aggiornati: {sync_record.products_updated}")
        logger.info(f"- Modifiche tracciate: {changes_count}")
        
        # 5. Esempio di query per vedere alcuni prodotti
        logger.info("\nEsempio di prodotti importati:")
        products = db.query(Product).limit(5).all()
        for product in products:
            logger.info(f"- {product.id}: {product.title} - {product.price}€")
        
        return True

def test_query_operations():
    """
    Testa alcune operazioni di query utili.
    """
    logger.info("\nTest query di esempio:")
    
    with DatabaseSession() as db:
        # 1. Trova prodotti per marca
        brand = "Mobili Fiver"
        brand_products = db.query(Product).filter(Product.brand == brand).count()
        logger.info(f"Prodotti di marca '{brand}': {brand_products}")
        
        # 2. Trova prodotti per intervallo di prezzo
        price_range_products = db.query(Product).filter(
            Product.price >= 100,
            Product.price <= 200
        ).count()
        logger.info(f"Prodotti con prezzo tra 100€ e 200€: {price_range_products}")
        
        # 3. Cerca prodotti per parola chiave nella descrizione
        keyword = "design"
        keyword_products = db.query(Product).filter(
            Product.description.ilike(f"%{keyword}%")
        ).count()
        logger.info(f"Prodotti con '{keyword}' nella descrizione: {keyword_products}")
        
        # 4. Recupera le ultime sincronizzazioni
        syncs = db.query(CatalogSync).order_by(CatalogSync.started_at.desc()).limit(3).all()
        logger.info("\nUltime sincronizzazioni:")
        for sync in syncs:
            logger.info(f"- ID: {sync.id}, Data: {sync.started_at}, Successo: {sync.success}, Prodotti: {sync.products_total}")
        
        # 5. Trova le ultime modifiche ai prodotti
        changes = db.query(ProductChange).order_by(ProductChange.changed_at.desc()).limit(5).all()
        logger.info("\nUltime modifiche ai prodotti:")
        for change in changes:
            logger.info(f"- Prodotto: {change.product_id}, Campo: {change.field_name}, "
                       f"Da: {change.old_value} → A: {change.new_value}")


if __name__ == "__main__":
    if run_import_test():
        test_query_operations()
    else:
        logger.error("Test di importazione fallito. Operazioni di query saltate.")