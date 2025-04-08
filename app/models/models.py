"""
Modelli per il database dell'applicazione
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class Product(Base):
    """
    Modello per i prodotti del catalogo.
    Contiene i campi principali visti nel feed JSON.
    """
    __tablename__ = 'products'
    
    # Campi primari
    id = Column(String, primary_key=True)  # ID del prodotto (es. "MENAPPCEM")
    item_group_id = Column(String, index=True)  # ID del gruppo di prodotti
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float)
    sale_price = Column(Float)
    
    # Attributi prodotto
    brand = Column(String(100))
    condition = Column(String(50))
    availability = Column(String(50))
    availability_date = Column(String(50))  # Data di disponibilità per prodotti in backorder
    color = Column(String(100))
    material = Column(String(100))
    mpn = Column(String(100))  # Manufacturer Part Number
    
    # Categorie e classificazioni
    google_product_category = Column(String(255))
    product_type = Column(String(255))
    
    # URL e immagini
    link = Column(String(500))
    mobile_link = Column(String(500))
    image_link = Column(String(500))
    additional_image_links = Column(Text)  # Lista di URL separati da virgola
    
    # Dati di sistema
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced = Column(DateTime)
    
    # Etichette personalizzate
    custom_label_1 = Column(String(255))
    custom_label_2 = Column(String(255))
    custom_label_3 = Column(String(255))
    custom_label_4 = Column(String(255))
    
    # Metadati aggiuntivi
    raw_data = Column(JSON)  # Memorizza l'intero JSON grezzo per eventuali campi non mappati
    
    # Relazioni
    changes = relationship("ProductChange", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id='{self.id}', title='{self.title}')>"


class CatalogSync(Base):
    """
    Registro delle sincronizzazioni del catalogo.
    Tiene traccia di ogni importazione per monitoraggio e debug.
    """
    __tablename__ = 'catalog_syncs'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(String(500))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    success = Column(Boolean, default=False)
    products_total = Column(Integer, default=0)
    products_added = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
    products_removed = Column(Integer, default=0)
    error_message = Column(Text)
    import_version = Column(String(20), unique=True, index=True)  # es. "2025-03-31"
    
    # Relazioni
    changes = relationship("ProductChange", back_populates="sync")
    
    def __repr__(self):
        return f"<CatalogSync(id={self.id}, started_at='{self.started_at}', success={self.success})>"


class ProductChange(Base):
    """
    Registro delle modifiche ai prodotti.
    Utile per tracciare la storia delle modifiche e implementare funzionalità
    come "cosa è cambiato oggi".
    """
    __tablename__ = 'product_changes'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey('products.id'), index=True)
    sync_id = Column(Integer, ForeignKey('catalog_syncs.id'), index=True)
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni
    product = relationship("Product", back_populates="changes")
    sync = relationship("CatalogSync", back_populates="changes")
    
    def __repr__(self):
        return f"<ProductChange(product_id='{self.product_id}', field='{self.field_name}')>"
