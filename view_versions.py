#!/usr/bin/env python3
"""
Script per visualizzare le versioni del feed importate e le relative statistiche.
"""
from database import DatabaseSession
from models import CatalogSync, Product, ProductChange
from datetime import datetime, timedelta
import argparse
from tabulate import tabulate  # Importa la funzione tabulate

def show_all_versions():
    """Mostra tutte le versioni importate del feed."""
    with DatabaseSession() as db:
        versions = db.query(CatalogSync).order_by(CatalogSync.started_at.desc()).all()
        
        if not versions:
            print("Nessuna importazione trovata nel database.")
            return
            
        # Prepara i dati per la tabella
        table_data = []
        for v in versions:
            completed = v.completed_at.strftime("%Y-%m-%d %H:%M") if v.completed_at else "In corso"
            duration = "-"
            if v.completed_at and v.started_at:
                duration = str(v.completed_at - v.started_at).split('.')[0]  # Rimuovi i microsecondi
                
            row = [
                v.id,
                v.import_version or "-",
                v.started_at.strftime("%Y-%m-%d %H:%M"),
                completed,
                duration,
                "✓" if v.success else "✗",
                v.products_total,
                v.products_added,
                v.products_updated,
                v.products_removed
            ]
            table_data.append(row)
            
        # Stampa la tabella
        headers = ["ID", "Versione", "Inizio", "Fine", "Durata", "Successo", 
                 "Tot Prodotti", "Aggiunti", "Aggiornati", "Rimossi"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

def compare_versions(version1, version2):
    """
    Confronta due versioni del feed e mostra le differenze.
    
    Args:
        version1: Prima versione (etichetta o ID)
        version2: Seconda versione (etichetta o ID)
    """
    with DatabaseSession() as db:
        # Cerca le versioni nel database
        sync1 = None
        sync2 = None
        
        # Prova a cercare per etichetta
        if version1:
            sync1 = db.query(CatalogSync).filter(CatalogSync.import_version == version1).first()
        if version2:
            sync2 = db.query(CatalogSync).filter(CatalogSync.import_version == version2).first()
            
        # Se non trovato, prova a cercare per ID
        if not sync1 and version1 and version1.isdigit():
            sync1 = db.query(CatalogSync).filter(CatalogSync.id == int(version1)).first()
        if not sync2 and version2 and version2.isdigit():
            sync2 = db.query(CatalogSync).filter(CatalogSync.id == int(version2)).first()
            
        # Se ancora non trovato, usa gli ultimi due sync
        if not sync1 or not sync2:
            syncs = db.query(CatalogSync).filter(CatalogSync.success == True).order_by(CatalogSync.id.desc()).limit(2).all()
            if len(syncs) < 2:
                print("Non ci sono abbastanza importazioni per fare un confronto.")
                return
            sync2 = syncs[0]  # Più recente
            sync1 = syncs[1]  # Precedente
            
        print(f"Confronto tra versioni:")
        print(f"1. {sync1.import_version or f'ID: {sync1.id}'} ({sync1.started_at.strftime('%Y-%m-%d')})")
        print(f"2. {sync2.import_version or f'ID: {sync2.id}'} ({sync2.started_at.strftime('%Y-%m-%d')})")
        print()
        
        # Trova le modifiche tra le due versioni
        changes = db.query(ProductChange).filter(
            ProductChange.sync_id == sync2.id
        ).order_by(ProductChange.product_id).all()
        
        if not changes:
            print("Nessuna modifica trovata tra queste versioni.")
            return
            
        # Raggruppa le modifiche per prodotto
        changes_by_product = {}
        for change in changes:
            if change.product_id not in changes_by_product:
                changes_by_product[change.product_id] = []
            changes_by_product[change.product_id].append(change)
            
        # Mostra le modifiche
        print(f"Modifiche trovate: {len(changes)} in {len(changes_by_product)} prodotti")
        print()
        
        for product_id, product_changes in list(changes_by_product.items())[:10]:  # Mostra primi 10 prodotti
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                print(f"Prodotto: {product.id} - {product.title}")
                
                change_data = []
                for change in product_changes:
                    change_data.append([
                        change.field_name,
                        change.old_value or "(vuoto)",
                        change.new_value or "(vuoto)"
                    ])
                
                print(tabulate(change_data, headers=["Campo", "Valore precedente", "Nuovo valore"], tablefmt="simple"))
                print()
        
        if len(changes_by_product) > 10:
            print(f"... e altri {len(changes_by_product) - 10} prodotti con modifiche")

if __name__ == "__main__":
    # Verifica che tabulate sia installato - senza reimportarlo
    # Il try/import era nella posizione sbagliata e causava il conflitto
    parser = argparse.ArgumentParser(description="Visualizza e confronta versioni del feed importate")
    parser.add_argument("--compare", "-c", action="store_true", 
                      help="Confronta due versioni del feed")
    parser.add_argument("--version1", "-v1", 
                      help="Prima versione per il confronto (etichetta o ID)")
    parser.add_argument("--version2", "-v2", 
                      help="Seconda versione per il confronto (etichetta o ID)")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_versions(args.version1, args.version2)
    else:
        show_all_versions()