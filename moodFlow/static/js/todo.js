document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded!');  // Sprawdzenie, czy DOM jest w pełni załadowany.

    const form = document.querySelector('form');

    if (form) {
        console.log('Form found!');
        form.addEventListener('keydown', function(event) {
            console.log('Key pressed:', event.key);  // Wypisuje klawisz
            console.log('Event target:', event.target);  // Sprawdza, z którego pola pochodzi klawisz

            const tag = event.target.tagName.toLowerCase();
            const type = event.target.getAttribute('type');

            const isTextInput = (tag === 'textarea') || (tag === 'input' && type === 'text');

            if (isTextInput && event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Nie przechodź do nowego wiersza
                form.submit();  // Wysyła formularz
            }
        });
    } else {
        console.log('Form not found.');
    }
});