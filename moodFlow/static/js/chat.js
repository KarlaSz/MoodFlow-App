// Funkcja obsługująca naciśnięcie Enter w polu tekstowym
    document.addEventListener('DOMContentLoaded', function() {
        // Zakładam, że form.prompt generuje pole input lub textarea
        const promptField = document.querySelector('#id_prompt');

        if (promptField) {
            promptField.addEventListener('keydown', function(event) {
                // Sprawdź czy naciśnięto Enter bez Shift (Shift+Enter dla nowej linii)
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault(); // Zapobiega domyślnej akcji (dodania nowej linii)
                    document.getElementById('chatForm').submit(); // Wysyła formularz
                }
            });
        }
    });