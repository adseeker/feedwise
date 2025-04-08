"""
FeedWise - Applicazione di gestione feed di prodotti
"""
from flask import Flask

def create_app(config_object='app.config.DevelopmentConfig'):
    """
    Factory pattern per la creazione dell'applicazione Flask
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Inizializzazione del database
    from app.models.database import init_db
    init_db(app)
    
    # Registrazione dei blueprint
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
