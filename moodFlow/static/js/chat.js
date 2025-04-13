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
        return;
    }

    const formData = new FormData(chatForm);
    // Logi FormData są OK

    // --- ZABLOKUJ UI (bez dodawania wiadomości!) ---
    loadingSpinner.classList.remove('d-none');
    promptField.disabled = true;
    submitBtn.disabled = true;
    promptField.value = '';

    // --- Wyślij żądanie fetch ---
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
       // ... (obsługa błędów response.ok jak wcześniej) ...
       return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);

        if (data.status === 'success') {
            // --- DODAJ WIADOMOŚĆ UŻYTKOWNIKA (TERAZ!) ---
            if (data.user_message) {
                addMessage(
                    data.user_message.role,
                    data.user_message.content,
                    data.user_message.timestamp // <-- Użyj timestampu z serwera
                );
            }

            // --- DODAJ WIADOMOŚĆ ASYSTENTA ---
            if (data.assistant_message) {
                addMessage(
                    data.assistant_message.role,
                    data.assistant_message.content,
                    data.assistant_message.timestamp // <-- Użyj timestampu z serwera
                );
            }
            errorContainer.classList.add('d-none');

        } else { // data.status === 'error'
             // W przypadku błędu serwera, możemy zdecydować czy chcemy dodać wiadomość użytkownika
             // Jeśli serwer zwrócił ją w user_message mimo błędu
             // if (data.user_message) {
             //     addMessage(
             //         data.user_message.role,
             //         data.user_message.content,
             //         data.user_message.timestamp
             //     );
             // }
            throw new Error(data.error_message || 'Nieznany błąd odpowiedzi serwera.');
        }
    })
    .catch(error => {
        console.error('Fetch Error:', error);
        // Można by tutaj dodać wiadomość użytkownika z jakimś wskaźnikiem błędu, np. "!" obok czasu
        // addMessage('user', userMessageContent, 'Błąd wysłania'); // Prosty przykład
        errorMessage.textContent = 'Wystąpił błąd: ' + error.message;
        errorContainer.classList.remove('d-none');
    })
    .finally(() => {
        loadingSpinner.classList.add('d-none');
        if(promptField) {
            promptField.disabled = false;
            promptField.focus();
        }
        if(submitBtn) {
             submitBtn.disabled = false;
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