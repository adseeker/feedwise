from database import DatabaseSession
from models import Product, CatalogSync, ProductChange

def check_database():
    with DatabaseSession() as db:
        # Conta prodotti
        product_count = db.query(Product).count()
        print(f"🏷️ Totale prodotti: {product_count}")
        
        # Ultima sincronizzazione
        last_sync = db.query(CatalogSync).order_by(CatalogSync.started_at.desc()).first()
        
        if last_sync:
            print(f"\n📊 Ultima sincronizzazione:")
            print(f"  ID: {last_sync.id}")
            print(f"  URL Sorgente: {last_sync.source_url}")
            print(f"  Avviata il: {last_sync.started_at}")
            print(f"  Completata il: {last_sync.completed_at}")
            print(f"  Successo: {last_sync.success}")
            print(f"  Totale prodotti: {last_sync.products_total}")
            print(f"  Aggiunti: {last_sync.products_added}")
            print(f"  Aggiornati: {last_sync.products_updated}")
            print(f"  Rimossi: {last_sync.products_removed}")
            
            if not last_sync.success:
                print(f"  Errore: {last_sync.error_message}")

if __name__ == "__main__":
    check_database()