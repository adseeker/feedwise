      1  # FeedWise - Documentazione del Progetto
      2  
      3  ## Panoramica del Progetto
      4  
      5  FeedWise è un'applicazione web sviluppata in Python che permette di gestire, importare e interrogare cataloghi di prodotti. Il sistema include una dashboard web, f
        unzionalità di importazione automatica di feed prodotto e un assistente AI per interrogare il catalogo in linguaggio naturale.
      6  
      7  ## Struttura del Progetto
      8  
      9  ### Componenti Principali
     10  
     11  - **Applicazione Web**: Server Flask sulla porta 8080
     12  - **Database**: SQLite con ORM SQLAlchemy
     13  - **Scheduler**: Importazioni automatiche programmate tramite APScheduler
     14  - **Assistente AI**: Integrazione con le API di OpenAI
     15  
     16  ### File Principali
     17  
     18  - `app.py`: Entry point principale dell'applicazione Flask
     19  - `app_scheduler.py`: Gestione delle importazioni automatiche programmate
     20  - `database.py`: Configurazione del database SQLite
     21  - `models.py`: Definizione dei modelli SQLAlchemy
     22  - `catalog_importer.py`: Importazione di cataloghi prodotti
     23  - `catalog_query.py`: Funzioni per interrogare il database
     24  - `ai_assistant.py`: Integrazione con OpenAI per query in linguaggio naturale
     25  
     26  ### Script di Sistema
     27  
     28  - `start_app.sh`: Avvia l'applicazione in background
     29  - `stop_app.sh`: Arresta l'applicazione
     30  - `setup_ai.sh`: Configurazione delle credenziali AI
     31  
     32  ## Struttura del Database
     33  
     34  ### Tabelle principali
     35  
     36  - **products**: Catalogo prodotti
     37    - `id`: Primary key
     38    - Campi descrittivi: title, description, price, etc.
     39    - Campi di categorizzazione: brand, product_type, google_product_category
     40    - Campi di sistema: created_at, updated_at, last_synced
     41  
     42  - **catalog_syncs**: Registro delle sincronizzazioni
     43    - Tracciamento importazioni con statistiche
     44  
     45  - **product_changes**: Registro storico delle modifiche
     46    - Storico modifiche con old_value e new_value
     47  
     48  ## Interfaccia Web
     49  
     50  - **Dashboard** (`/`): Statistiche riassuntive, cronologia importazioni
     51  - **Catalogo** (`/catalog`): Visualizzazione e ricerca prodotti
     52  - **Assistente AI** (`/chat`): Chat con assistente AI per interrogare il catalogo
     53  - **Importazione** (`/import`): Configurazione importazioni manuali e automatiche
     54  - **Impostazioni** (`/settings`): Configurazione feed e API key
     55  
     56  ## Flusso di Funzionamento
     57  
     58  1. **Importazione dati**:
     59     - Feed prodotti scaricato da URL JSON
     60     - Elaborazione e inserimento nel database
     61     - Tracciamento modifiche
     62  
     63  2. **Dashboard Web**:
     64     - Visualizzazione e ricerca catalogo
     65     - Statistiche importazioni
     66     - Interrogazione tramite assistente AI
     67  
     68  ## Comandi Utili
     69  
     70  - Avvio applicazione: `./start_app.sh`
     71  - Arresto applicazione: `./stop_app.sh`
     72  - Debug database: `python debug_database.py`
     73  - Debug catalogo: `python debug_catalog.py`
     74  
     75  ## Log delle Modifiche
     76  
     77  *Questo spazio conterrà le modifiche future che faremo al progetto*