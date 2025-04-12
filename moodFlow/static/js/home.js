document.addEventListener('DOMContentLoaded', () => {
    // --- Elementy DOM (bez zmian) ---
    const citySelector = document.getElementById('city-selector');
    const temperatureElement = document.getElementById('temperature');
    const descriptionElement = document.getElementById('weather-description');
    const locationElement = document.getElementById('weather-location');
    const updatedElement = document.getElementById('weather-updated');
    const humidityElement = document.getElementById('humidity');
    const windSpeedElement = document.getElementById('wind_speed');
    const pressureElement = document.getElementById('pressure');
    const refreshButton = document.getElementById('refresh-weather');
    const lastUpdateElement = document.getElementById('last-update');
    const weatherIconElement = document.getElementById('weather-icon'); // Kontener na ikonę
    const currentDateElement = document.getElementById('current-date');

    // --- NOWE: Elementy do ukrycia/pokazania ---
    const dataElementsToToggle = [
        weatherIconElement,
        temperatureElement,
        descriptionElement,
        locationElement,
        updatedElement,
        humidityElement,
        windSpeedElement,
        pressureElement
    ];

    const weatherApiUrl = '/weather_api'; // Upewnij się, że URL jest poprawny

    // --- NOWE: Funkcja do przełączania widoczności ---
    function toggleDataVisibility(show) {
        dataElementsToToggle.forEach(el => {
            if (el) {
                if (show) {
                    el.classList.remove('weather-data-loading');
                    el.classList.add('weather-data-loaded');
                } else {
                    el.classList.remove('weather-data-loaded');
                    el.classList.add('weather-data-loading');
                }
            }
        });
    }

    // --- ZMODYFIKOWANE: Funkcja aktualizacji UI ---
    function updateWeatherUI(weatherData) {
        if (!weatherData) {
            console.error("Brak danych pogodowych do wyświetlenia");
            locationElement.textContent = 'Brak danych';
            temperatureElement.textContent = '-°C';
            descriptionElement.textContent = '-';
            humidityElement.textContent = '- %';
            windSpeedElement.textContent = '- km/h';
            pressureElement.textContent = '- hPa';
            updatedElement.textContent = '';
            lastUpdateElement.textContent = `Odświeżono: ${new Date().toLocaleTimeString()}`;
             // NOWE: Zresetuj ikonę i ukryj pola
            updateWeatherIcon(null); // Przekazujemy null, aby pokazać ikonę domyślną/błędu
            toggleDataVisibility(false);
            return;
        }

        console.log("Aktualizowanie UI dla:", weatherData);

        // Aktualizacja tekstów (trochę uprościłem wyświetlanie miasta)
        locationElement.textContent = `Wybrane miasto: ${weatherData.city || 'Nieznane miasto'}`;
        temperatureElement.textContent = `${weatherData.temperature || '?'} °C`;
        descriptionElement.textContent = determineWeatherDescription(weatherData.temperature); // Używamy starej funkcji do opisu tekstowego

        // --- ZMIANA: Przekazujemy cały obiekt weatherData do funkcji ikony ---
        updateWeatherIcon(weatherData);

        humidityElement.textContent = `${weatherData.humidity || '?'} %`;
        windSpeedElement.textContent = `${weatherData.wind_speed || '?'} km/h`;
        pressureElement.textContent = `${weatherData.pressure || '?'} hPa`;
        updatedElement.textContent = `Pomiar z ${weatherData.hour || '?'} godz.`;
        lastUpdateElement.textContent = `Odświeżono: ${new Date().toLocaleTimeString()}`;

        // NOWE: Pokaż pola po wypełnieniu
        toggleDataVisibility(true);
    }

     // --- Funkcja do określania opisu pogody (bez zmian) ---
     function determineWeatherDescription(temp) {
        if (temp === null || temp === undefined || temp === '?') return 'Brak danych';
        const tempNum = parseFloat(temp);
        if (isNaN(tempNum)) return 'Błędne dane';
        if (tempNum > 25) return 'Gorąco';
        if (tempNum > 15) return 'Ciepło';
        if (tempNum > 5) return 'Chłodno';
        return 'Zimno';
    }

    // --- NOWA WERSJA: Funkcja do zmiany ikony i dodania animacji ---
    function updateWeatherIcon(weatherData) {
        let iconClass = 'bi-question-circle'; // Domyślna ikona
        let animationClass = ''; // Domyślnie brak animacji

        // Sprawdź czy mamy dane i czy temperatura jest poprawna
        if (weatherData && weatherData.temperature !== '?' && weatherData.temperature !== undefined) {
            const temp = parseFloat(weatherData.temperature);
            // Upewnij się, że precipitation_sum jest liczbą, domyślnie 0 jeśli brak
            const precipitation = parseFloat(weatherData.precipitation_sum || 0);
            // Upewnij się, że wind_speed jest liczbą, domyślnie 0 jeśli brak
            const windSpeed = parseFloat(weatherData.wind_speed || 0);

            if (isNaN(temp)) {
                 iconClass = 'bi-question-circle'; // Błąd danych temperatury
            } else if (!isNaN(precipitation) && precipitation > 0.1) { // Są opady? (Więcej niż śladowe 0.1 mm)
                if (temp <= 0) {
                    iconClass = 'bi-cloud-snow-fill'; // Śnieg
                    animationClass = 'weather-animate-snow';
                } else {
                    iconClass = 'bi-cloud-rain-heavy-fill'; // Deszcz
                    animationClass = 'weather-animate-rain';
                }
            } else if (temp <= 0) {
                iconClass = 'bi-thermometer-snow'; // Mróz/zimno bez opadów
                animationClass = 'weather-animate-cold';
            } else if (!isNaN(windSpeed) && windSpeed > 30) { // Silny wiatr? (Próg np. 30 km/h)
                 iconClass = 'bi-wind';
                 animationClass = 'weather-animate-wind';
            } else if (temp >= 25) {
                iconClass = 'bi-sun-fill'; // Gorąco/słonecznie
                animationClass = 'weather-animate-sun';
            } else if (temp >= 15) {
                 iconClass = 'bi-cloud-sun-fill'; // Ciepło, słońce z chmurką
                 animationClass = 'weather-animate-sun-cloud';
            } else { // temp między 0 a 15
                iconClass = 'bi-cloud-fill'; // Chłodno/pochmurno
                animationClass = 'weather-animate-cloud';
            }
        } else {
            // Brak danych lub błąd danych temperatury
             iconClass = 'bi-question-circle';
        }

        // Zastosuj ikonę do elementu HTML
        weatherIconElement.innerHTML = `<i class="bi ${iconClass}" style="font-size: 3rem;"></i>`;

        // Znajdź element <i> wewnątrz kontenera ikony
        const iconElement = weatherIconElement.querySelector('i');
        if (iconElement) {
             // Usuń wszystkie potencjalne stare klasy animacji (bezpieczniejsze niż remove pojedynczych)
             iconElement.className = iconElement.className.replace(/\bweather-animate-\S+/g, '').trim();
             // Dodaj nową klasę animacji, jeśli została zdefiniowana
             if (animationClass) {
                iconElement.classList.add(animationClass);
             }
        }
    }


    // --- Funkcja fetchWeatherData (bez zmian w stosunku do Twojej poprzedniej, działającej wersji) ---
    async function fetchWeatherData(cityName) {
        console.log(`Pobieranie pogody dla: ${cityName}`);
        const url = `${weatherApiUrl}?city=${encodeURIComponent(cityName)}`;
        console.log(`Wysyłanie zapytania do: ${url}`);
        try {
            const response = await fetch(url);
            console.log(`Odpowiedź fetch dla ${cityName}:`, response.status, response.statusText);

            if (!response.ok) {
                if (response.status === 404) {
                    console.error(`Miasto ${cityName} nie znalezione (status 404).`);
                    const errorData = await response.json().catch(() => ({ error: `Nie znaleziono miasta: ${cityName}` }));
                    updateWeatherUI(null);
                    locationElement.textContent = errorData.error || `Nie znaleziono: ${cityName}`;
                    toggleDataVisibility(true); // NOWE: Pokaż komunikat o błędzie
                } else {
                    updateWeatherUI(null); // Wyczyść w razie innego błędu HTTP
                    locationElement.textContent = `Błąd HTTP: ${response.status}`;
                    toggleDataVisibility(true); // NOWE: Pokaż komunikat o błędzie
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return null;
            }

            const data = await response.json();
            console.log(`Dane JSON dla ${cityName}:`, data);

            if (data.error || !data.weather) { // Dodano sprawdzenie !data.weather
                console.error("Błąd w danych API:", data.error || 'Brak klucza "weather"');
                updateWeatherUI(null);
                locationElement.textContent = `Błąd API: ${data.error || 'Nieprawidłowe dane'}`;
                toggleDataVisibility(true); // NOWE: Pokaż komunikat o błędzie
                return null;
            }

            updateWeatherUI(data.weather);
            return data.weather;

        } catch (error) {
            console.error(`Błąd podczas fetchWeatherData dla ${cityName}:`, error);
            updateWeatherUI(null);
            locationElement.textContent = 'Błąd połączenia';
            toggleDataVisibility(true); // NOWE: Pokaż komunikat o błędzie
            return null;
        }
    }

    // --- Funkcja populateCitySelector (bez zmian w stosunku do Twojej poprzedniej, działającej wersji) ---
    async function populateCitySelector(defaultCity = 'Wrocław') {
        console.log("Rozpoczynam populateCitySelector...");
        citySelector.innerHTML = '<option value="">Ładowanie miast...</option>'; // Lepiej dać znać, że ładujemy
        citySelector.disabled = true;
        try {
            const response = await fetch(`${weatherApiUrl}?list_cities=true`);
            console.log("Odpowiedź fetch dla listy miast:", response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Otrzymane dane miast (JSON):", data);

            if (data.cities && Array.isArray(data.cities)) {
                citySelector.innerHTML = '<option value="">Wybierz miasto...</option>';
                let foundDefault = false;
                data.cities.forEach(cityData => {
                    const option = document.createElement('option');
                    option.value = cityData.city;
                    option.textContent = cityData.city;
                    if (cityData.city.toUpperCase() === defaultCity.toUpperCase()) {
                        option.selected = true;
                        foundDefault = true;
                    }
                    citySelector.appendChild(option);
                });

                if (!foundDefault) {
                    citySelector.value = "";
                    console.warn(`Domyślne miasto "${defaultCity}" nie znalezione na liście z API.`);
                }
                console.log("Selektor miast wypełniony.");

            } else {
                console.error("Otrzymano nieprawidłowy format listy miast", data);
                citySelector.innerHTML = '<option value="">Błąd formatu danych</option>';
            }

        } catch (error) {
            console.error('Błąd podczas populateCitySelector:', error);
            citySelector.innerHTML = '<option value="">Błąd ładowania miast</option>';
        } finally {
            citySelector.disabled = false; // Zawsze odblokuj po zakończeniu
        }
    }

    // --- ZMODYFIKOWANE: Inicjalizacja ---
    async function initializeWeatherWidget() {
        console.log("--- Rozpoczynam initializeWeatherWidget ---");
        const defaultCity = 'Wrocław'; // Możesz zmienić z powrotem na Kraków

        // Pokaż aktualną datę od razu
        if (currentDateElement) {
            const today = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            currentDateElement.textContent = today.toLocaleDateString('pl-PL', options);
        }

        // NOWE: Ukryj pola danych na starcie
        toggleDataVisibility(false);

        // Załaduj miasta
        await populateCitySelector(defaultCity);
        console.log("initializeWeatherWidget: Po populateCitySelector.");

        // Sprawdź wybrane miasto i pobierz pogodę
        const selectedCity = citySelector.value;
        console.log(`initializeWeatherWidget: Miasto wybrane w selektorze: ${selectedCity || 'BRAK'}`);

        if (selectedCity) {
            console.log(`initializeWeatherWidget: Pobieranie pogody dla "${selectedCity}"`);
            await fetchWeatherData(selectedCity);
        } else {
            console.warn("initializeWeatherWidget: Brak wybranego miasta, nie pobieram pogody początkowej.");
            updateWeatherUI(null); // Pokaż stan błędu/braku danych
            locationElement.textContent = 'Wybierz miasto';
            toggleDataVisibility(true);
        }
        console.log("--- Zakończono initializeWeatherWidget ---");
    }

    // --- ZMODYFIKOWANE: Event Listeners ---
    citySelector.addEventListener('change', () => {
        const selectedCity = citySelector.value;
        console.log(`Zmieniono miasto na: ${selectedCity}`); // Dodano log dla debugowania
        if (selectedCity) {
             // NOWE: Ukryj stare dane przed załadowaniem nowych
             toggleDataVisibility(false);
            fetchWeatherData(selectedCity);
        } else {
            updateWeatherUI(null);
            locationElement.textContent = 'Wybierz miasto';
            // NOWE: Pokaż komunikat 'Wybierz miasto'
            toggleDataVisibility(true);
        }
    });

    refreshButton.addEventListener('click', () => {
        const selectedCity = citySelector.value;
        console.log(`Kliknięto Odśwież dla miasta: ${selectedCity || 'brak'}`); // Dodano log
        if (selectedCity) {
             // NOWE: Ukryj stare dane przed załadowaniem nowych
             toggleDataVisibility(false);
            fetchWeatherData(selectedCity);
        } else {
            // Zmieniono alert na bardziej informacyjny
            alert("Najpierw wybierz miasto z listy, aby odświeżyć pogodę.");
        }
    });

    // --- Start (bez zmian) ---
    initializeWeatherWidget();

});