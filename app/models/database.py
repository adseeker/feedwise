"""
Gestione del database con SQLAlchemy
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app

# Configurazione logging
logger = logging.getLogger("database")

# Base per i modelli
Base = declarative_base()

# Dichiarazione variabili globali
engine = None
SessionLocal = None
db_session = None

def init_db(app):
    """
    Inizializza il database creando l'engine e la sessione.
    """
    global engine, SessionLocal, db_session
    
    # URL di connessione per SQLite
    database_path = app.config['DATABASE_PATH']
    database_dir = os.path.dirname(database_path)
    
    # Assicuriamo che la directory del database esista
    os.makedirs(database_dir, exist_ok=True)
    
    database_url = f"sqlite:///{database_path}"
    
    logger.info(f"Connessione al database: {database_url}")
    
    # Creazione dell'engine SQLAlchemy
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Necessario per SQLite in ambiente multi-thread
        echo=app.config['DEBUG']  # Attiva il logging SQL in modalità debug
    )

    # Creazione della session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Creazione di una sessione con scope thread-local per applicazioni multi-thread
    db_session = scoped_session(SessionLocal)
    
    # Associa la sessione alla base
    Base.query = db_session.query_property()
    
    logger.info("Inizializzazione del database completata")

def ensure_db_initialized():
    """
    Assicura che tutte le tabelle del database siano create.
    """
    # Importiamo i modelli qui per evitare dipendenze circolari
    from app.models.models import Product, CatalogSync, ProductChange
    
    logger.info("Verifica delle tabelle del database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelle del database verificate e create se necessario!")

def get_db():
    """
    Fornisce una sessione di database.
    Uso: 'with get_db() as db: ...'
    """
    return DatabaseSession()

# Context manager per la sessione
class DatabaseSession:
    """
    Context manager per gestire le sessioni del database.
    Uso: 'with get_db() as db: ...'
    """
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
