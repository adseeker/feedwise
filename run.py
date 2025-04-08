#!/usr/bin/env python3
"""
Script di avvio dell'applicazione FeedWise
"""
import os
import logging
import signal
from app import create_app
from app.services.scheduler import start_scheduler
from app.models.database import ensure_db_initialized

def setup_logging(app):
    """Configura il sistema di logging"""
    # Assicurati che la directory dei log esista
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    
    # Configurazione logging
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format=app.config['LOG_FORMAT'],
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("feedwise")

def signal_handler(sig, frame):
    """Gestisce la chiusura graceful dell'applicazione"""
    logger.info("Arresto dell'applicazione in corso...")
    # In futuro qui potresti aggiungere altre operazioni di pulizia
    exit(0)

if __name__ == "__main__":
    # Crea l'applicazione Flask
    app = create_app()
    
    # Configura il logging
    logger = setup_logging(app)
    logger.info("Avvio dell'applicazione FeedWise...")
    
    # Assicurati che il database sia inizializzato
    ensure_db_initialized()
    
    # Avvia lo scheduler interno
    scheduler = start_scheduler()
    
    # Registra il gestore di segnali per la chiusura pulita
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Avvio server web sulla porta {os.environ.get('PORT', 8080)}...")
    
    # Avvia il server web
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 8080)),
        debug=app.config['DEBUG'],
        use_reloader=False  # Disabilita il reloader per evitare problemi con lo scheduler
    )
