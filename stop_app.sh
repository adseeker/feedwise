#!/bin/bash
# Script per fermare l'applicazione FeedWise

# Directory del progetto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# File PID
PID_FILE="$PROJECT_DIR/feedwise.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # Verifica se il processo è ancora in esecuzione
    if ps -p $PID > /dev/null; then
        echo "Arresto dell'applicazione FeedWise (PID: $PID)..."
        kill $PID
        
        # Attendi che il processo termini
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            echo "Attesa terminazione processo..."
            sleep 1
        done
        
        # Se il processo è ancora attivo, forzane la chiusura
        if ps -p $PID > /dev/null; then
            echo "Forzatura chiusura processo..."
            kill -9 $PID
        fi
        
        echo "Applicazione FeedWise arrestata."
    else
        echo "Il processo con PID $PID non è in esecuzione."
    fi
    
    # Rimuovi il file PID
    rm "$PID_FILE"
else
    echo "File PID non trovato. L'applicazione potrebbe non essere in esecuzione."
fi