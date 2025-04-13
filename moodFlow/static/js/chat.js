document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const promptField = document.getElementById('prompt');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const chatMessages = document.getElementById('chat-messages');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    // Sprawdź, czy biblioteka marked jest załadowana
    if (typeof marked === 'undefined') {
        console.error('Biblioteka marked.js nie została załadowana!');
        if (errorContainer) {
             errorContainer.classList.remove('d-none');
             errorMessage.textContent = 'Błąd ładowania komponentu czatu. Odśwież stronę.';
        }
        if(promptField) promptField.disabled = true;
        if(submitBtn) submitBtn.disabled = true;
        return; // Zatrzymaj dalsze wykonywanie, jeśli marked nie działa
    } else {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // --- ZMODYFIKOWANA FUNKCJA addMessage ---
    // Dodajemy parametr timestamp
    function addMessage(role, content, timestamp) {
        if (typeof marked === 'undefined') return; // Ponowne sprawdzenie na wszelki wypadek

        const messageBubble = document.createElement('div');
        messageBubble.className = `message-bubble bg-${role === 'user' ? 'success' : 'dark'}`;

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'chat-text';

        const strong = document.createElement('strong');
        strong.textContent = role === 'user' ? 'Ty:' : 'ChatGPT:';
        contentWrapper.appendChild(strong);
        contentWrapper.appendChild(document.createElement('br'));

        // Parsowanie Markdown
        const htmlContent = marked.parse(content || '');
        // Użycie innerHTML jest tu zwykle bezpieczne dla treści z czatu,
        // ale bądź ostrożna, jeśli treść mogłaby zawierać złośliwy kod.
        // Można zastosować bibliotekę do sanityzacji HTML (np. DOMPurify), jeśli to konieczne.
        contentWrapper.innerHTML += htmlContent;

        messageBubble.appendChild(contentWrapper);

        // --- DODANIE TIMESTAMP ---
        if (timestamp) {
            const timeElement = document.createElement('small');
            // Dodaj odpowiednie klasy dla stylu (takie jak w szablonie)
            timeElement.className = 'message-timestamp text-white-50 d-block text-end mt-1';
            timeElement.textContent = timestamp; // Używamy timestampu przekazanego z backendu
            messageBubble.appendChild(timeElement);
        }
        // -------------------------

        chatMessages.appendChild(messageBubble);

        // Przewijanie do najnowszej wiadomości
        const chatContainer = document.getElementById('chat-container'); // Znajdź kontener ze scrollem
        if (chatContainer) {
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
        } else {
            // Fallback, jeśli struktura się zmieniła
            chatMessages.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }

    // Obsługa Enter w polu tekstowym
    if(promptField) {
        promptField.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                if (typeof marked !== 'undefined') {
                    submitMessage();
                }
            }
        });
    }

    // Obsługa przycisku submit
    if(chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            if (typeof marked !== 'undefined') {
                submitMessage();
            }
        });
    }

    function submitMessage() {
    const userMessageContent = promptField.value.trim();

    if (userMessageContent === '' || !promptField || !submitBtn) {
        return; // Nie wysyłaj pustych wiadomości
    }

    // --- 1. Przygotuj dane FormData ZANIM wyłączysz pole ---
    const formData = new FormData(chatForm);
    // FormData(chatForm) powinno automatycznie pobrać wartość z pola 'prompt',
    // ponieważ ma ono atrybut 'name' i NIE jest jeszcze wyłączone.

    // Opcjonalny log do sprawdzenia, czy FormData zawiera 'prompt'
    console.log("FormData created. Does it contain 'prompt'?", formData.has('prompt'));
    // Możesz też wylistować wszystkie wpisy dla pewności:
    for (let [key, value] of formData.entries()) {
        console.log(`FormData entry: ${key}=${value}`);
    }
    // --- Koniec przygotowania FormData ---


    // --- 2. Wyświetl wiadomość użytkownika i zablokuj UI ---
    const approxTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    addMessage('user', userMessageContent, approxTime); // Dodajemy od razu

    loadingSpinner.classList.remove('d-none');
    promptField.disabled = true; // Wyłącz pole DOPIERO TERAZ
    submitBtn.disabled = true;
    promptField.value = '';    // Wyczyść pole DOPIERO TERAZ


    // --- 3. Wyślij żądanie fetch ---
    fetch(window.location.href, { // Wysyłamy na bieżący URL widoku chat
        method: 'POST',
        body: formData, // Użyj wcześniej przygotowanego formData
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Kluczowe dla odróżnienia AJAX w Django
        }
    })
    .then(response => {
        // Sprawdź najpierw status HTTP
        if (!response.ok) {
             // Spróbuj odczytać treść błędu JSON, jeśli serwer ją zwrócił
             return response.json().then(errData => {
                 // Rzuć błąd z wiadomością z serwera lub statusem
                 throw new Error(errData.error_message || `Błąd serwera: ${response.status}`);
             }).catch(() => {
                // Spróbuj odczytać jako tekst, jeśli nie JSON
                return response.text().then(text => {
                    console.error("Server non-JSON error response:", text);
                    throw new Error(text || `Błąd serwera: ${response.status}`);
                });
             });
        }
        return response.json(); // Parsuj JSON, jeśli status jest OK
    })
    .then(data => {
        console.log('Response from server:', data); // Logowanie odpowiedzi

        if (data.status === 'success') {
            // Odpowiedź asystenta
            if (data.assistant_message) {
                // Dodaj wiadomość asystenta z timestampem z serwera
                addMessage(
                    data.assistant_message.role,
                    data.assistant_message.content,
                    data.assistant_message.timestamp // Użyj timestampu z odpowiedzi
                );
            }
            errorContainer.classList.add('d-none'); // Ukryj błędy, jeśli były
        } else {
            // Obsługa błędu zwróconego w JSON (np. status: 'error')
            throw new Error(data.error_message || 'Nieznany błąd odpowiedzi serwera.');
        }
    })
    .catch(error => {
        console.error('Fetch Error:', error);
        errorMessage.textContent = 'Wystąpił błąd: ' + error.message;
        errorContainer.classList.remove('d-none');
    })
    .finally(() => {
        loadingSpinner.classList.add('d-none');
        // Sprawdź czy elementy istnieją przed próbą odblokowania
        if(promptField) {
            promptField.disabled = false; // WAŻNE: Włącz pole z powrotem
            promptField.focus(); // Ustaw focus z powrotem na pole wprowadzania
        }
        if(submitBtn) {
             submitBtn.disabled = false; // Włącz przycisk z powrotem
        }
    });
}


    // Ustaw focus na pole tekstowe po załadowaniu strony
    if(promptField) {
        promptField.focus();
    }

    // Inicjalne przewinięcie do dołu, jeśli są już wiadomości załadowane z serwera
     const chatContainer = document.getElementById('chat-container');
     if (chatContainer && chatContainer.scrollHeight > chatContainer.clientHeight) {
         chatContainer.scrollTop = chatContainer.scrollHeight;
     }

});