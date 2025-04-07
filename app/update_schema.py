#!/usr/bin/env python3
"""
Script per aggiornare lo schema del database esistente.
Aggiunge le nuove colonne shipping_cost e shipping_time alla tabella products.
"""
import os
import sqlite3
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_schema")

# Percorso del database
DB_PATH = "data/catalog.db"

def add_shipping_columns():
    """Aggiunge le colonne shipping_cost e shipping_time alla tabella products."""
    try:
        # Verifica che il database esista
        if not os.path.exists(DB_PATH):
            logger.error(f"Database non trovato: {DB_PATH}")
            return False
        
        # Connessione al database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Controlla se le colonne già esistono
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Aggiunge availability_date se non esiste
        if "availability_date" not in columns:
            logger.info("Aggiunta colonna availability_date...")
            cursor.execute("ALTER TABLE products ADD COLUMN availability_date TEXT")
            logger.info("Colonna availability_date aggiunta con successo")
        else:
            logger.info("La colonna availability_date esiste già")
        
        # Commit delle modifiche
        conn.commit()
        logger.info("Schema aggiornato con successo")
        
        # Non impostiamo valori predefiniti ma lasciamo i campi NULL
        # così mostriamo solo i dati reali presenti nel feed
        logger.info("Schema aggiornato senza valori predefiniti")
        
        # Chiudi la connessione
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento dello schema: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Avvio dell'aggiornamento dello schema...")
    
    if add_shipping_columns():
        logger.info("✅ Aggiornamento completato con successo!")
    else:
        logger.error("❌ Errore durante l'aggiornamento dello schema")
        exit(1)