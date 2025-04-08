"""
Rotte principali dell'applicazione web FeedWise
"""
from flask import Blueprint, render_template, current_app
import logging

# Logger
logger = logging.getLogger("routes.main")

# Blueprint per le rotte principali
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Mostra la dashboard principale."""
    logger.debug("Accesso alla dashboard")
    return render_template('index.html')

@main_bp.route('/catalog')
def catalog():
    """Mostra la pagina del catalogo prodotti."""
    logger.debug("Accesso al catalogo")
    return render_template('catalog.html')

@main_bp.route('/chat')
def chat():
    """Mostra la pagina della chat con l'assistente AI."""
    logger.debug("Accesso alla chat")
    return render_template('chat.html')

@main_bp.route('/import')
def import_page():
    """Mostra la pagina di importazione feed."""
    logger.debug("Accesso alla pagina di importazione")
    return render_template('import.html')

@main_bp.route('/settings')
def settings():
    """Mostra la pagina delle impostazioni."""
    logger.debug("Accesso alle impostazioni")
    return render_template('settings.html')
