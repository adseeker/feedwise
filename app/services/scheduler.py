"""
Scheduler interno per l'applicazione FeedWise.
Gestisce l'esecuzione automatica delle importazioni del feed.
"""
import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from app.models.database import get_db, ensure_db_initialized
from app.services.catalog_importer import CatalogImporter
from app.models.models import CatalogSync

# Logger
logger = logging.getLogger("scheduler")

# Configurazione del feed (valore di fallback, in genere letto da config)
FEED_URL = "https://repository.mobilifiver.com/public/feed/test_json/test.json"
FEED_PREFIX = "feed"  # Prefisso per le etichette di versione

def run_scheduled_import():
    """
    Esegue l'importazione programmata del feed.
    
    Returns:
        bool: True se l'importazione è avvenuta con successo, False altrimenti
    """
    logger.info("Avvio importazione programmata")
    
    try:
        # Crea etichetta con data corrente
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        version_label = f"{FEED_PREFIX}_{current_datetime}"
        
        # Esegui l'importazione
        with get_db() as db:
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
                
            return success
    
    except Exception as e:
        logger.error(f"Errore durante l'importazione programmata: {str(e)}")
        return False

def start_scheduler():
    """
    Avvia lo scheduler con i job configurati.
    
    Returns:
        BackgroundScheduler: L'istanza dello scheduler avviato
    """
    scheduler = BackgroundScheduler()
    
    # Aggiungi il job per l'importazione giornaliera (alle 6:00 AM)
    scheduler.add_job(
        run_scheduled_import,
        trigger=CronTrigger(hour=6, minute=0),
        id='daily_import',
        name='Importazione giornaliera del feed',
        replace_existing=True
    )
    
    # In ambiente di sviluppo, aggiungi anche un job che esegue ogni 15 minuti
    if os.environ.get('FLASK_ENV') == 'development':
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
