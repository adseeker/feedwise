#!/usr/bin/env python3
"""
Script per verificare il contenuto del database.
"""
from database import DatabaseSession
from models import Product, CatalogSync
import sys

def check_database():
    """Controlla il database e mostra informazioni sui prodotti."""
    with DatabaseSession() as db:
        # Verifica se ci sono prodotti nel database
        product_count = db.query(Product).count()
        print(f"Numero totale di prodotti nel database: {product_count}")
        
        # Verifica le importazioni
        syncs = db.query(CatalogSync).order_by(CatalogSync.id.desc()).all()
        print(f"Numero di importazioni registrate: {len(syncs)}")
        
        for sync in syncs:
            print(f"- ID: {sync.id}, Versione: {sync.import_version}, Successo: {sync.success}, Prodotti: {sync.products_total}")
        
        # Cerca il prodotto specifico
        product_id = "MENAPPCEM"
        if len(sys.argv) > 1:
            product_id = sys.argv[1]
            
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if product:
            print(f"\nProdotto {product_id} trovato:")
            print(f"- Titolo: {product.title}")
            print(f"- Prezzo: {product.price}")
            print(f"- Marca: {product.brand}")
        else:
            print(f"\nProdotto {product_id} NON trovato nel database.")
            
            # Prova una ricerca case-insensitive
            product = db.query(Product).filter(Product.id.ilike(f"%{product_id}%")).first()
            if product:
                print(f"Trovato un prodotto con ID simile: {product.id}")
            
            # Elenca i primi 5 prodotti per controllare
            print("\nEcco i primi 5 prodotti nel database:")
            products = db.query(Product).limit(5).all()
            for p in products:
                print(f"- ID: {p.id}, Titolo: {p.title}")

if __name__ == "__main__":
    check_database()