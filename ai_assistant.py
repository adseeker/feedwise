#!/usr/bin/env python3
"""
Modulo per l'integrazione con modelli di linguaggio.
Fornisce funzionalità per interrogare il catalogo usando linguaggio naturale.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from catalog_query import execute_query, get_catalog_stats

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_assistant")

# Costanti
DEFAULT_MODEL = "gpt-3.5-turbo"  # Modello predefinito
SYSTEM_PROMPT = """
Sei un assistente AI specializzato nel catalogo prodotti di Mobili Fiver.
Il tuo compito è aiutare i clienti a trovare informazioni sui prodotti.
Basati SEMPRE sui dati forniti e non inventare informazioni.
Se non hai dati sufficienti, chiedi maggiori dettagli all'utente.

Quando descrivi i prodotti:
- Usa un tono professionale ma amichevole
- Evidenzia caratteristiche chiave come materiali e colori
- Menziona sempre il prezzo quando disponibile
- Suggerisci prodotti simili quando appropriato

Per domande sulle disponibilità o sui prezzi, usa ESCLUSIVAMENTE 
i dati forniti, senza fare supposizioni.
"""

def get_openai_api_key() -> str:
    """
    Recupera la chiave API OpenAI.
    
    Returns:
        str: Chiave API OpenAI
    """
    # Prova a recuperare dalla variabile d'ambiente
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Se non trovata, prova a leggere da un file di configurazione
    if not api_key:
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    api_key = config.get("openai_api_key")
        except:
            pass
    
    if not api_key:
        logger.warning("OpenAI API key non trovata. Imposta la variabile d'ambiente OPENAI_API_KEY.")
    
    return api_key

def query_openai(
    messages: List[Dict[str, str]], 
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Optional[str]:
    """
    Invia una richiesta all'API OpenAI.
    
    Args:
        messages: Lista di messaggi nel formato richiesto dall'API
        model: Modello da utilizzare
        temperature: Temperatura per la generazione
        max_tokens: Numero massimo di token nella risposta
        
    Returns:
        str: Risposta generata dal modello o None in caso di errore
    """
    api_key = get_openai_api_key()
    if not api_key:
        logger.error("OpenAI API key non disponibile")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result["choices"][0]["message"]["content"]
        
    except Exception as e:
        logger.error(f"Errore nella chiamata OpenAI: {str(e)}")
        return None

def format_product_info(product: Dict[str, Any]) -> str:
    """
    Formatta le informazioni di un prodotto per l'inclusione nel prompt.
    
    Args:
        product: Dizionario con i dati del prodotto
        
    Returns:
        str: Informazioni formattate
    """
    if not product:
        return "Prodotto non trovato nel catalogo."
        
    info = [
        f"ID: {product['id']}",
        f"Nome: {product['title']}",
        f"Descrizione: {product['description']}",
        f"Marca: {product['brand']}",
        f"Prezzo: {product['price']}€",
    ]
    
    if product.get('sale_price') and product['sale_price'] != product['price']:
        info.append(f"Prezzo scontato: {product['sale_price']}€")
        
    if product.get('color'):
        info.append(f"Colore: {product['color']}")
        
    if product.get('material'):
        info.append(f"Materiale: {product['material']}")
        
    if product.get('availability'):
        info.append(f"Disponibilità: {product['availability']}")
        
    if product.get('category'):
        info.append(f"Categoria: {product['category']}")
    
    return "\n".join(info)

def format_products_list(products: List[Dict[str, Any]]) -> str:
    """
    Formatta una lista di prodotti per l'inclusione nel prompt.
    
    Args:
        products: Lista di prodotti
        
    Returns:
        str: Lista formattata
    """
    if not products:
        return "Nessun prodotto trovato che corrisponde ai criteri."
        
    result = [f"Trovati {len(products)} prodotti:"]
    
    for i, product in enumerate(products, 1):
        product_info = [
            f"{i}. {product['title']} (ID: {product['id']})",
            f"   Prezzo: {product['price']}€"
        ]
        
        if product.get('sale_price') and product['sale_price'] != product['price']:
            product_info.append(f"   Prezzo scontato: {product['sale_price']}€")
            
        if product.get('brand'):
            product_info.append(f"   Marca: {product['brand']}")
            
        if product.get('availability'):
            product_info.append(f"   Disponibilità: {product['availability']}")
        
        result.append("\n".join(product_info))
    
    return "\n\n".join(result)

def format_changes(changes: List[Dict[str, Any]]) -> str:
    """
    Formatta le modifiche recenti per l'inclusione nel prompt.
    
    Args:
        changes: Lista di modifiche
        
    Returns:
        str: Modifiche formattate
    """
    if not changes:
        return "Nessuna modifica recente trovata."
        
    result = [f"Trovate modifiche recenti per {len(changes)} prodotti:"]
    
    for i, change_info in enumerate(changes, 1):
        product_changes = change_info['changes']
        
        change_text = [
            f"{i}. {change_info['title']} (ID: {change_info['id']})",
            "   Modifiche:"
        ]
        
        for change in product_changes:
            field = change['field']
            old_value = change['old_value'] or "(vuoto)"
            new_value = change['new_value'] or "(vuoto)"
            
            change_text.append(f"   - {field}: {old_value} → {new_value}")
        
        result.append("\n".join(change_text))
    
    return "\n\n".join(result)

def format_catalog_stats(stats: Dict[str, Any]) -> str:
    """
    Formatta le statistiche del catalogo per l'inclusione nel prompt.
    
    Args:
        stats: Statistiche del catalogo
        
    Returns:
        str: Statistiche formattate
    """
    info = [
        "Statistiche del catalogo:",
        f"- Numero totale di prodotti: {stats['total_products']}",
        f"- Numero di marche diverse: {stats['unique_brands']}",
        f"- Numero di categorie diverse: {stats['unique_categories']}",
        f"- Prezzo medio: {stats['price_stats']['average']}€",
        f"- Prezzo massimo: {stats['price_stats']['maximum']}€",
        f"- Prezzo minimo: {stats['price_stats']['minimum']}€",
    ]
    
    if stats.get('top_brands'):
        brands_list = ", ".join(stats['top_brands'])
        info.append(f"- Marche principali: {brands_list}")
    
    if stats.get('recent_imports'):
        imports = stats['recent_imports']
        info.append("- Importazioni recenti:")
        
        for imp in imports:
            imp_info = f"  * {imp['date']}: {imp['products']} prodotti"
            if imp['added'] > 0:
                imp_info += f", {imp['added']} aggiunti"
            if imp['updated'] > 0:
                imp_info += f", {imp['updated']} aggiornati"
            info.append(imp_info)
    
    return "\n".join(info)

def format_query_result(result: Dict[str, Any]) -> str:
    """
    Formatta il risultato di una query per l'inclusione nel prompt.
    
    Args:
        result: Risultato della query
        
    Returns:
        str: Risultato formattato
    """
    if not result.get('success', False):
        return "Non ho trovato informazioni che corrispondono alla tua richiesta nel catalogo."
    
    result_type = result.get('result_type')
    
    if result_type == 'product':
        return format_product_info(result.get('product', {}))
        
    elif result_type == 'products':
        return format_products_list(result.get('products', []))
        
    elif result_type == 'changes':
        return format_changes(result.get('changes', []))
        
    elif result_type == 'stats':
        return format_catalog_stats(result.get('stats', {}))
        
    else:
        return "Mi dispiace, non ho capito la tua richiesta."

def get_similar_products(product_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Trova prodotti simili a un prodotto dato.
    Semplice implementazione basata su categoria e prezzo simile.
    
    Args:
        product_id: ID del prodotto di riferimento
        limit: Numero massimo di prodotti simili da restituire
        
    Returns:
        Lista di prodotti simili
    """
    from catalog_query import get_product_by_id, get_products_by_category
        
    # Ottieni il prodotto di riferimento
    product = get_product_by_id(product_id)
    if not product:
        return []
    
    # Cerca prodotti nella stessa categoria
    category = product.get('category', '')
    if not category:
        return []
    
    similar_products = get_products_by_category(category, limit=10)
    
    # Filtra il prodotto stesso
    similar_products = [p for p in similar_products if p['id'] != product_id]
    
    # Ordina per similitudine di prezzo
    product_price = product.get('price', 0)
    if product_price > 0:
        for p in similar_products:
            p['price_diff'] = abs(p.get('price', 0) - product_price)
        
        similar_products.sort(key=lambda p: p.get('price_diff', 0))
    
    # Limita il numero di risultati
    return similar_products[:limit]

