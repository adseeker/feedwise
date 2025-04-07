#!/usr/bin/env python3
"""
Applicazione principale FeedWise.
Avvia lo scheduler interno e serve una dashboard web.
"""
import os
import logging
import signal
import time
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, Response, url_for
from sqlalchemy import func
from threading import Thread

from app_scheduler import start_scheduler, ensure_db_initialized, run_scheduled_import, FEED_URL
from ai_assistant import handle_conversation
from database import get_db
from models import Product, CatalogSync, ProductChange
from catalog_importer import CatalogImporter

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

# Inizializzazione Flask
app = Flask(__name__, template_folder="templates")
app.config['JSON_AS_ASCII'] = False

# Gestione della chiusura dell'applicazione
def signal_handler(sig, frame):
    logger.info("Arresto dell'applicazione in corso...")
    # In futuro qui potresti aggiungere altre operazioni di pulizia
    exit(0)

# Routes per la dashboard
@app.route('/')
def dashboard():
    """Mostra la dashboard principale."""
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    """Mostra la pagina del catalogo prodotti."""
    return render_template('catalog.html')

@app.route('/chat')
def chat():
    """Mostra la pagina della chat con l'assistente AI."""
    return render_template('chat.html')

@app.route('/import')
def import_page():
    """Mostra la pagina di importazione feed."""
    return render_template('import.html')

@app.route('/settings')
def settings():
    """Mostra la pagina delle impostazioni."""
    return render_template('settings.html')

@app.route('/api/dashboard')
def dashboard_data():
    """API per i dati della dashboard."""
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

@app.route('/api/products')
def get_products():
    """API per ottenere tutti i prodotti."""
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
                        'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M') if product.updated_at else None
                    }
                    
                    # Aggiungi il campo availability_date se esiste nella tabella
                    try:
                        product_dict['availability_date'] = product.availability_date 
                    except:
                        product_dict['availability_date'] = None
                    
                    products_data.append(product_dict)
                except Exception as e:
                    logger.error(f"Errore nell'elaborazione del prodotto {product.id}: {str(e)}")
            
            return jsonify(products_data)
    except Exception as e:
        logger.error(f"Errore nel caricamento dei prodotti: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API per la chat con l'assistente AI."""
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

@app.route('/static/placeholder.png')
def placeholder_image():
    """Serve a placeholder image for products without images."""
    # Simple placeholder SVG image
    svg = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#cccccc" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <path d="M21 15l-5-5L5 21"></path>
    </svg>
    '''
    return Response(svg, mimetype='image/svg+xml')

@app.route('/api/import', methods=['POST'])
def start_import():
    """API per avviare una nuova importazione."""
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

def run_import(source_url, json_file, version_label):
    """Esegue un'importazione in background."""
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

def format_time_ago(timestamp):
    """Formatta un timestamp come tempo relativo (es. "2 ore fa")."""
    if not timestamp:
        return "Mai"
    
    # Convert timestamp to be timezone-aware if it isn't already
    if timestamp.tzinfo is None:
        # Assume UTC if no timezone specified
        from datetime import timezone
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Get current time in UTC to match timestamp
    now = datetime.now(timezone.utc)
    diff = now - timestamp
    
    if diff < timedelta(minutes=1):
        return "Appena ora"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} {'minuto' if minutes == 1 else 'minuti'} fa"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} {'ora' if hours == 1 else 'ore'} fa"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} {'giorno' if days == 1 else 'giorni'} fa"
    else:
        return timestamp.strftime('%Y-%m-%d %H:%M')

def main():
    """Funzione principale dell'applicazione."""
    logger.info("Avvio dell'applicazione FeedWise...")
    
    # Assicurati che il database sia inizializzato
    ensure_db_initialized()
    
    # Avvia lo scheduler interno
    scheduler = start_scheduler()
    
    # Esegui anche un'importazione immediata all'avvio
    from threading import Thread
    import time
    logger.info("Avvio importazione iniziale...")
    Thread(target=lambda: (time.sleep(2), run_scheduled_import())).start()
    
    # Registra il gestore di segnali per la chiusura pulita
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Avvio server web sulla porta 8080...")
    
    # Avvia il server web
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    
    try:
        # Il server Flask gestisce già il loop principale
        pass
    except KeyboardInterrupt:
        logger.info("Interruzione richiesta dall'utente.")
        scheduler.shutdown()
        logger.info("Applicazione terminata.")

if __name__ == "__main__":
    main()