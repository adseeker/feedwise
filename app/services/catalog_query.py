"""
Modulo per eseguire query sul catalogo prodotti usando linguaggio naturale.
Versione semplificata che sarà implementata in futuro con NLP più avanzato.
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import func, or_, desc
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.models import Product, CatalogSync, ProductChange

# Logger
logger = logging.getLogger("catalog_query")

def execute_query(query_text: str) -> Dict[str, Any]:
    """
    Esegue una query in linguaggio naturale sul catalogo.
    
    Args:
        query_text: Query in linguaggio naturale
        
    Returns:
        Dict con risultati della query e metadati
    """
    logger.info(f"Esecuzione query: {query_text}")
    
    # Normalizza la query
    query_text = query_text.lower().strip()
    
    # Analisi semplificata dell'intento
    intent = "unknown"
    
    # Controllo per ID prodotto specifico
    import re
    product_id_match = re.search(r'\b([A-Za-z0-9]{6,})\b', query_text)
    
    if "statistiche" in query_text or "statistiche del catalogo" in query_text:
        intent = "stats"
        return get_catalog_stats_response()
    
    elif "novità" in query_text or "modifiche recenti" in query_text:
        intent = "changes"
        return get_recent_changes_response()
    
    elif product_id_match:
        # Probabile richiesta di informazioni su prodotto specifico
        product_id = product_id_match.group(1)
        intent = "product_info"
        return get_product_info_response(product_id)
    
    elif any(keyword in query_text for keyword in ["prezzo", "costo", "economico", "costoso"]):
        # Query relativa al prezzo
        intent = "product_price"
        
        if "sotto" in query_text or "meno di" in query_text:
            # Cerca un valore numerico
            price_match = re.search(r'(\d+)', query_text)
            if price_match:
                price_limit = float(price_match.group(1))
                return get_products_by_price_response(max_price=price_limit)
        
        elif "sopra" in query_text or "più di" in query_text:
            price_match = re.search(r'(\d+)', query_text)
            if price_match:
                price_limit = float(price_match.group(1))
                return get_products_by_price_response(min_price=price_limit)
                
        # Fallback: mostra prodotti più economici
        return get_products_by_price_response(max_price=100, limit=5)
    
    # Ricerca per categoria
    categories = ["tavolo", "sedia", "mobile", "libreria", "scaffale", "cassettiera"]
    for category in categories:
        if category in query_text:
            intent = "product_category"
            return get_products_by_category_response(category)
    
    # Se non riusciamo a capire l'intento, eseguiamo una ricerca full-text
    intent = "full_text_search"
    return get_full_text_search_response(query_text)
    
def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupera un prodotto per ID.
    
    Args:
        product_id: ID del prodotto
        
    Returns:
        Dizionario con i dati del prodotto o None se non trovato
    """
    try:
        with get_db() as db:
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return None
                
            return {
                'id': product.id,
                'title': product.title, 
                'description': product.description,
                'price': product.price,
                'sale_price': product.sale_price,
                'brand': product.brand,
                'color': product.color,
                'material': product.material,
                'availability': product.availability,
                'link': product.link,
                'image_link': product.image_link,
                'category': product.product_type or product.google_product_category
            }
    except Exception as e:
        logger.error(f"Errore nel recupero del prodotto {product_id}: {str(e)}")
        return None