def generate_ai_response(user_query: str) -> str:
    """
    Genera una risposta AI basata sulla query dell'utente e sui dati del catalogo.
    
    Args:
        user_query: Query in linguaggio naturale dell'utente
        
    Returns:
        str: Risposta generata dall'AI
    """
    # Esegui la query sul catalogo
    query_result = execute_query(user_query)
    intent = query_result.get('intent')
    
    # Formatta i risultati della query
    formatted_result = format_query_result(query_result)
    
    # Arricchisci con dati aggiuntivi in base all'intento
    if intent == "product_info" and query_result.get('success', False):
        # Aggiungi prodotti simili
        product_id = query_result.get('product', {}).get('id')
        if product_id:
            similar_products = get_similar_products(product_id)
            if similar_products:
                formatted_similar = format_products_list(similar_products)
                formatted_result += "\n\nProdotti simili che potrebbero interessarti:\n" + formatted_similar
    
    # Costruisci il prompt per il modello di linguaggio
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
        {"role": "system", "content": f"Ecco le informazioni dal catalogo:\n\n{formatted_result}"}
    ]
    
    # Genera la risposta con OpenAI
    ai_response = query_openai(messages)
    
    # Se la chiamata API fallisce, restituisci direttamente i dati formattati
    if not ai_response:
        return f"Ecco le informazioni trovate nel catalogo:\n\n{formatted_result}"
    
    return ai_response

