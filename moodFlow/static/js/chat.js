// // Funkcja obsługująca naciśnięcie Enter w polu tekstowym
//     document.addEventListener('DOMContentLoaded', function() {
//         // Zakładam, że form.prompt generuje pole input lub textarea
//         const promptField = document.querySelector('#id_prompt');
//
//         if (promptField) {
//             promptField.addEventListener('keydown', function(event) {
//                 // Sprawdź czy naciśnięto Enter bez Shift (Shift+Enter dla nowej linii)
//                 if (event.key === 'Enter' && !event.shiftKey) {
//                     event.preventDefault(); // Zapobiega domyślnej akcji (dodania nowej linii)
//                     document.getElementById('chatForm').submit(); // Wysyła formularz
//                 }
//             });
//         }
//     });

document.addEventListener('DOMContentLoaded', function() {
        const chatForm = document.getElementById('chatForm');
        const promptField = document.getElementById('prompt');
        const submitBtn = document.getElementById('submitBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const chatMessages = document.getElementById('chat-messages');
        const conversationHistory = document.getElementById('conversation_history');
        const errorContainer = document.getElementById('error-container');
        const errorMessage = document.getElementById('error-message');

        // Funkcja do dodawania wiadomości do chatu
        function addMessage(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `alert bg-${role === 'user' ? 'success' : 'dark'}`;

            const paragraph = document.createElement('p');
            const strong = document.createElement('strong');
            strong.textContent = role === 'user' ? 'Ty:' : 'ChatGPT:';

            paragraph.appendChild(strong);
            paragraph.appendChild(document.createTextNode(' ' + content));

            messageDiv.appendChild(paragraph);
            chatMessages.appendChild(messageDiv);

            // Przewijanie do najnowszej wiadomości
            chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });

        }

        // Obsługa Enter w polu tekstowym
        promptField.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                submitMessage();
            }
        });

        // Obsługa przycisku submit
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            submitMessage();
        });

        // Funkcja wysyłająca wiadomość AJAX
        function submitMessage() {
            const userMessage = promptField.value.trim();

            // Sprawdzamy czy pole nie jest puste
            if (userMessage === '') {
                return;
            }

            // Pokazujemy spinner ładowania
            loadingSpinner.classList.remove('d-none');

            // Blokujemy przycisk i pole tekstowe na czas ładowania
            promptField.disabled = true;
            submitBtn.disabled = true;

            // Dodajemy wiadomość użytkownika do interfejsu
            addMessage('user', userMessage);

            // Przygotowujemy dane do wysłania
            const formData = new FormData();
            formData.append('prompt', userMessage);
            formData.append('conversation_history', conversationHistory.value);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            // Wysyłamy zapytanie AJAX
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // Aby Django rozpoznało AJAX
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Błąd serwera: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                // Aktualizujemy historię konwersacji
                conversationHistory.value = data.conversation_history;

                // Dodajemy odpowiedź asystenta
                addMessage('assistant', data.assistant_response);

                // Ukrywamy błędy jeśli były
                errorContainer.classList.add('d-none');
            })
            .catch(error => {
                // Wyświetlamy komunikat o błędzie
                errorContainer.classList.remove('d-none');
                errorMessage.textContent = 'Wystąpił błąd: ' + error.message;
            })
            .finally(() => {
                // Ukrywamy spinner i odblokowujemy kontrolki
                loadingSpinner.classList.add('d-none');
                promptField.disabled = false;
                submitBtn.disabled = false;

                // Czyszczenie pola tekstowego i focus
                promptField.value = '';
                promptField.focus();
            });
        }

        // Ustawiamy focus na pole tekstowe
        promptField.focus();
    });