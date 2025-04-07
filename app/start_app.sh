#!/bin/bash
# Script per avviare l'applicazione FeedWise

# Directory del progetto (da modificare con il percorso corretto)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Directory dell'ambiente virtuale
# Invece di "dirname" che prende la directory genitore, 
# usiamo direttamente il percorso all'ambiente virtuale
VENV_DIR="/Users/sviluppo/venv_feedwise"

# Vai alla directory del progetto
cd "$PROJECT_DIR"

# Crea directory per log e pid se non esistono
mkdir -p logs
mkdir -p data

# Attiva l'ambiente virtuale
source "$VENV_DIR/bin/activate"

# Avvia l'applicazione in background
echo "Avvio dell'applicazione FeedWise..."
python app.py >> logs/app_output.log 2>&1 &

# Salva il PID
echo $! > feedwise.pid
echo "Applicazione avviata con PID: $!"
echo "Per fermare l'applicazione, esegui: ./stop_app.sh"

# Disattiva l'ambiente virtuale
deactivate