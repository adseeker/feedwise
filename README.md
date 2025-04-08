# FeedWise

FeedWise è un'applicazione per la gestione e il monitoraggio di feed di prodotti. Permette di importare, visualizzare e analizzare cataloghi di prodotti da fonti esterne.

## Caratteristiche

- Dashboard per il monitoraggio dell'attività
- Importazione automatica e manuale di feed JSON
- Visualizzazione catalogo prodotti
- Tracciamento delle modifiche ai prodotti
- Assistente AI per ricerche sul catalogo

## Struttura del Progetto

L'applicazione è organizzata secondo una struttura modulare:

```
feedwise/
├── app/
│   ├── __init__.py         # Inizializzazione dell'app Flask
│   ├── config.py           # Configurazioni dell'applicazione
│   ├── routes/             # Rotte dell'applicazione
│   │   ├── main.py         # Rotte per le pagine web
│   │   └── api.py          # Endpoint API
│   ├── models/             # Modelli del database
│   │   ├── database.py     # Configurazione del database SQLAlchemy
│   │   └── models.py       # Definizione dei modelli
│   ├── services/           # Servizi e logica di business
│   │   ├── catalog_importer.py  # Importazione dei feed
│   │   ├── catalog_query.py     # Query sul catalogo
│   │   ├── ai_assistant.py      # Assistente AI
│   │   └── scheduler.py         # Scheduler per importazioni automatiche
│   ├── utils/              # Funzioni di utilità
│   ├── static/             # File statici (CSS, JS, immagini)
│   └── templates/          # Template HTML
├── data/                   # Database e file dati
├── logs/                   # Log dell'applicazione
├── tests/                  # Test dell'applicazione
└── run.py                  # Script per avviare l'applicazione
```

## Requisiti

- Python 3.9+
- Flask
- SQLAlchemy
- Requests
- APScheduler
- (Opzionale) API key OpenAI per l'assistente AI

## Installazione

1. Clona il repository:
   ```
   git clone https://github.com/tuonome/feedwise.git
   cd feedwise
   ```

2. Crea e attiva un ambiente virtuale:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

4. Configura le variabili d'ambiente (opzionale):
   ```
   export FLASK_ENV=development
   export OPENAI_API_KEY=your_api_key  # Per l'assistente AI
   ```

5. Avvia l'applicazione:
   ```
   python run.py
   ```

6. Apri il browser all'indirizzo [http://localhost:8080](http://localhost:8080)

## Utilizzo

### Importazione di un feed

1. Dalla dashboard, clicca su "Nuova Importazione"
2. Specifica l'URL del feed JSON o carica un file locale
3. Opzionalmente, aggiungi un'etichetta di versione

### Utilizzo dell'assistente AI

1. Vai alla pagina "Chat AI"
2. Fai domande sul catalogo in linguaggio naturale
3. L'assistente ti fornirà informazioni basate sui dati presenti nel catalogo

## Configurazione

Le principali opzioni di configurazione si trovano nel file `app/config.py`. Qui puoi modificare:

- Percorso del database
- URL predefinito del feed
- Programmazione delle importazioni automatiche
- Altre impostazioni dell'applicazione

## Licenza

Questo progetto è distribuito con licenza MIT.

## Contribuire

1. Fai un fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/nome-feature`)
3. Fai commit delle tue modifiche (`git commit -am 'Aggiunta funzionalità'`)
4. Fai il push sul branch (`git push origin feature/nome-feature`)
5. Crea una Pull Request
