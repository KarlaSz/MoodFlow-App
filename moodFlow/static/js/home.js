document.addEventListener('DOMContentLoaded', () => {
    const citySelector = document.getElementById('city-selector');
    const temperatureElement = document.getElementById('temperature');
    const descriptionElement = document.getElementById('weather-description');
    const locationElement = document.getElementById('weather-location');
    const updatedElement = document.getElementById('weather-updated');
    const humidityElement = document.getElementById('humidity');
    const windSpeedElement = document.getElementById('wind_speed');
    const pressureElement = document.getElementById('pressure');
    const refreshButton = document.getElementById('refresh-weather');
    const lastUpdateElement = document.getElementById('last-update'); // Dodane dla czasu aktualizacji
    const weatherIconElement = document.getElementById('weather-icon'); // Dla ikony

    const weatherApiUrl = '/weather_api'; // Upewnij się, że URL jest poprawny

    // --- 1. Funkcja do aktualizacji UI danymi pogodowymi ---
    function updateWeatherUI(weatherData) {
        if (!weatherData) {
            console.error("Brak danych pogodowych do wyświetlenia");
            // Można tu wyświetlić komunikat o błędzie w UI
            locationElement.textContent = 'Brak danych';
            temperatureElement.textContent = '-°C';
            descriptionElement.textContent = '-';
            humidityElement.textContent = '- %';
            windSpeedElement.textContent = '- km/h';
            pressureElement.textContent = '- hPa';
            updatedElement.textContent = '';
            lastUpdateElement.textContent = `Ostatnia aktualizacja: ${new Date().toLocaleTimeString()}`;
            return;
        }

        console.log("Aktualizowanie UI dla:", weatherData); // Debug

        locationElement.textContent = `Miasto: ${weatherData.city || 'Nieznane miasto'}`;
        temperatureElement.textContent = `${weatherData.temperature || '?'}°C`;
        // Prosta logika opisu/ikony (można rozbudować)
        descriptionElement.textContent = determineWeatherDescription(weatherData.temperature);
        updateWeatherIcon(weatherData.temperature); // Funkcja do aktualizacji ikony

        humidityElement.textContent = `${weatherData.humidity || '?'} %`;
        // Sprawdź jednostkę wiatru zwracaną przez API (zakładam km/h, może być m/s)
        windSpeedElement.textContent = `${weatherData.wind_speed || '?'} km/h`;
        pressureElement.textContent = `${weatherData.pressure || '?'} hPa`;
        updatedElement.textContent = `Pomiar o ${weatherData.hour || '?'} godzinie`;
        lastUpdateElement.textContent = `Ostatnia aktualizacja: ${new Date().toLocaleTimeString()}`;
    }

     // --- Prosta funkcja do określania opisu pogody ---
     function determineWeatherDescription(temp) {
        if (temp === null || temp === undefined || temp === '?') return 'Brak danych';
        const tempNum = parseFloat(temp);
        if (isNaN(tempNum)) return 'Błędne dane';
        if (tempNum > 25) return 'Gorąco';
        if (tempNum > 15) return 'Ciepło';
        if (tempNum > 5) return 'Chłodno';
        return 'Zimno';
    }

    // --- Prosta funkcja do zmiany ikony ---
    function updateWeatherIcon(temp) {
        let iconClass = 'bi-question-circle'; // Domyślna ikona
        if (temp !== null && temp !== undefined && temp !== '?') {
            const tempNum = parseFloat(temp);
             if (!isNaN(tempNum)) {
                if (tempNum > 20) iconClass = 'bi-sun text-warning'; // Słonecznie/ciepło
                else if (tempNum > 5) iconClass = 'bi-cloud-sun'; // Częściowe zachmurzenie/chłodniej
                else iconClass = 'bi-snow text-info'; // Zimno/śnieg
             }
        }
        weatherIconElement.innerHTML = `<i class="bi ${iconClass}" style="font-size: 3rem;"></i>`;
    }


    // --- 2. Funkcja do pobierania danych dla konkretnego miasta ---
    async function fetchWeatherData(cityName) {
    console.log(`Pobieranie pogody dla: ${cityName}`);
    const url = `${weatherApiUrl}?city=${encodeURIComponent(cityName)}`;
    console.log(`Wysyłanie zapytania do: ${url}`);
    try {
        const response = await fetch(url);
        console.log(`Odpowiedź fetch dla ${cityName}:`, response.status, response.statusText);

        // --- POCZĄTEK BRAKUJĄCEGO KODU ---
        if (!response.ok) {
            if (response.status === 404) {
                console.error(`Miasto ${cityName} nie znalezione (status 404).`);
                const errorData = await response.json().catch(() => ({ error: `Nie znaleziono miasta: ${cityName}` })); // Spróbuj odczytać JSON z błędem
                updateWeatherUI(null);
                locationElement.textContent = errorData.error || `Nie znaleziono: ${cityName}`;
            } else {
                // Inny błąd HTTP
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return null; // Zwróć null w przypadku błędu 404 lub innego błędu HTTP
        }

        // Jeśli odpowiedź jest OK (status 200)
        const data = await response.json();
        console.log(`Dane JSON dla ${cityName}:`, data);

        if (data.error) {
            // Błąd zwrócony przez API w JSON (mimo statusu 200, np. wewnętrzny błąd API)
            console.error("Błąd zwrócony przez API:", data.error);
            updateWeatherUI(null);
            locationElement.textContent = `Błąd API: ${data.error}`;
            return null;
        }

        // Mamy poprawne dane pogodowe
        updateWeatherUI(data.weather);
        return data.weather; // Zwróć pobrane dane
        // --- KONIEC BRAKUJĄCEGO KODU ---

    } catch (error) {
        // Błędy sieciowe, błędy parsowania JSON itp.
        console.error(`Błąd podczas fetchWeatherData dla ${cityName}:`, error);
        updateWeatherUI(null); // Wyczyść UI w razie błędu
        locationElement.textContent = 'Błąd pobierania';
        return null;
    }
}

    // --- 3. Funkcja do pobierania listy miast i wypełniania selektora ---
    async function populateCitySelector(defaultCity = 'Wrocław') {
    console.log("Rozpoczynam populateCitySelector...");
    try {
        const response = await fetch(`${weatherApiUrl}?list_cities=true`);
        console.log("Odpowiedź fetch dla listy miast:", response.status, response.statusText);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Otrzymane dane miast (JSON):", data);

        // --- POCZĄTEK BRAKUJĄCEGO KODU ---
        if (data.cities && Array.isArray(data.cities)) {
            citySelector.innerHTML = '<option value="">Wybierz miasto...</option>'; // Wyczyść i dodaj placeholder
            let foundDefault = false;
            data.cities.forEach(cityData => {
                const option = document.createElement('option');
                option.value = cityData.city; // WAŻNE: ustawienie wartości
                option.textContent = cityData.city; // Tekst widoczny dla użytkownika
                if (cityData.city.toUpperCase() === defaultCity.toUpperCase()) { // Porównanie bez wielkości liter
                    option.selected = true; // Zaznacz domyślne miasto
                    foundDefault = true;
                }
                citySelector.appendChild(option);
            });

            // Jeśli domyślne miasto nie zostało znalezione na liście, upewnij się, że wybrane jest "Wybierz miasto..."
            if (!foundDefault) {
                citySelector.value = "";
                 console.warn(`Domyślne miasto "${defaultCity}" nie znalezione na liście z API.`);
            }
             console.log("Selektor miast wypełniony.");

        } else {
            console.error("Otrzymano nieprawidłowy format listy miast", data);
            citySelector.innerHTML = '<option value="">Błąd formatu danych</option>';
        }
        // --- KONIEC BRAKUJĄCEGO KODU ---

        console.log("Zakończono sukcesem populateCitySelector.");

    } catch (error) {
        console.error('Błąd podczas populateCitySelector:', error);
        citySelector.innerHTML = '<option value="">Błąd ładowania miast</option>';
        console.error("Zakończono populateCitySelector z BŁĘDEM.");
    }
}

    // --- 4. Inicjalizacja ---
    async function initializeWeatherWidget() {
    console.log("--- Rozpoczynam initializeWeatherWidget ---");
    const defaultCity = 'Wrocław';

    // 1. Najpierw pobierz i wypełnij listę miast
    await populateCitySelector(defaultCity);
    console.log("initializeWeatherWidget: Po populateCitySelector.");

    // 2. Sprawdź, co jest wybrane w selektorze
    const selectedCity = citySelector.value; // Pobierz aktualną wartość z selektora
    console.log(`initializeWeatherWidget: Miasto wybrane w selektorze: ${selectedCity || 'BRAK (pusty string)'}`);

    // 3. Pobierz pogodę tylko jeśli coś jest wybrane
    if (selectedCity) {
         console.log(`initializeWeatherWidget: Pobieranie pogody dla "${selectedCity}"`);
         await fetchWeatherData(selectedCity);
    } else {
        // To się stanie, jeśli populateCitySelector zawiedzie lub nie znajdzie domyślnego miasta
        console.warn("initializeWeatherWidget: Brak wybranego miasta, nie pobieram pogody początkowej.");
         updateWeatherUI(null); // Pokaż puste dane
         locationElement.textContent = 'Wybierz miasto';
    }
     console.log("--- Zakończono initializeWeatherWidget ---");
}

    // --- 5. Event Listeners ---
    citySelector.addEventListener('change', () => {
        const selectedCity = citySelector.value;
        if (selectedCity) {
            fetchWeatherData(selectedCity);
        } else {
             // Jeśli wybrano "Wybierz miasto...", wyczyść dane
             updateWeatherUI(null);
             locationElement.textContent = 'Wybierz miasto';
        }
    });

    refreshButton.addEventListener('click', () => {
        const selectedCity = citySelector.value;
        if (selectedCity) {
            fetchWeatherData(selectedCity);
        } else {
            alert("Wybierz miasto, aby odświeżyć pogodę.");
        }
    });

     // --- Ustawienie aktualnej daty ---
    const currentDateElement = document.getElementById('current-date');
    if (currentDateElement) {
        const today = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        currentDateElement.textContent = today.toLocaleDateString('pl-PL', options);
    }


    // --- Start ---
    initializeWeatherWidget();

});