#!/bin/bash
# Script per configurare l'ambiente per il layer AI

# Assicurati di essere nella directory del progetto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Attiva l'ambiente virtuale
source ../venv_feedwise/bin/activate

# Installa le dipendenze necessarie
pip install requests

# Verifica la configurazione
if [ ! -f "config.json" ]; then
    echo "ATTENZIONE: File config.json non trovato."
    echo "Crea un file config.json con la tua chiave API OpenAI."
    echo "Esempio:"
    echo '{
    "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
    "model": "gpt-3.5-turbo"
}'
else
    echo "Configurazione trovata."
    
    # Verifica se la chiave API è configurata
    API_KEY=$(grep -o '"openai_api_key": *"[^"]*"' config.json | cut -d '"' -f 4)
    if [ "$API_KEY" = "YOUR_OPENAI_API_KEY_HERE" ]; then
        echo "ATTENZIONE: Devi configurare la tua chiave API OpenAI in config.json"
    else
        echo "Chiave API configurata."
    fi
fi

echo ""
echo "Setup completato. Puoi avviare l'assistente AI con:"
echo "python chat.py"
echo ""
echo "O testare una query specifica con:"
echo "python chat.py --query \"Dammi informazioni sul prodotto MENAPPCEM\""

# Disattiva l'ambiente virtuale
deactivate