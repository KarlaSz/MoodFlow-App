document.addEventListener('DOMContentLoaded', function() {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const today = new Date();
        document.getElementById('current-date').textContent = today.toLocaleDateString('pl-PL', options);

        // Symulacja odświeżania pogody
        document.getElementById('refresh-weather').addEventListener('click', function() {
            // Tutaj można dodać kod do pobierania danych z API pogodowego
            alert('Odświeżanie danych pogodowych...');
        });
    });