#!/usr/bin/env python3
"""
Interfaccia a riga di comando per interagire con l'assistente AI del catalogo.
"""
import os
import argparse
from typing import List, Dict
from ai_assistant import handle_conversation, generate_ai_response, get_catalog_context
from catalog_query import get_catalog_stats

def clear_screen():
    """Pulisce lo schermo del terminale."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    """Stampa il messaggio di benvenuto."""
    clear_screen()
    print("=" * 80)
    print("                   FeedWise AI - Assistente Catalogo                   ")
    print("=" * 80)
    print("Benvenuto! Sono l'assistente AI per il catalogo di Mobili Fiver.")
    print("Puoi chiedermi informazioni su prodotti, categorie, prezzi e novità.")
    print()
    print("Esempi di domande:")
    print("- Dammi informazioni sul prodotto MENAPPCEM")
    print("- Mostrami i tavoli disponibili")
    print("- Quali prodotti sono sotto i 100 euro?")
    print("- Ci sono state modifiche recenti al catalogo?")
    print("- Dammi le statistiche del catalogo")
    print()
    print("Digita 'exit', 'quit' o 'q' per uscire.")
    print("=" * 80)
    print()

def run_chat_interface():
    """Esegue l'interfaccia di chat interattiva."""
    print_welcome()
    
    # Inizializza la cronologia della conversazione
    conversation_history: List[Dict[str, str]] = []
    
    # Aggiungi il contesto del catalogo
    catalog_context = get_catalog_context()
    
    # Messaggio di benvenuto dall'assistente
    stats = get_catalog_stats()
    welcome_message = f"""Ciao! Sono l'assistente AI di FeedWise, esperto del catalogo Mobili Fiver.
Posso aiutarti a trovare informazioni sui {stats['total_products']} prodotti disponibili, 
con prezzi da {stats['price_stats']['minimum']}€ a {stats['price_stats']['maximum']}€.

Come posso aiutarti oggi?"""
    
    print("Assistente: " + welcome_message)
    conversation_history.append({"role": "assistant", "content": welcome_message})
    
    while True:
        # Input utente
        user_input = input("\nTu: ")
        
        # Verifica se l'utente vuole uscire
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\nAssistente: Grazie per aver utilizzato FeedWise AI. A presto!")
            break
        
        # Aggiungi l'input dell'utente alla cronologia
        conversation_history.append({"role": "user", "content": user_input})
        
        # Ottieni la risposta dell'assistente
        print("\nElaborazione in corso...")
        
        response = handle_conversation(conversation_history, user_input)
        
        # Aggiungi la risposta alla cronologia
        conversation_history.append({"role": "assistant", "content": response})
        
        # Mostra la risposta
        print("\nAssistente: " + response)
        
        # Limita la dimensione della cronologia per evitare di superare i limiti del contesto
        if len(conversation_history) > 10:
            # Mantieni il primo messaggio (contesto) e gli ultimi 9 messaggi
            conversation_history = [conversation_history[0]] + conversation_history[-9:]

def run_simple_query(query: str):
    """
    Esegue una singola query senza mantenere la conversazione.
    
    Args:
        query: Query dell'utente
    """
    print(f"Query: {query}")
    print("\nElaborazione in corso...")
    
    response = generate_ai_response(query)
    print("\nRisposta:")
    print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FeedWise AI - Assistente Catalogo")
    parser.add_argument("--query", "-q", help="Esegui una singola query senza interfaccia interattiva")
    
    args = parser.parse_args()
    
    if args.query:
        run_simple_query(args.query)
    else:
        run_chat_interface()