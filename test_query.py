#!/usr/bin/env python3
"""
Script per testare le funzioni di query sul catalogo.
"""
from catalog_query import get_product_by_id, search_products
import sys

def test_get_product():
    """Testa la funzione get_product_by_id."""
    product_id = "MENAPPCEM"
    if len(sys.argv) > 1:
        product_id = sys.argv[1]
    
    print(f"Cercando prodotto con ID: {product_id}")
    product = get_product_by_id(product_id)
    
    if product:
        print("Prodotto trovato:")
        for key, value in product.items():
            print(f"- {key}: {value}")
    else:
        print(f"Prodotto {product_id} non trovato.")
        
        # Prova una ricerca più ampia
        print("\nEseguendo una ricerca generale...")
        results = search_products(product_id)
        
        if results:
            print(f"Trovati {len(results)} prodotti simili:")
            for r in results:
                print(f"- ID: {r['id']}, Titolo: {r['title']}")
        else:
            print("Nessun risultato trovato.")

if __name__ == "__main__":
    test_get_product()