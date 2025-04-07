from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("database")

# URL di connessione per SQLite (file locale)
DATABASE_URL = "sqlite:///data/catalog.db"

# Creazione dell'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessario per SQLite in ambiente multi-thread
    echo=False  # Impostare a True per vedere le query SQL generate
)

# Creazione della session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creazione di una sessione con scope thread-local per applicazioni multi-thread
db_session = scoped_session(SessionLocal)

# Base per i modelli
Base = declarative_base()

def init_db():
    """
    Inizializza il database creando tutte le tabelle definite nei modelli.
    """
    # Importiamo i modelli qui per evitare dipendenze circolari
    # Importante: assicurati che i modelli siano importati prima di creare le tabelle
    from models import Product, CatalogSync, ProductChange
    
    logger.info("Inizializzazione del database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database inizializzato con successo!")

def get_db():
    """
    Fornisce una sessione di database.
    Uso: 'with get_db() as db: ...'
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Esempio di context manager per la sessione
class DatabaseSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

# Utilizzo: 
# with DatabaseSession() as db:
#     products = db.query(Product).all()