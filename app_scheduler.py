#!/usr/bin/env python3
"""
Scheduler interno per l'applicazione FeedWise.
Gestisce l'esecuzione automatica delle importazioni del feed.
"""
import os
import logging
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import init_db, DatabaseSession
from catalog_importer import CatalogImporter
from models import CatalogSync

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app_scheduler")

# Assicurati che le directory esistano
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Configurazione del feed
FEED_URL = "https://repository.mobilifiver.com/public/feed/test_json/test.json"
FEED_PREFIX = "feed"  # Prefisso per le etichette di versione

def ensure_db_initialized():
    """Assicura che il database sia inizializzato."""
    try:
        from database import engine
        from models import Base
        if not os.path.exists("data/catalog.db"):
            logger.info("Inizializzazione database...")
            init_db()
            logger.info("Database inizializzato.")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {str(e)}")
        raise

def run_scheduled_import():
    """Esegue l'importazione programmata del feed."""
    logger.info("Avvio importazione programmata")
    
    try:
        # Crea etichetta con data corrente
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        version_label = f"{FEED_PREFIX}_{current_datetime}"
        
        # Verifica se esiste già un'importazione nelle ultime due ore
        with DatabaseSession() as db:
            # Rimosso controllo duplicati per permettere più importazioni durante il test
                
            # Esegui l'importazione
            importer = CatalogImporter(
                db_session=db,
                source_url=FEED_URL,
                version_label=version_label
            )
            success = importer.import_catalog()
            
            if success:
                logger.info(f"Importazione {version_label} completata con successo!")
            else:
                logger.error(f"Importazione {version_label} fallita.")
    
    except Exception as e:
        logger.error(f"Errore durante l'importazione programmata: {str(e)}")

def start_scheduler():
    """Avvia lo scheduler con i job configurati."""
    scheduler = BackgroundScheduler()
    
    # Aggiungi il job per l'importazione giornaliera (alle 6:00 AM)
    scheduler.add_job(
        run_scheduled_import,
        trigger=CronTrigger(hour=6, minute=0),
        id='daily_import',
        name='Importazione giornaliera del feed',
        replace_existing=True
    )
    
    # Aggiungi anche un job per testing che esegue ogni 15 minuti
    scheduler.add_job(
        run_scheduled_import,
        trigger=CronTrigger(minute='*/15'),  # Ogni 15 minuti
        id='test_import',
        name='Importazione test ogni 15 minuti',
        replace_existing=True
    )
    
    # Avvia lo scheduler
    scheduler.start()
    logger.info("Scheduler avviato con successo. L'importazione verrà eseguita ogni giorno alle 6:00 AM.")
    
    return scheduler

if __name__ == "__main__":
    # Assicurati che il database sia inizializzato
    ensure_db_initialized()
    
    # Esegui l'importazione immediatamente (opzionale)
    run_scheduled_import()
    
    # Avvia lo scheduler
    scheduler = start_scheduler()
    
    # Mantieni il processo attivo
    try:
        # Loop infinito per mantenere il programma in esecuzione
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler arrestato.")