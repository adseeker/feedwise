from database import DatabaseSession
from models import Product, CatalogSync, ProductChange

def debug_import():
    with DatabaseSession() as db:
        # Verifica ultima importazione
        last_sync = db.query(CatalogSync).order_by(CatalogSync.started_at.desc()).first()
        
        print("🔍 Dettagli ultima sincronizzazione:")
        print(f"ID: {last_sync.id}")
        print(f"URL: {last_sync.source_url}")
        print(f"Successo: {last_sync.success}")
        print(f"Totale prodotti: {last_sync.products_total}")
        print(f"Aggiunti: {last_sync.products_added}")
        print(f"Aggiornati: {last_sync.products_updated}")
        
        # Prova a leggere alcuni prodotti
        products = db.query(Product).limit(5).all()
        
        print("\n📦 Primi 5 prodotti:")
        for p in products:
            print(f"ID: {p.id}, Titolo: {p.title}, Prezzo: {p.price}")

if __name__ == "__main__":
    debug_import()