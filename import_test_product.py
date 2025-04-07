#!/usr/bin/env python3
"""
Script per importare manualmente un prodotto di test nel database.
Utile se la sincronizzazione del feed non funziona correttamente.
"""
import json
import datetime
from database import DatabaseSession
from models import Product, CatalogSync

def import_test_product():
    """Importa un prodotto di test nel database."""
    print("Importazione di un prodotto di test nel database...")
    
    # Dati del prodotto MENAPPCEM (da un esempio reale)
    test_product_data = {
        "id": "MENAPPCEM",
        "brand": "Mobili Fiver",
        "title": "Appendiabiti da terra di Design, Emma, Grigio Cemento",
        "description": "L'appendiabiti da terra Emma Grigio Cemento è realizzato in nobilitato di alta qualità. È dotato di 4 braccia in grado di reggere un carico massimo di 7 Kg ciascuna.",
        "price": 94.40,
        "sale_price": 94.4,
        "availability": "in stock",
        "color": "Grigio Cemento",
        "material": "Nobilitato",
        "mpn": "0793579922421",
        "google_product_category": "Casa e giardino > Arredo > Appendiabiti e appendicappelli",
        "product_type": "APPENDIABITI > Appendiabiti Da Terra > Emma",
        "link": "https://www.mobilifiver.com/eu/it/appendiabiti-da-terra-di-design-emma-grigio-cemento/?currency=EUR",
        "mobile_link": "https://www.mobilifiver.com/eu/it/appendiabiti-da-terra-di-design-emma-grigio-cemento/?currency=EUR",
        "image_link": "https://www.mobilifiver.com/eu/media/catalog/product/M/E/MENAPPCEM_prodotto_princ_01_web_1758.jpeg_img_feed",
        "additional_image_links": "https://www.mobilifiver.com/eu/media/catalog/product/M/E/MENAPPCEM_prodotto_02_web_d114.jpeg,https://www.mobilifiver.com/eu/media/catalog/product/M/E/MENAPP_prodotto_03_web_8b86.jpeg",
        "custom_label_1": "NO",
        "custom_label_2": "NO",
        "custom_label_3": "Appendiabiti",
        "custom_label_4": "Emma",
        "item_group_id": "MENAPP"
    }
    
    # Connessione al database
    with DatabaseSession() as db:
        # Verifica se il prodotto esiste già
        existing_product = db.query(Product).filter(Product.id == test_product_data["id"]).first()
        
        if existing_product:
            print(f"Il prodotto {test_product_data['id']} esiste già nel database.")
            print("Aggiornamento dei dati...")
            
            # Aggiorna i campi
            existing_product.title = test_product_data["title"]
            existing_product.description = test_product_data["description"]
            existing_product.price = test_product_data["price"]
            existing_product.sale_price = test_product_data["sale_price"]
            existing_product.brand = test_product_data["brand"]
            existing_product.condition = "new"
            existing_product.availability = test_product_data["availability"]
            existing_product.color = test_product_data["color"]
            existing_product.material = test_product_data["material"]
            existing_product.mpn = test_product_data["mpn"]
            existing_product.google_product_category = test_product_data["google_product_category"]
            existing_product.product_type = test_product_data["product_type"]
            existing_product.link = test_product_data["link"]
            existing_product.mobile_link = test_product_data["mobile_link"]
            existing_product.image_link = test_product_data["image_link"]
            existing_product.additional_image_links = test_product_data["additional_image_links"]
            existing_product.custom_label_1 = test_product_data["custom_label_1"]
            existing_product.custom_label_2 = test_product_data["custom_label_2"]
            existing_product.custom_label_3 = test_product_data["custom_label_3"]
            existing_product.custom_label_4 = test_product_data["custom_label_4"]
            existing_product.item_group_id = test_product_data["item_group_id"]
            existing_product.updated_at = datetime.datetime.utcnow()
            existing_product.last_synced = datetime.datetime.utcnow()
            existing_product.raw_data = test_product_data
            
        else:
            print(f"Inserimento nuovo prodotto: {test_product_data['id']}")
            
            # Crea un nuovo prodotto
            new_product = Product(
                id=test_product_data["id"],
                title=test_product_data["title"],
                description=test_product_data["description"],
                price=test_product_data["price"],
                sale_price=test_product_data["sale_price"],
                brand=test_product_data["brand"],
                condition="new",
                availability=test_product_data["availability"],
                color=test_product_data["color"],
                material=test_product_data["material"],
                mpn=test_product_data["mpn"],
                google_product_category=test_product_data["google_product_category"],
                product_type=test_product_data["product_type"],
                link=test_product_data["link"],
                mobile_link=test_product_data["mobile_link"],
                image_link=test_product_data["image_link"],
                additional_image_links=test_product_data["additional_image_links"],
                custom_label_1=test_product_data["custom_label_1"],
                custom_label_2=test_product_data["custom_label_2"],
                custom_label_3=test_product_data["custom_label_3"],
                custom_label_4=test_product_data["custom_label_4"],
                item_group_id=test_product_data["item_group_id"],
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                last_synced=datetime.datetime.utcnow(),
                raw_data=test_product_data
            )
            db.add(new_product)
        
        # Registra un'importazione di test
        test_sync = CatalogSync(
            source_url="manual_import",
            started_at=datetime.datetime.utcnow(),
            completed_at=datetime.datetime.utcnow(),
            success=True,
            products_total=1,
            products_added=1 if not existing_product else 0,
            products_updated=1 if existing_product else 0,
            products_removed=0,
            import_version="test_manual_import"
        )
        db.add(test_sync)
        
        # Salva le modifiche
        db.commit()
        
        print("Prodotto importato/aggiornato con successo!")
        print(f"ID: {test_product_data['id']}")
        print(f"Titolo: {test_product_data['title']}")
        print(f"Prezzo: {test_product_data['price']}€")

if __name__ == "__main__":
    import_test_product()