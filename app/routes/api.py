"""
API per l'applicazione FeedWise
"""
from flask import Blueprint, jsonify, request, Response, current_app
import logging
from datetime import datetime
from sqlalchemy import func
from threading import Thread

from app.models.database import get_db
from app.models.models import Product, CatalogSync, ProductChange
from app.services.catalog_importer import CatalogImporter
from app.services.ai_assistant import handle_conversation
from app.services.scheduler import run_scheduled_import
from app.utils.helpers import format_time_ago

# Logger
logger = logging.getLogger("routes.api")

# Blueprint per le API
api_bp = Blueprint('api', __name__)

@api_bp.route('/dashboard')
def dashboard_data():
    """API per i dati della dashboard."""
    logger.debug("Richiesta dati dashboard")
    
    try:
        with get_db() as db:
            # Conta totale prodotti
            total_products = db.query(func.count(Product.id)).scalar() or 0
            
            # Conta sincronizzazioni
            total_syncs = db.query(func.count(CatalogSync.id)).scalar() or 0
            
            # Ultima sincronizzazione
            last_sync = db.query(CatalogSync).order_by(CatalogSync.completed_at.desc()).first()
            last_sync_time = "Mai" if not last_sync else format_time_ago(last_sync.completed_at)
            
            # Totale modifiche
            total_changes = db.query(func.count(ProductChange.id)).scalar() or 0
            
            # Lista sincronizzazioni recenti
            recent_syncs = db.query(CatalogSync).order_by(CatalogSync.completed_at.desc()).limit(10).all()
            syncs_data = []
            
            for sync in recent_syncs:
                syncs_data.append({
                    'id': sync.id,
                    'version': sync.import_version,
                    'date': sync.completed_at.strftime('%Y-%m-%d %H:%M') if sync.completed_at else sync.started_at.strftime('%Y-%m-%d %H:%M'),
                    'source': sync.source_url,
                    'products': sync.products_total,
                    'added': sync.products_added,
                    'updated': sync.products_updated,
                    'removed': sync.products_removed,
                    'success': sync.success
                })
            
            return jsonify({
                'totalProducts': total_products,
                'totalSyncs': total_syncs,
                'lastSync': last_sync_time,
                'totalChanges': total_changes,
                'syncs': syncs_data
            })
    except Exception as e:
        logger.error(f"Errore nel recupero dati dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/products')
def get_products():
    """API per ottenere tutti i prodotti."""
    logger.debug("Richiesta lista prodotti")
    
    try:
        with get_db() as db:
            products = db.query(Product).all()
            products_data = []
            
            for product in products:
                try:
                    product_dict = {
                        'id': product.id,
                        'title': product.title,
                        'description': product.description,
                        'price': product.price,
                        'sale_price': product.sale_price,
                        'brand': product.brand,
                        'condition': product.condition,
                        'availability': product.availability,
                        'color': product.color,
                        'material': product.material,
                        'product_type': product.product_type,
                        'google_product_category': product.google_product_category,
                        'link': product.link,
                        'image_link': product.image_link,
                        'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M') if product.updated_at else None,
                        'availability_date': product.availability_date
                    }
                    
                    products_data.append(product_dict)
                except Exception as e:
                    logger.error(f"Errore nell'elaborazione del prodotto {product.id}: {str(e)}")
            
            return jsonify(products_data)
    except Exception as e:
        logger.error(f"Errore nel caricamento dei prodotti: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """API per la chat con l'assistente AI."""
    logger.debug("Richiesta chat API")
    
    try:
        data = request.json
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        # Assicurati che la cronologia della conversazione sia valida
        if not isinstance(conversation_history, list):
            conversation_history = []
        
        # Ottieni la risposta dall'assistente AI
        response = handle_conversation(conversation_history, message)
        
        return jsonify({
            'response': response
        })
    except Exception as e:
        logger.error(f"Errore nell'API di chat: {str(e)}")
        return jsonify({
            'error': 'Si è verificato un errore durante l\'elaborazione della richiesta',
            'response': 'Mi dispiace, si è verificato un errore. Riprova più tardi.'
        }), 500

@api_bp.route('/import', methods=['POST'])
def start_import():
    """API per avviare una nuova importazione."""
    logger.debug("Richiesta importazione")
    
    source_type = request.json.get('source_type')
    source_url = request.json.get('url')
    version_label = request.json.get('version_label')
    
    if source_type == 'url' and source_url:
        # Avvia l'importazione in un thread separato per non bloccare l'API
        thread = Thread(target=run_import, args=(source_url, None, version_label))
        thread.daemon = True
        thread.start()
        return jsonify({'success': True, 'message': 'Importazione avviata'})
    elif source_type == 'file':
        # In una implementazione reale, qui gestiresti l'upload del file
        return jsonify({'success': False, 'message': 'Importazione da file non ancora implementata'})
    elif source_type == 'default':
        # Usa l'URL predefinito del feed
        thread = Thread(target=run_scheduled_import)
        thread.daemon = True
        thread.start()
        return jsonify({'success': True, 'message': 'Importazione avviata con URL predefinito'})
    else:
        return jsonify({'success': False, 'message': 'Parametri non validi'})

@api_bp.route('/placeholder.png')
def placeholder_image():
    """Serve a placeholder image for products without images."""
    logger.debug("Richiesta immagine placeholder")
    
    # Simple placeholder SVG image
    svg = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#cccccc" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <path d="M21 15l-5-5L5 21"></path>
    </svg>
    '''
    return Response(svg, mimetype='image/svg+xml')

def run_import(source_url, json_file, version_label):
    """Esegue un'importazione in background."""
    logger.info(f"Avvio importazione da {source_url}")
    
    with get_db() as db:
        try:
            importer = CatalogImporter(
                db_session=db,
                source_url=source_url,
                json_file=json_file,
                version_label=version_label
            )
            success = importer.import_catalog()
            logger.info(f"Importazione completata con successo: {success}")
        except Exception as e:
            logger.error(f"Errore durante l'importazione: {str(e)}")
