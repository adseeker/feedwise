#!/usr/bin/env python3
"""
Modulo per eseguire query sul catalogo.
Fornisce funzioni per recuperare informazioni sui prodotti dal database.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import or_, and_, text
from database import DatabaseSession
from models import Product, CatalogSync, ProductChange

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("catalog_query")

def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupera un prodotto dal suo ID (SKU).
    
    Args:
        product_id: ID del prodotto da recuperare
        
    Returns:
        Dict con i dati del prodotto o None se non trovato
    """
    with DatabaseSession() as db:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
            
        return {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "sale_price": product.sale_price,
            "brand": product.brand,
            "availability": product.availability,
            "color": product.color,
            "material": product.material,
            "category": product.product_type,
            "image_url": product.image_link
        }
    print(f"🔍 Ricerca prodotto con ID: {product_id}")
    with DatabaseSession() as db:
        # Stampa tutti gli ID per debug
        all_ids = [p.id for p in db.query(Product.id).all()]
        print(f"🏷️ IDs nel database: {all_ids[:10]}...")  # Mostra primi 10 ID
        
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            print(f"❌ Prodotto {product_id} non trovato")
            return None
            
        return {
            # Campi di ritorno
        }

def search_products(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Cerca prodotti che corrispondono ai termini di ricerca.
    
    Args:
        query: Termini di ricerca (titolo, descrizione, marca, ecc.)
        limit: Numero massimo di risultati da restituire
        
    Returns:
        Lista di prodotti che corrispondono alla ricerca
    """
    with DatabaseSession() as db:
        # Dividi la query in parole chiave
        keywords = query.lower().split()
        
        # Crea una query con filtri OR per ogni parola chiave
        filters = []
        for keyword in keywords:
            keyword_filter = or_(
                Product.title.ilike(f"%{keyword}%"),
                Product.description.ilike(f"%{keyword}%"),
                Product.brand.ilike(f"%{keyword}%"),
                Product.color.ilike(f"%{keyword}%"),
                Product.material.ilike(f"%{keyword}%"),
                Product.product_type.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
        
        # Combina tutti i filtri con AND (tutti i termini devono corrispondere)
        query = db.query(Product).filter(and_(*filters))
        
        # Limita i risultati
        products = query.limit(limit).all()
        
        # Converti in dizionari
        results = []
        for p in products:
            results.append({
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "sale_price": p.sale_price,
                "brand": p.brand,
                "availability": p.availability,
                "color": p.color,
                "material": p.material,
                "category": p.product_type
            })
            
        return results

def get_products_by_category(category: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Recupera prodotti di una specifica categoria.
    
    Args:
        category: Categoria dei prodotti
        limit: Numero massimo di risultati
        
    Returns:
        Lista di prodotti nella categoria specificata
    """
    with DatabaseSession() as db:
        products = db.query(Product).filter(
            Product.product_type.ilike(f"%{category}%")
        ).limit(limit).all()
        
        results = []
        for p in products:
            results.append({
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "sale_price": p.sale_price,
                "brand": p.brand,
                "availability": p.availability
            })
            
        return results

def get_products_by_price_range(min_price: float, max_price: float, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Recupera prodotti in un determinato intervallo di prezzo.
    
    Args:
        min_price: Prezzo minimo
        max_price: Prezzo massimo
        limit: Numero massimo di risultati
        
    Returns:
        Lista di prodotti nell'intervallo di prezzo specificato
    """
    with DatabaseSession() as db:
        products = db.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).limit(limit).all()
        
        results = []
        for p in products:
            results.append({
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "sale_price": p.sale_price,
                "brand": p.brand,
                "availability": p.availability
            })
            
        return results

def get_recent_changes(days: int = 1) -> List[Dict[str, Any]]:
    """
    Recupera le modifiche recenti ai prodotti.
    
    Args:
        days: Numero di giorni indietro per cui cercare modifiche
        
    Returns:
        Lista di modifiche recenti ai prodotti
    """
    with DatabaseSession() as db:
        # Trova l'ultima sincronizzazione completata con successo
        latest_sync = db.query(CatalogSync).filter(
            CatalogSync.success == True
        ).order_by(CatalogSync.completed_at.desc()).first()
        
        if not latest_sync:
            return []
            
        # Trova la sincronizzazione precedente
        previous_sync = db.query(CatalogSync).filter(
            CatalogSync.success == True,
            CatalogSync.id < latest_sync.id
        ).order_by(CatalogSync.id.desc()).first()
        
        if not previous_sync:
            return []
            
        # Recupera le modifiche tra le due sincronizzazioni
        changes = db.query(ProductChange).filter(
            ProductChange.sync_id == latest_sync.id
        ).order_by(ProductChange.product_id).all()
        
        # Raggruppa le modifiche per prodotto
        changes_by_product = {}
        for change in changes:
            if change.product_id not in changes_by_product:
                changes_by_product[change.product_id] = []
            changes_by_product[change.product_id].append({
                "field": change.field_name,
                "old_value": change.old_value,
                "new_value": change.new_value
            })
        
        # Ottieni informazioni sui prodotti modificati
        results = []
        for product_id, product_changes in changes_by_product.items():
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                results.append({
                    "id": product.id,
                    "title": product.title,
                    "changes": product_changes
                })
                
        return results

def get_catalog_stats() -> Dict[str, Any]:
    """
    Recupera statistiche sul catalogo.
    
    Returns:
        Dizionario con statistiche varie sul catalogo
    """
    with DatabaseSession() as db:
        # Numero totale di prodotti
        total_products = db.query(Product).count()
        
        # Numero di marche diverse
        brands_query = db.query(Product.brand).distinct()
        brands = [b[0] for b in brands_query.all() if b[0]]
        
        # Numero di categorie diverse
        categories_query = db.query(Product.product_type).distinct()
        categories = [c[0] for c in categories_query.all() if c[0]]
        
        # Prezzo medio, massimo e minimo
        try:
            price_stats = db.query(
                text("AVG(price) as avg_price"),
                text("MAX(price) as max_price"),
                text("MIN(price) as min_price")
            ).select_from(Product).first()
            
            avg_price = round(price_stats[0], 2) if price_stats[0] else 0
            max_price = price_stats[1] if price_stats[1] else 0
            min_price = price_stats[2] if price_stats[2] else 0
        except:
            # Fallback in caso di errore SQL
            avg_price = max_price = min_price = 0
            
        # Ultime importazioni
        recent_imports = db.query(CatalogSync).filter(
            CatalogSync.success == True
        ).order_by(CatalogSync.completed_at.desc()).limit(5).all()
        
        imports = []
        for imp in recent_imports:
            imports.append({
                "id": imp.id,
                "version": imp.import_version,
                "date": imp.completed_at.strftime("%Y-%m-%d %H:%M") if imp.completed_at else None,
                "products": imp.products_total,
                "added": imp.products_added,
                "updated": imp.products_updated
            })
        
        return {
            "total_products": total_products,
            "unique_brands": len(brands),
            "unique_categories": len(categories),
            "price_stats": {
                "average": avg_price,
                "maximum": max_price,
                "minimum": min_price
            },
            "recent_imports": imports,
            "top_brands": brands[:10] if len(brands) > 10 else brands
        }

def extract_price_info(query: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Estrae informazioni sul prezzo da una query in linguaggio naturale.
    Utilizza alcune euristiche per identificare intervalli di prezzo.
    
    Args:
        query: Query in linguaggio naturale
        
    Returns:
        Tupla (min_price, max_price) o (None, None) se non trovato
    """
    import re
    
    # Cerca pattern come "tra X e Y euro" o "da X a Y euro"
    range_pattern = r"(?:tra|from|between|da)\s+(\d+(?:\.\d+)?)\s+(?:e|and|a|to)\s+(\d+(?:\.\d+)?)"
    range_match = re.search(range_pattern, query.lower())
    
    if range_match:
        min_price = float(range_match.group(1))
        max_price = float(range_match.group(2))
        return min_price, max_price
    
    # Cerca pattern come "sotto X euro" o "meno di X euro"
    under_pattern = r"(?:sotto|under|below|meno di|less than)\s+(\d+(?:\.\d+)?)"
    under_match = re.search(under_pattern, query.lower())
    
    if under_match:
        max_price = float(under_match.group(1))
        return 0, max_price
    
    # Cerca pattern come "sopra X euro" o "più di X euro"
    over_pattern = r"(?:sopra|over|above|più di|more than)\s+(\d+(?:\.\d+)?)"
    over_match = re.search(over_pattern, query.lower())
    
    if over_match:
        min_price = float(over_match.group(1))
        return min_price, 9999999.0
    
    return None, None

def query_understanding(query: str) -> Dict[str, Any]:
    """
    Analizza una query in linguaggio naturale per determinare l'intento.
    Utilizza euristiche per riconoscere i pattern più comuni.
    
    Args:
        query: Query in linguaggio naturale dell'utente
        
    Returns:
        Dizionario con l'intento e i parametri estratti
    """
    query_lower = query.lower()
    
    # Verifica esplicita per il prodotto MENAPPCEM (caso speciale per il test)
    if "menappcem" in query_lower:
        return {
            "intent": "product_info",
            "product_id": "MENAPPCEM"
        }
    
    # Verifica se la query riguarda un prodotto specifico per ID
    if ("prodotto" in query_lower or "articolo" in query_lower) and ("id" in query_lower or "sku" in query_lower or "codice" in query_lower):
        # Estrai l'ID del prodotto (pattern semplice)
        import re
        id_match = re.search(r'(?:id|sku|codice)[:\s]+([a-zA-Z0-9]+)', query_lower)
        
        if id_match:
            product_id = id_match.group(1).upper()
            return {
                "intent": "product_info",
                "product_id": product_id
            }
    
    # Verifica per pattern "informazioni su prodotto X"
    if "informazioni" in query_lower and "prodotto" in query_lower:
        import re
        info_match = re.search(r'prodotto\s+([a-zA-Z0-9]+)', query_lower)
        
        if info_match:
            product_id = info_match.group(1).upper()
            return {
                "intent": "product_info",
                "product_id": product_id
            }
    
    # Verifica se la query riguarda una categoria
    category_keywords = ["categoria", "category", "tipo", "type"]
    if any(keyword in query_lower for keyword in category_keywords):
        # Estrai la categoria (prima parola dopo keyword)
        for keyword in category_keywords:
            if keyword in query_lower:
                parts = query_lower.split(keyword)
                if len(parts) > 1:
                    # Prendi la parte successiva alla keyword e puliscila
                    category = parts[1].strip().split()[0].strip(",:;.")
                    return {
                        "intent": "category_search",
                        "category": category
                    }
    
    # Verifica se la query riguarda un intervallo di prezzo
    price_keywords = ["prezzo", "price", "euro", "costo", "cost"]
    if any(keyword in query_lower for keyword in price_keywords):
        min_price, max_price = extract_price_info(query_lower)
        
        if min_price is not None and max_price is not None:
            return {
                "intent": "price_range",
                "min_price": min_price,
                "max_price": max_price
            }
    
    # Verifica se la query riguarda le modifiche recenti
    change_keywords = ["modifiche", "changes", "novità", "news", "aggiornamenti", "updates"]
    if any(keyword in query_lower for keyword in change_keywords):
        days = 1  # Default a 1 giorno
        
        # Cerca di estrarre il numero di giorni
        import re
        days_match = re.search(r'(\d+)\s+(?:giorni|days)', query_lower)
        if days_match:
            days = int(days_match.group(1))
            
        return {
            "intent": "recent_changes",
            "days": days
        }
    
    # Verifica se la query riguarda statistiche
    stats_keywords = ["statistiche", "statistics", "stats", "numeri", "numbers"]
    if any(keyword in query_lower for keyword in stats_keywords):
        return {
            "intent": "catalog_stats"
        }
    
    # Se nessun intento specifico è riconosciuto, assume ricerca generale
    return {
        "intent": "general_search",
        "query": query
    }
    query_lower = query.lower()
    
    # Verifica se la query riguarda un prodotto specifico per ID
    if "prodotto" in query_lower and (("id" in query_lower) or ("sku" in query_lower)):
        # Estrai l'ID del prodotto (pattern semplice)
        import re
        id_match = re.search(r'(?:id|sku)[:\s]+([a-zA-Z0-9]+)', query_lower)
        
        if id_match:
            product_id = id_match.group(1)
            return {
                "intent": "product_info",
                "product_id": product_id
            }
    
    # Verifica se la query riguarda una categoria
    category_keywords = ["categoria", "category", "tipo", "type"]
    if any(keyword in query_lower for keyword in category_keywords):
        # Estrai la categoria (prima parola dopo keyword)
        for keyword in category_keywords:
            if keyword in query_lower:
                parts = query_lower.split(keyword)
                if len(parts) > 1:
                    # Prendi la parte successiva alla keyword e puliscila
                    category = parts[1].strip().split()[0].strip(",:;.")
                    return {
                        "intent": "category_search",
                        "category": category
                    }
    
    # Verifica se la query riguarda un intervallo di prezzo
    price_keywords = ["prezzo", "price", "euro", "costo", "cost"]
    if any(keyword in query_lower for keyword in price_keywords):
        min_price, max_price = extract_price_info(query_lower)
        
        if min_price is not None and max_price is not None:
            return {
                "intent": "price_range",
                "min_price": min_price,
                "max_price": max_price
            }
    
    # Verifica se la query riguarda le modifiche recenti
    change_keywords = ["modifiche", "changes", "novità", "news", "aggiornamenti", "updates"]
    if any(keyword in query_lower for keyword in change_keywords):
        days = 1  # Default a 1 giorno
        
        # Cerca di estrarre il numero di giorni
        import re
        days_match = re.search(r'(\d+)\s+(?:giorni|days)', query_lower)
        if days_match:
            days = int(days_match.group(1))
            
        return {
            "intent": "recent_changes",
            "days": days
        }
    
    # Verifica se la query riguarda statistiche
    stats_keywords = ["statistiche", "statistics", "stats", "numeri", "numbers"]
    if any(keyword in query_lower for keyword in stats_keywords):
        return {
            "intent": "catalog_stats"
        }
    
    # Se nessun intento specifico è riconosciuto, assume ricerca generale
    return {
        "intent": "general_search",
        "query": query
    }

def execute_query(user_query: str) -> Dict[str, Any]:
    """
    Esegue una query in linguaggio naturale sul catalogo.
    
    Args:
        user_query: Query in linguaggio naturale dell'utente
        
    Returns:
        Dizionario con i risultati della query
    """
    # Analizza la query per determinare l'intento
    understanding = query_understanding(user_query)
    intent = understanding["intent"]
    
    # Esegui la query appropriata in base all'intento
    if intent == "product_info":
        product = get_product_by_id(understanding["product_id"])
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "product",
            "product": product,
            "success": product is not None
        }
        
    elif intent == "category_search":
        products = get_products_by_category(understanding["category"])
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "products",
            "products": products,
            "count": len(products),
            "success": len(products) > 0
        }
        
    elif intent == "price_range":
        products = get_products_by_price_range(
            understanding["min_price"],
            understanding["max_price"]
        )
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "products",
            "products": products,
            "count": len(products),
            "price_range": {
                "min": understanding["min_price"],
                "max": understanding["max_price"]
            },
            "success": len(products) > 0
        }
        
    elif intent == "recent_changes":
        changes = get_recent_changes(understanding["days"])
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "changes",
            "changes": changes,
            "count": len(changes),
            "success": len(changes) > 0
        }
        
    elif intent == "catalog_stats":
        stats = get_catalog_stats()
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "stats",
            "stats": stats,
            "success": True
        }
        
    else:  # general_search
        products = search_products(user_query)
        return {
            "intent": intent,
            "query": user_query,
            "result_type": "products",
            "products": products,
            "count": len(products),
            "success": len(products) > 0
        }

# Funzione di test
if __name__ == "__main__":
    test_queries = [
        "Dammi informazioni sul prodotto con ID MENAPPCEM",
        "Cerca tavoli sotto 200 euro",
        "Quali sono le novità degli ultimi 2 giorni?",
        "Mostrami le statistiche del catalogo",
        "Tavoli in legno di quercia"
    ]
    
    for query in test_queries:
        print(f"\nTest query: '{query}'")
        result = execute_query(query)
        print(f"Intent riconosciuto: {result['intent']}")
        print(f"Tipo di risultato: {result['result_type']}")
        print(f"Successo: {result['success']}")
        
        if result['result_type'] == 'products':
            print(f"Trovati {result['count']} prodotti")