def handle_conversation(conversation_history: List[Dict[str, str]], user_query: str) -> str:
    """
    Gestisce una conversazione con l'utente, mantenendo il contesto.
    
    Args:
        conversation_history: Cronologia della conversazione
        user_query: Nuova query dell'utente
        
    Returns:
        str: Risposta generata dall'AI
    """
    # Esegui la query sul catalogo
    query_result = execute_query(user_query)
    formatted_result = format_query_result(query_result)
    
    # Costruisci i messaggi per il modello di linguaggio
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Aggiungi la cronologia della conversazione
    for message in conversation_history:
        messages.append(message)
    
    # Aggiungi la nuova query
    messages.append({"role": "user", "content": user_query})
    
    # Aggiungi i dati del catalogo come messaggio di sistema
    messages.append({"role": "system", "content": f"Ecco le informazioni dal catalogo:\n\n{formatted_result}"})
    
    # Genera la risposta con OpenAI
    ai_response = query_openai(messages)
    
    # Se la chiamata API fallisce, restituisci direttamente i dati formattati
    if not ai_response:
        return f"Ecco le informazioni trovate nel catalogo:\n\n{formatted_result}"
    
    return ai_response

def get_catalog_context() -> str:
    """
    Ottiene un contesto generale sul catalogo per fornire informazioni di base all'AI.
    
    Returns:
        str: Informazioni di contesto sul catalogo
    """
    stats = get_catalog_stats()
    formatted_stats = format_catalog_stats(stats)
    
    return f"""
Contesto del catalogo:
{formatted_stats}

Quando rispondi alle domande dell'utente, utilizza queste informazioni generali
sul catalogo insieme alle informazioni specifiche che ti fornirò per ogni domanda.
"""

# Funzione di test
if __name__ == "__main__":
    import time
    
    # Test di alcune query
    test_queries = [
        "Qual è il prezzo del prodotto MENAPPCEM?",
        "Mostrami i tavoli disponibili",
        "Quali prodotti sono sotto i 100 euro?",
        "Quali sono le novità nel catalogo?",
        "Dammi le statistiche del catalogo"
    ]
    
    for query in test_queries:
        print(f"\n\n--- Test query: '{query}' ---")
        print("Elaborazione della query...")
        
        start_time = time.time()
        response = generate_ai_response(query)
        elapsed_time = time.time() - start_time
        
        print(f"Risposta generata in {elapsed_time:.2f} secondi:")
        print(response)
        print("\n" + "-" * 80)