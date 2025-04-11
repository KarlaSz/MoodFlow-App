document.addEventListener('DOMContentLoaded', function () {
    console.log("🟢 DOM załadowany");

    const today = new Date();
    document.getElementById('current-date').textContent = today.toLocaleDateString('pl-PL', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });

    // Debugowanie: Sprawdźmy czy wszystkie elementy są znajdowane
    console.log("citySelector:", document.getElementById('city-selector'));
    console.log("refreshBtn:", document.getElementById('refresh-weather'));
    console.log("lastUpdateSpan:", document.querySelector('.mt-3.d-flex.justify-content-between.align-items-center.small.text-white-50 span'));

    // Pobierz selector miasta i dodaj obsługę zmiany
    const citySelector = document.getElementById('city-selector');
    const refreshBtn = document.getElementById('refresh-weather');
    // Bezpośrednie odniesienie do elementu z datą aktualizacji
    const lastUpdateSpan = document.querySelector('.mt-3.d-flex.justify-content-between.align-items-center.small.text-white-50 span');

    // Ustaw początkowe miasto z URL lub domyślne
    const urlParams = new URLSearchParams(window.location.search);
    const cityParam = urlParams.get('city') || 'KRAKÓW';
    const city = cityParam.toUpperCase();

    console.log("Wybrane miasto:", city);

    // Ustaw wybrane miasto w selektorze zgodnie z parametrem URL
    if (citySelector) {
        for (let i = 0; i < citySelector.options.length; i++) {
            if (citySelector.options[i].value === city) {
                citySelector.selectedIndex = i;
                break;
            }
        }
    }

    function updateWeatherDisplay(data) {
        console.log("✅ Dane znalezione dla miasta:", data.stacja);
        console.log("Pełne dane pogodowe:", data);

        // Sprawdzamy klucze dostępne w danych - możliwe że API zwraca inne nazwy pól
        // Używamy try/catch aby uniknąć błędów jeśli dane mają inną strukturę
        try {
            document.getElementById('temperature').textContent = `${data.temperatura || '?'}°C`;
            document.getElementById('weather-description').textContent = 'Dane IMGW';

            // Sprawdzamy różne możliwe nazwy pól dla wilgotności
            const humidity = data.wilgotnosc_wzgledna || data.wilgotnosc || '?';
            document.getElementById('humidity').textContent = `${humidity}%`;

            // Sprawdzamy różne możliwe nazwy pól dla prędkości wiatru
            const wind = data.predkosc_wiatru || data.wiatr || '?';
            document.getElementById('wind-speed').textContent = `${wind} km/h`;

            document.getElementById('visibility').textContent = '–';
            document.getElementById('weather-location').textContent = `Miasto: ${data.stacja}`;

            // Aktualizacja czasu pobrania danych
            const now = new Date();
            if (lastUpdateSpan) {
                lastUpdateSpan.textContent = `Ostatnia aktualizacja: ${now.toLocaleTimeString('pl-PL')}`;
            }
        } catch (e) {
            console.error("Błąd podczas aktualizacji interfejsu:", e);
        }
    }

    function fetchWeather() {
        console.log("🔄 Pobieranie danych pogodowych…");

        fetch('https://danepubliczne.imgw.pl/api/data/synop')
            .then(response => {
                console.log("🟡 Odpowiedź z serwera IMGW:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("Otrzymane dane z API:", data);

                // Najpierw sprawdzamy strukturę danych
                if (!Array.isArray(data)) {
                    console.error("Dane z API nie są tablicą!");
                    return;
                }

                // Szukamy dokładnego dopasowania lub częściowego
                let found = data.find(entry => entry.stacja && entry.stacja.toUpperCase() === city);

                // Jeśli nie znaleziono dokładnego dopasowania, szukamy częściowego
                if (!found) {
                    found = data.find(entry => entry.stacja && entry.stacja.toUpperCase().includes(city));
                }

                if (found) {
                    updateWeatherDisplay(found);
                } else {
                    alert(`❌ Brak danych pogodowych dla miasta: ${city}`);
                    console.warn("Nie znaleziono miasta:", city);
                }
            })
            .catch(error => {
                console.error('❌ Błąd przy fetchu:', error);
                alert('Nie udało się pobrać danych pogodowych.');
            });
    }

    // Obsługa przycisku odświeżania
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function () {
            console.log("🧊 Kliknięto: Odśwież pogodę");
            fetchWeather();
        });
    }

    // Obsługa zmiany miasta - dodajemy brakującą funkcjonalność!
    if (citySelector) {
        citySelector.addEventListener('change', function() {
            const selectedCity = citySelector.value;
            console.log("Wybrano nowe miasto:", selectedCity);

            // Aktualizuj URL z nowym parametrem miasta
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('city', selectedCity);
            window.location.href = newUrl.toString();
        });
    } else {
        console.error("Nie znaleziono selektora miasta!");
    }

    // Automatyczne ładowanie przy starcie
    fetchWeather();
});