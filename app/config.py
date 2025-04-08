"""
Configurazioni dell'applicazione FeedWise
"""
import os
import logging

class Config:
    """Configurazione base dell'applicazione"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'feedwise-sviluppo-chiave'
    
    # Percorsi
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATABASE_DIR = os.path.join(BASE_DIR, 'data')
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'catalog.db')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Configurazioni Flask
    JSON_AS_ASCII = False
    
    # Configurazioni Feed
    DEFAULT_FEED_URL = os.environ.get('DEFAULT_FEED_URL', 'http://example.com/feed.json')
    
    # Configurazioni logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_LEVEL = logging.INFO

class DevelopmentConfig(Config):
    """Configurazione per ambiente di sviluppo"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configurazione per ambiente di test"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = os.path.join(Config.DATABASE_DIR, 'testing.db')

class ProductionConfig(Config):
    """Configurazione per ambiente di produzione"""
    DEBUG = False
    TESTING = False
    # In produzione, usare una chiave segreta forte
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'produzione-chiave-molto-segreta'
    LOG_LEVEL = logging.WARNING