def get_products_by_category(category: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Recupera prodotti per categoria.
    
    Args:
        category: Nome della categoria
        limit: Numero massimo di risultati
        
    Returns:
        Lista di prodotti
    """
    try:
        with get_db() as db:
            products = db.query(Product).filter(
                or_(
                    Product.product_type.ilike(f'%{category}%'),
                    Product.google_product_category.ilike(f'%{category}%')
                )
            ).limit(limit).all()
            
            return [{
                'id': p.id,
                'title': p.title,
                'price': p.price,
                'sale_price': p.sale_price,
                'brand': p.brand,
                'availability': p.availability,
                'image_link': p.image_link,
                'category': p.product_type or p.google_product_category
            } for p in products]
    except Exception as e:
        logger.error(f"Errore nel recupero dei prodotti per categoria {category}: {str(e)}")
        return []

def get_catalog_stats() -> Dict[str, Any]:
    """
    Recupera statistiche generali sul catalogo.
    
    Returns:
        Dizionario con statistiche
    """
    try:
        with get_db() as db:
            # Conteggio prodotti
            total_products = db.query(func.count(Product.id)).scalar() or 0
            
            # Statistiche sui prezzi
            price_stats = db.query(
                func.avg(Product.price),
                func.min(Product.price),
                func.max(Product.price)
            ).first()
            
            # Conta marche uniche
            unique_brands = db.query(func.count(func.distinct(Product.brand))).scalar() or 0
            
            # Conta categorie uniche
            unique_categories = db.query(func.count(func.distinct(Product.product_type))).scalar() or 0
            
            # Importazioni recenti
            recent_imports = db.query(CatalogSync).filter(
                CatalogSync.success == True
            ).order_by(desc(CatalogSync.completed_at)).limit(5).all()
            
            # Top marche
            top_brands = [r[0] for r in db.query(
                Product.brand, 
                func.count(Product.id).label('count')
            ).group_by(Product.brand).order_by(desc('count')).limit(5).all() if r[0]]
            
            return {
                'total_products': total_products,
                'price_stats': {
                    'average': round(price_stats[0] or 0, 2),
                    'minimum': price_stats[1] or 0,
                    'maximum': price_stats[2] or 0
                },
                'unique_brands': unique_brands,
                'unique_categories': unique_categories,
                'top_brands': top_brands,
                'recent_imports': [{
                    'date': imp.completed_at.strftime('%Y-%m-%d %H:%M') if imp.completed_at else 'N/A',
                    'products': imp.products_total,
                    'added': imp.products_added,
                    'updated': imp.products_updated
                } for imp in recent_imports]
            }
    except Exception as e:
        logger.error(f"Errore nel recupero delle statistiche del catalogo: {str(e)}")
        return {
            'total_products': 0,
            'price_stats': {
                'average': 0,
                'minimum': 0,
                'maximum': 0
            },
            'unique_brands': 0,
            'unique_categories': 0
        }

# Funzioni di risposta per vari tipi di query

def get_product_info_response(product_id: str) -> Dict[str, Any]:
    """
    Risposta per query su prodotto specifico.
    
    Args:
        product_id: ID del prodotto
        
    Returns:
        Dizionario con risultato della query
    """
    product = get_product_by_id(product_id)
    
    return {
        'success': product is not None,
        'intent': 'product_info',
        'result_type': 'product',
        'product': product
    }

def get_products_by_category_response(category: str) -> Dict[str, Any]:
    """
    Risposta per query su categoria.
    
    Args:
        category: Nome della categoria
        
    Returns:
        Dizionario con risultato della query
    """
    products = get_products_by_category(category)
    
    return {
        'success': len(products) > 0,
        'intent': 'product_category',
        'result_type': 'products',
        'category': category,
        'products': products
    }

def get_products_by_price_response(min_price: float = None, max_price: float = None, limit: int = 10) -> Dict[str, Any]:
    """
    Risposta per query su prezzo.
    
    Args:
        min_price: Prezzo minimo
        max_price: Prezzo massimo
        limit: Numero massimo di risultati
        
    Returns:
        Dizionario con risultato della query
    """
    try:
        with get_db() as db:
            query = db.query(Product)
            
            if min_price is not None:
                query = query.filter(Product.price >= min_price)
                
            if max_price is not None:
                query = query.filter(Product.price <= max_price)
                
            products = query.limit(limit).all()
            
            product_list = [{
                'id': p.id,
                'title': p.title,
                'price': p.price,
                'sale_price': p.sale_price,
                'brand': p.brand,
                'availability': p.availability,
                'image_link': p.image_link
            } for p in products]
            
            return {
                'success': len(product_list) > 0,
                'intent': 'product_price',
                'result_type': 'products',
                'min_price': min_price,
                'max_price': max_price,
                'products': product_list
            }
    except Exception as e:
        logger.error(f"Errore nella ricerca per prezzo: {str(e)}")
        return {
            'success': False,
            'intent': 'product_price',
            'result_type': 'products',
            'error': str(e),
            'products': []
        }

def get_catalog_stats_response() -> Dict[str, Any]:
    """
    Risposta per query su statistiche del catalogo.
    
    Returns:
        Dizionario con risultato della query
    """
    stats = get_catalog_stats()
    
    return {
        'success': True,
        'intent': 'stats',
        'result_type': 'stats',
        'stats': stats
    }

def get_recent_changes_response() -> Dict[str, Any]:
    """
    Risposta per query su modifiche recenti.
    
    Returns:
        Dizionario con risultato della query
    """
    try:
        with get_db() as db:
            # Trova le modifiche degli ultimi 7 giorni
            one_week_ago = datetime.now() - timedelta(days=7)
            
            # Ottiene i prodotti modificati raggruppati
            product_changes = db.query(
                ProductChange.product_id, 
                func.count(ProductChange.id).label('change_count')
            ).filter(
                ProductChange.changed_at >= one_week_ago
            ).group_by(
                ProductChange.product_id
            ).order_by(
                desc('change_count')
            ).limit(10).all()
            
            changes_list = []
            
            for product_id, _ in product_changes:
                product = db.query(Product).filter(Product.id == product_id).first()
                
                if not product:
                    continue
                
                changes = db.query(ProductChange).filter(
                    ProductChange.product_id == product_id,
                    ProductChange.changed_at >= one_week_ago
                ).order_by(
                    desc(ProductChange.changed_at)
                ).all()
                
                changes_data = [{
                    'field': c.field_name,
                    'old_value': c.old_value,
                    'new_value': c.new_value,
                    'date': c.changed_at.strftime('%Y-%m-%d %H:%M')
                } for c in changes]
                
                changes_list.append({
                    'id': product.id,
                    'title': product.title,
                    'changes': changes_data
                })
            
            return {
                'success': len(changes_list) > 0,
                'intent': 'changes',
                'result_type': 'changes',
                'changes': changes_list
            }
    except Exception as e:
        logger.error(f"Errore nel recupero delle modifiche recenti: {str(e)}")
        return {
            'success': False,
            'intent': 'changes',
            'result_type': 'changes',
            'error': str(e),
            'changes': []
        }

def get_full_text_search_response(query_text: str) -> Dict[str, Any]:
    """
    Risposta per ricerca full-text.
    
    Args:
        query_text: Testo della query
        
    Returns:
        Dizionario con risultato della query
    """
    try:
        terms = query_text.split()
        
        with get_db() as db:
            # Ricerca semplice
            query = db.query(Product)
            
            # Filtra per ogni termine
            for term in terms:
                if len(term) >= 3:  # ignora termini troppo brevi
                    query = query.filter(
                        or_(
                            Product.title.ilike(f'%{term}%'),
                            Product.description.ilike(f'%{term}%'),
                            Product.brand.ilike(f'%{term}%'),
                            Product.product_type.ilike(f'%{term}%')
                        )
                    )
            
            products = query.limit(10).all()
            
            product_list = [{
                'id': p.id,
                'title': p.title,
                'price': p.price,
                'sale_price': p.sale_price,
                'brand': p.brand,
                'availability': p.availability,
                'image_link': p.image_link
            } for p in products]
            
            return {
                'success': len(product_list) > 0,
                'intent': 'full_text_search',
                'result_type': 'products',
                'query': query_text,
                'products': product_list
            }
    except Exception as e:
        logger.error(f"Errore nella ricerca full-text: {str(e)}")
        return {
            'success': False,
            'intent': 'full_text_search',
            'result_type': 'products',
            'error': str(e),
            'products': []
        }
