# FeedWise
TEST MODIFICHE
FeedWise è un'applicazione per la gestione di cataloghi di prodotti, specializzata nell'importazione, tracciamento e interrogazione di feed di prodotti con supporto di un assistente AI.

## 🚀 Caratteristiche

- **Importazione automatica** di feed di prodotti da sorgenti JSON
- **Tracciamento modifiche** dei prodotti tra diverse versioni
- **Interrogazione intelligente** del catalogo tramite query in linguaggio naturale
- **Assistente AI integrato** per rispondere a domande sul catalogo
- **Schedulazione automatica** delle importazioni
- **Interfaccia CLI** per interagire con l'assistente

## 📋 Requisiti

- Python 3.8+
- SQLite 3
- Connessione internet per le importazioni di feed e API OpenAI

## 🛠️ Installazione

1. Clona il repository:
```bash
git clone https://github.com/yourusername/feedwise.git
cd feedwise
```

2. Crea un ambiente virtuale:
```bash
python -m venv venv
source venv/bin/activate  # su Windows: venv\Scripts\activate
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Configura l'applicazione:
```bash
# Crea un file config.json con le tue credenziali OpenAI
echo '{
  "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
  "model": "gpt-3.5-turbo"
}' > config.json
```

## 📊 Utilizzo

### Importazione del catalogo
```bash
# Importazione manuale del feed
<<<<<<< HEAD
python scheduled_import.py --url "https://repository.mobilifiver.com/public/feed/test_json/test.json"
=======
python scheduled_import.py --url "https://your-feed-url.com/feed.json"
>>>>>>> 91fe536 (Initial commit)

# Importazione di un prodotto di test
python import_test_product.py
```

### Avvio dell'assistente AI
```bash
# Avvia l'interfaccia conversazionale
python chat.py

# Esegui una query specifica
python chat.py --query "Dammi informazioni sul prodotto MENAPPCEM"
```

### Avvio dell'applicazione completa
```bash
# Avvia l'applicazione con lo scheduler
./start_app.sh

# Arresta l'applicazione
./stop_app.sh
```

### Visualizzazione delle versioni
```bash
# Visualizza tutte le versioni
python view_versions.py

# Confronta due versioni
python view_versions.py --compare --version1 "feed_2023-01-01" --version2 "feed_2023-01-02"
```

## 🧠 Interrogazione del catalogo

L'assistente AI supporta diversi tipi di query:

- **Informazioni sui prodotti**: "Dammi informazioni sul prodotto MENAPPCEM"
- **Ricerca per categoria**: "Mostrami i tavoli disponibili"
- **Ricerca per prezzo**: "Quali prodotti sono sotto i 100 euro?"
- **Modifiche recenti**: "Ci sono state modifiche recenti al catalogo?"
- **Statistiche**: "Dammi le statistiche del catalogo"

## 📂 Struttura del progetto

```
feedwise/
├── app.py                  # Punto di ingresso principale
├── app_scheduler.py        # Gestione delle operazioni programmate
├── ai_assistant.py         # Implementazione dell'assistente AI
├── catalog_importer.py     # Importazione di feed JSON
├── catalog_query.py        # Funzioni di query sul catalogo
├── chat.py                 # Interfaccia CLI per l'assistente
├── database.py             # Configurazione del database SQLite
├── models.py               # Modelli SQLAlchemy
├── scheduled_import.py     # Script per importazioni programmate
├── view_versions.py        # Visualizzazione delle versioni
├── data/                   # Directory per i dati locali
│   └── catalog.db          # Database SQLite
└── logs/                   # Log dell'applicazione
```

## 🔧 Configurazione avanzata

### Modifica della sorgente del feed

È possibile modificare l'URL del feed di prodotti nel file `app_scheduler.py`:

```python
# Configurazione del feed
FEED_URL = "https://your-feed-url.com/feed.json"
```

### Pianificazione delle importazioni

Per modificare l'orario di importazione automatica, modifica il CronTrigger in `app_scheduler.py`:

```python
scheduler.add_job(
    run_scheduled_import,
    trigger=CronTrigger(hour=6, minute=0),  # Modifica qui l'orario
    id='daily_import',
    name='Importazione giornaliera del feed',
    replace_existing=True
)
```
<<<<<<< HEAD

## 🤝 Contribuire

Le contribuzioni sono benvenute! Per favore:

1. Forka il repository
2. Crea un branch per la tua feature (`git checkout -b feature/amazing-feature`)
3. Commit delle tue modifiche (`git commit -m 'Aggiungi una feature incredibile'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è concesso in licenza con i termini della licenza MIT. Vedi il file `LICENSE` per ulteriori informazioni.

## 👏 Riconoscimenti

- Mobili Fiver per il feed di prodotti di esempio
- SQLAlchemy per l'ORM
- OpenAI per le funzionalità di AI
=======
>>>>>>> 91fe536 (Initial commit)
