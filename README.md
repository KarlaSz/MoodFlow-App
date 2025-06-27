# MoodFlow - Aplikacja do Zarządzania Życiem

MoodFlow to kompleksowa aplikacja webowa zaprojektowana, aby pomóc użytkownikom w zintegrowanym zarządzaniu różnymi aspektami ich codziennego życia: czasem, zadaniami, nastrojem oraz finansami osobistymi. Aplikacja została stworzona jako projekt w ramach studiów podyplomowych, wykorzystując Python i framework Django.


![moodflow](https://github.com/user-attachments/assets/e4095b06-3d2b-4f06-b4ef-89a26ea005b3)
![mockuperdziennik](https://github.com/user-attachments/assets/9b04bfc7-bd62-44ef-91e2-3dca769b9dab)

![moodflow-app 3png](https://github.com/user-attachments/assets/ae201fd4-0b9b-4d6e-824a-78ecd98c5642)

## Kluczowe Funkcjonalności

*   **Dashboard (Strona Główna):** Centralny punkt startowy z szybkim dostępem do głównych modułów, widżetem pogodowym (integracja z API IMGW) oraz inspirującymi cytatami.
*   **Asystent AI:** Spersonalizowany chatbot oparty na API OpenAI (modele GPT), wzbogacony o możliwość wyszukiwania aktualnych informacji w Google dzięki integracji z SerpApi. Rozmowy są przechowywane w bazie danych i przypisane do użytkownika.
*   **Dziennik & Planner:** Moduł do tworzenia i zarządzania zadaniami, notatkami, pomysłami lub wpisami dziennika.
    *   Możliwość powiązania **nastroju** z każdym wpisem.
    *   Śledzenie **statusu** zadań (Nowy, W trakcie, Zrobione).
    *   Filtrowanie i sortowanie wpisów.
    *   Automatyczne zapisywanie daty utworzenia i modyfikacji.
*   **Tracker Finansów:** Narzędzie do monitorowania przychodów i wydatków.
    *   Rejestrowanie transakcji z możliwością kategoryzacji.
    *   Podstawowa analiza i wizualizacja danych finansowych.
    *   Przeglądanie historii transakcji.
*   **Zarządzanie Użytkownikami:** Bezpieczna rejestracja i logowanie użytkowników (l:user/pass:merito25) dzięki wbudowanemu systemowi Django Auth. Prywatność danych zapewniona poprzez izolację danych per użytkownik.

## Stos Technologiczny

*   **Backend:** Python 3.x, Django
*   **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
*   **Baza Danych:** SQLite3 na DBeaver
*   **API Zewnętrzne:**
    *   OpenAI API
    *   SerpApi (Google Search Results API)
    *   IMGW Synoptic Data API (dla danych pogodowych)

## Instalacja i Uruchomienie Lokalne

Aby uruchomić aplikację MoodFlow lokalnie na swoim komputerze, postępuj zgodnie z poniższymi krokami:

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/KarlaSz/MoodFlow-App.git
    ```

2.  **Utwórz i aktywuj środowisko wirtualne:**
    ```bash
    # Dla Windows
    python -m venv venv
    venv\Scripts\activate

    # Dla macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Zainstaluj zależności:**
    
    ```bash
    pip install -r requirements.txt
    ```

4.  **Otwórz projekt**
    ```bash
     cd moodflow
    ```

4.  **Skonfiguruj zmienne środowiskowe:** Jeśli nie chce to możesz od razu uruchomić serwer - next step 5.

    Aplikacja wymaga kluczy API i innych ustawień konfiguracyjnych.
    *   Skopiuj plik `.env.example` (jeśli istnieje) do `.env`:
        ```bash
#        cp .env.example .env
        ```
        Jeśli plik `.env.example` nie istnieje, utwórz ręcznie plik `.env` w głównym katalogu projektu.
    *   Edytuj plik `.env` i dodaj wymagane zmienne:
        ```plaintext
        # Przykład zawartości pliku .env
        SECRET_KEY='twoj_bardzo_tajny_klucz_django_tutaj' # Wygeneruj nowy, silny klucz!
        DEBUG=True # Ustaw na False w środowisku produkcyjnym
        OPENAI_API_KEY='twoj_klucz_api_openai'
        SERPAPI_API_KEY='twoj_klucz_api_serpapi'
        # Opcjonalnie inne zmienne, np. klucz do API IMGW
        ```
    *   **WAŻNE:** Zdobądź własne klucze API z [OpenAI](https://platform.openai.com/) i [SerpApi](https://serpapi.com/). Nigdy nie udostępniaj swoich kluczy publicznie. *(tutaj wpływa to na działanie chataGpt)

5.  **Uruchom serwer deweloperski:**
    ```bash
    python manage.py runserver
    ```

6.  **Otwórz aplikację w przeglądarce:**
    Przejdź pod adres [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Użytkowanie

*   Po uruchomieniu serwera, możesz zarejestrować nowego użytkownika lub zalogować się, jeśli już masz konto.
*   Panel administracyjny Django jest dostępny pod adresem `/admin/` (wymaga logowania jako user/merito25).
*   Eksploruj dostępne moduły (Dziennik, Finanse, Asystent AI) z poziomu strony głównej lub menu nawigacyjnego.

## Autor

*   **Karolina Szymaszkiewicz** 
