#!/usr/bin/env python3
"""
Script per l'importazione programmata del catalogo.
Può essere eseguito come cronjob o task pianificato.
"""
import logging
import datetime
import argparse
import os
from database import init_db, DatabaseSession
from catalog_importer import CatalogImporter
from models import CatalogSync, Product, ProductChange
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scheduled_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduled_import")

def ensure_directory(directory):
    """Assicura che la directory esista"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Creata directory: {directory}")

def run_import(catalog_url, label_prefix=None):
    """
    Esegue l'importazione del catalogo con etichetta temporale.
    
    Args:
        catalog_url: URL del feed da importare
        label_prefix: Prefisso opzionale per l'etichetta (default: 'feed')
    
    Returns:
        bool: True se l'importazione è riuscita, False altrimenti
    """
    # Crea etichetta con data corrente
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    prefix = label_prefix or "feed"
    version_label = f"{prefix}_{current_datetime}"
    
    logger.info(f"Avvio importazione programmata: {version_label}")
    logger.info(f"URL catalogo: {catalog_url}")
    
    # Verifica se esiste già un'importazione con questa etichetta
    with DatabaseSession() as db:
        existing = db.query(CatalogSync).filter(CatalogSync.import_version == version_label).first()
        if existing:
            logger.warning(f"Esiste già un'importazione con etichetta {version_label}.")
            if existing.success:
                logger.info("L'importazione precedente è stata completata con successo.")
                return True
            else:
                logger.info("L'importazione precedente è fallita. Riprovo.")

    # Esegui l'importazione
    try:
        with DatabaseSession() as db:
            importer = CatalogImporter(
                db_session=db,
                source_url=catalog_url,
                version_label=version_label
            )
            success = importer.import_catalog()
            
            if success:
                logger.info(f"Importazione {version_label} completata con successo!")
                
                # Esegui alcune statistiche opzionali
                products_count = db.query(Product).count()
                latest_sync = db.query(CatalogSync).order_by(CatalogSync.id.desc()).first()
                
                logger.info(f"Statistiche dopo importazione:")
                logger.info(f"- Prodotti totali nel database: {products_count}")
                logger.info(f"- Prodotti aggiunti in questa importazione: {latest_sync.products_added}")
                logger.info(f"- Prodotti aggiornati in questa importazione: {latest_sync.products_updated}")
                
                return True
            else:
                logger.error(f"Importazione {version_label} fallita.")
                return False
                
    except Exception as e:
        logger.error(f"Errore durante l'importazione programmata: {str(e)}")
        return False

if __name__ == "__main__":
    # Assicurati che le directory esistano
    ensure_directory("data")
    ensure_directory("logs")
    
    # Configura argomenti da linea di comando
    parser = argparse.ArgumentParser(description="Importazione programmata del catalogo")
    parser.add_argument("--url", default="https://repository.mobilifiver.com/public/feed/test_json/test.json",
                      help="URL del feed da importare")
    parser.add_argument("--prefix", default="feed",
                      help="Prefisso per l'etichetta di versione")
    parser.add_argument("--init-db", action="store_true",
                      help="Inizializza il database se non esiste")
    
    args = parser.parse_args()
    
    # Inizializza DB se richiesto
    if args.init_db:
        init_db()
    
    # Esegui importazione
    success = run_import(args.url, args.prefix)
    
    # Imposta codice di uscita appropriato
    exit(0 if success else 1)