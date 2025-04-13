document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const promptField = document.getElementById('prompt');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const chatMessages = document.getElementById('chat-messages');
    const conversationHistory = document.getElementById('conversation_history');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    // --- KLUCZOWA ZMIANA: Konfiguracja marked ---
    // Sprawdź, czy biblioteka marked jest załadowana
    if (typeof marked === 'undefined') {
        console.error('Biblioteka marked.js nie została załadowana!');
        // Możesz tu dodać obsługę błędu, np. wyświetlić komunikat użytkownikowi
        // i zablokować dalsze działanie czatu.
        if (errorContainer) {
             errorContainer.classList.remove('d-none');
             errorMessage.textContent = 'Błąd ładowania komponentu czatu. Odśwież stronę.';
        }
        // Zablokuj formularz, jeśli marked się nie załadował
        if(promptField) promptField.disabled = true;
        if(submitBtn) submitBtn.disabled = true;

    } else {
        // Konfiguruj marked, aby traktował pojedyncze nowe linie jako <br>
        // i włącz opcje GitHub Flavored Markdown (lepsze listy, etc.)
        marked.setOptions({
            breaks: true,  // To jest kluczowe dla \n -> <br>
            gfm: true      // Dobra praktyka dla list, etc.
        });
    }
    // --- KONIEC KLUCZOWEJ ZMIANY ---


    // Funkcja do dodawania wiadomości do chatu
    function addMessage(role, content) {
        // Upewnij się, że marked istnieje przed próbą użycia
        if (typeof marked === 'undefined') return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `alert bg-${role === 'user' ? 'success' : 'dark'}`;

        // Tworzymy wrapper dla treści, któremu nadamy klasę CSS
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'chat-text'; // Nadajemy klasę dla stylów CSS

        // Dodajemy etykietę roli
        const strong = document.createElement('strong');
        strong.textContent = role === 'user' ? 'Ty:' : 'ChatGPT:';
        contentWrapper.appendChild(strong);
        contentWrapper.appendChild(document.createElement('br')); // Dodajemy <br> po etykiecie

        // Parsujemy Markdown na HTML za pomocą skonfigurowanego marked
        // Nie potrzebujemy już 'fixedMarkdown', bo opcja 'breaks: true' zajmie się \n
        const htmlContent = marked.parse(content || ''); // Używamy marked.parse() i upewniamy się, że content nie jest null/undefined

        // Bezpieczniejsze dodanie HTML - tworzymy tymczasowy element
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent;

        // Dodajemy sparsowaną treść (węzeł po węźle, aby uniknąć problemów z zagnieżdżeniem <p> w <p>)
        // lub po prostu dodajemy całe wygenerowane HTML, jeśli jest proste
        contentWrapper.innerHTML += htmlContent; // Prostsze podejście, powinno działać dla większości przypadków


        messageDiv.appendChild(contentWrapper);
        chatMessages.appendChild(messageDiv);

        // Przewijanie do najnowszej wiadomości
        chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
    }

    // Obsługa Enter w polu tekstowym (bez zmian)
    promptField.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            // Sprawdź czy marked istnieje przed wysłaniem
            if (typeof marked !== 'undefined') {
                 submitMessage();
            }
        }
    });

    // Obsługa przycisku submit (bez zmian)
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        // Sprawdź czy marked istnieje przed wysłaniem
        if (typeof marked !== 'undefined') {
             submitMessage();
        }
    });

    // Funkcja wysyłająca wiadomość AJAX (bez zmian w logice fetch)
    function submitMessage() {
        const userMessage = promptField.value.trim();

        if (userMessage === '') {
            return;
        }

        loadingSpinner.classList.remove('d-none');
        promptField.disabled = true;
        submitBtn.disabled = true;

        addMessage('user', userMessage); // Wiadomość użytkownika nie wymaga parsowania Markdown

        const formData = new FormData();
        formData.append('prompt', userMessage);
        formData.append('conversation_history', conversationHistory.value);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                 // Spróbuj odczytać treść błędu, jeśli serwer ją zwrócił
                 return response.text().then(text => {
                     throw new Error(`Błąd serwera: ${response.status} - ${text || 'Brak szczegółów'}`);
                 });
            }
            return response.json();
        })
        .then(data => {
            console.log('Response from server: ', data.assistant_response);

            conversationHistory.value = data.conversation_history;

            // Dodajemy odpowiedź asystenta, zostanie sparsowana przez addMessage
            addMessage('assistant', data.assistant_response);

            errorContainer.classList.add('d-none');
        })
        .catch(error => {
            console.error('Fetch Error:', error); // Logowanie błędu do konsoli
            errorContainer.classList.remove('d-none');
            errorMessage.textContent = 'Wystąpił błąd: ' + error.message;
        })
        .finally(() => {
            loadingSpinner.classList.add('d-none');
            promptField.disabled = false;
            submitBtn.disabled = false;
            promptField.value = '';
            promptField.focus();
        });
    }

    // Ustawiamy focus na pole tekstowe (bez zmian)
    promptField.focus();
});