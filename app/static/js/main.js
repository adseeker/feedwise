/**
 * FeedWise - Script principale
 * Funzioni JavaScript comuni per tutte le pagine dell'applicazione
 */

// Funzione per formattare prezzi in Euro
function formatPrice(price) {
    if (price === null || price === undefined) return "-";
    return parseFloat(price).toFixed(2) + " €";
}

// Funzione per formattare date
function formatDate(dateString) {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Funzione per truncare testo lungo
function truncateText(text, maxLength = 100) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
}

// Funzione per segnalare errori API
function handleApiError(error, elementId) {
    console.error('API Error:', error);
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Errore durante il caricamento dei dati. Riprova più tardi.
            </div>
        `;
    }
}

// Definizione oggetto per colori disponibilità
const availabilityColors = {
    'in stock': 'success',
    'disponibile': 'success',
    'out of stock': 'danger',
    'non disponibile': 'danger',
    'preorder': 'warning',
    'preordine': 'warning',
    'backorder': 'info',
    'ordinabile': 'info'
};

// Formatta il badge di disponibilità
function formatAvailabilityBadge(availability) {
    if (!availability) return "";
    
    const lowerAvailability = availability.toLowerCase();
    const color = availabilityColors[lowerAvailability] || 'secondary';
    
    return `<span class="badge bg-${color}">${availability}</span>`;
}

// Inizializzazioni comuni
document.addEventListener('DOMContentLoaded', function() {
    // Evidenzia voce di menu attiva
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Inizializza tooltip di Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
