#!/usr/bin/env python3
"""
Script di debug per il catalogo e le query AI.
Verifica l'accesso al database, la struttura delle tabelle e l'esecuzione delle query.
"""
import os
import sqlite3
from database import DatabaseSession
from models import Product, CatalogSync

def check_database_file():
    """Verifica se il file del database esiste e la sua dimensione."""
    db_path = "data/catalog.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Database trovato: {db_path}")
        print(f"Dimensione: {size} bytes ({size/1024/1024:.2f} MB)")
        return True
    else:
        print(f"ERRORE: Database non trovato in {db_path}")
        return False

def check_database_tables():
    """Verifica le tabelle nel database."""
    try:
        conn = sqlite3.connect("data/catalog.db")
        cursor = conn.cursor()
        
        # Ottieni la lista delle tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tabelle trovate nel database: {len(tables)}")
        for table in tables:
            print(f"- {table[0]}")
            
            # Ottieni la struttura della tabella
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"  Colonne: {len(columns)}")
            
            # Ottieni il conteggio delle righe
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"  Righe: {count}")
            
        conn.close()
        return True
    except Exception as e:
        print(f"ERRORE nell'accesso alle tabelle: {str(e)}")
        return False

def check_sqlalchemy_access():
    """Verifica l'accesso al database tramite SQLAlchemy."""
    try:
        with DatabaseSession() as db:
            # Controlla la tabella products
            products_count = db.query(Product).count()
            print(f"SQLAlchemy - Prodotti trovati: {products_count}")
            
            if products_count > 0:
                # Mostra alcuni prodotti di esempio
                products = db.query(Product).limit(3).all()
                print("Esempi di prodotti:")
                for p in products:
                    print(f"- ID: {p.id}, Titolo: {p.title}")
            else:
                print("ATTENZIONE: Nessun prodotto trovato nel database!")
            
            # Controlla la tabella catalog_syncs
            syncs_count = db.query(CatalogSync).count()
            print(f"SQLAlchemy - Sincronizzazioni trovate: {syncs_count}")
            
            if syncs_count > 0:
                # Mostra le sincronizzazioni recenti
                syncs = db.query(CatalogSync).order_by(CatalogSync.id.desc()).limit(2).all()
                print("Sincronizzazioni recenti:")
                for s in syncs:
                    print(f"- ID: {s.id}, Versione: {s.import_version}, Successo: {s.success}")
            
        return True
    except Exception as e:
        print(f"ERRORE nell'accesso SQLAlchemy: {str(e)}")
        return False

def search_for_product(product_id="MENAPPCEM"):
    """Cerca un prodotto specifico usando SQLAlchemy e SQLite diretto."""
    # 1. Ricerca con SQLAlchemy
    print(f"\nCercando il prodotto '{product_id}'...")
    
    try:
        with DatabaseSession() as db:
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if product:
                print("SQLAlchemy - Prodotto trovato:")
                print(f"- ID: {product.id}")
                print(f"- Titolo: {product.title}")
                print(f"- Prezzo: {product.price}")
            else:
                print(f"SQLAlchemy - Prodotto '{product_id}' NON trovato.")
                
                # Prova una ricerca case-insensitive
                product = db.query(Product).filter(Product.id.ilike(f"%{product_id}%")).first()
                if product:
                    print(f"Trovato un prodotto con ID simile: {product.id}")
    except Exception as e:
        print(f"ERRORE nella ricerca SQLAlchemy: {str(e)}")
    
    # 2. Ricerca diretta con SQLite
    try:
        conn = sqlite3.connect("data/catalog.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, price FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()
        
        if result:
            print("\nSQLite - Prodotto trovato:")
            print(f"- ID: {result[0]}")
            print(f"- Titolo: {result[1]}")
            print(f"- Prezzo: {result[2]}")
        else:
            print(f"\nSQLite - Prodotto '{product_id}' NON trovato.")
            
            # Prova una ricerca case-insensitive
            cursor.execute("SELECT id, title FROM products WHERE id LIKE ?", (f"%{product_id}%",))
            similar = cursor.fetchall()
            
            if similar:
                print("Prodotti con ID simili:")
                for s in similar:
                    print(f"- {s[0]}: {s[1]}")
            
            # Mostra alcuni ID di esempio
            cursor.execute("SELECT id, title FROM products LIMIT 5")
            examples = cursor.fetchall()
            
            if examples:
                print("\nAlcuni prodotti nel database:")
                for e in examples:
                    print(f"- {e[0]}: {e[1]}")
        
        conn.close()
    except Exception as e:
        print(f"ERRORE nella ricerca SQLite: {str(e)}")

def debug_query_execution(query="MENAPPCEM"):
    """Debug dell'esecuzione della query nel modulo catalog_query."""
    from catalog_query import execute_query
    
    print(f"\nEsecuzione della query: '{query}'")
    
    try:
        result = execute_query(query)
        
        print(f"Intent riconosciuto: {result.get('intent')}")
        print(f"Tipo di risultato: {result.get('result_type')}")
        print(f"Successo: {result.get('success')}")
        
        if result.get('result_type') == 'product' and result.get('product'):
            print("\nProdotto trovato:")
            for key, value in result['product'].items():
                print(f"- {key}: {value}")
        elif result.get('result_type') == 'products' and result.get('products'):
            print(f"\nTrovati {len(result['products'])} prodotti")
            for i, p in enumerate(result['products'][:3], 1):
                print(f"{i}. {p.get('title')} (ID: {p.get('id')})")
        else:
            print("\nNessun risultato trovato o errore nella query.")
            print("Dettagli del risultato:")
            print(result)
    except Exception as e:
        print(f"ERRORE nell'esecuzione della query: {str(e)}")

if __name__ == "__main__":
    print("=== Diagnostica del catalogo e delle query AI ===\n")
    
    # Verifica il file del database
    if not check_database_file():
        print("\nIl database non esiste. Esegui l'importazione del catalogo.")
        exit(1)
    
    # Verifica le tabelle
    print("\n=== Struttura del database ===")
    check_database_tables()
    
    # Verifica l'accesso SQLAlchemy
    print("\n=== Accesso SQLAlchemy ===")
    check_sqlalchemy_access()
    
    # Cerca un prodotto specifico
    print("\n=== Ricerca prodotto specifico ===")
    search_for_product("MENAPPCEM")
    
    # Debug esecuzione query
    print("\n=== Debug esecuzione query ===")
    debug_query_execution("Dammi informazioni sul prodotto MENAPPCEM")
    
    print("\n=== Diagnostica completata ===")