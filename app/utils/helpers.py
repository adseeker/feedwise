"""
Funzioni di utilità varie per l'applicazione
"""
from datetime import datetime, timedelta, timezone

def format_time_ago(timestamp):
    """
    Formatta un timestamp come tempo relativo (es. "2 ore fa").
    
    Args:
        timestamp (datetime): Il timestamp da formattare
        
    Returns:
        str: Una stringa che rappresenta il tempo relativo
    """
    if not timestamp:
        return "Mai"
    
    # Converti il timestamp in timezone-aware se non lo è già
    if timestamp.tzinfo is None:
        # Assume UTC se non è specificata la timezone
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Ottieni l'ora corrente in UTC per corrispondere al timestamp
    now = datetime.now(timezone.utc)
    diff = now - timestamp
    
    if diff < timedelta(minutes=1):
        return "Appena ora"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} {'minuto' if minutes == 1 else 'minuti'} fa"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} {'ora' if hours == 1 else 'ore'} fa"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days} {'giorno' if days == 1 else 'giorni'} fa"
    else:
        return timestamp.strftime('%Y-%m-%d %H:%M')
