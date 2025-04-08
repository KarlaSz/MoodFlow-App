import os
from openai import OpenAI


def get_api_key():
    """Pobiera klucz API z pliku openai_key.txt"""
    try:
        with open('openai_key.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Błąd: Plik openai_key.txt nie został znaleziony.")
        exit(1)
    except Exception as e:
        print(f"Błąd odczytu pliku z kluczem API: {str(e)}")
        exit(1)


def main():
    # Pobierz klucz API
    api_key = get_api_key()

    # Inicjalizacja klienta OpenAI
    client = OpenAI(api_key=api_key)

    # Historia wiadomości
    messages = []

    # Informacje o skrypcie
    print("=" * 50)
    print("ChatGPT Hello World - Prosty interfejs do API OpenAI")
    print("=" * 50)
    print("Wpisz 'exit' aby zakończyć program.")
    print("=" * 50)

    # Model domyślny
    model = "gpt-3.5-turbo"
    print(f"Używany model: {model}")

    # Główna pętla programu
    while True:
        # Pobierz prompt od użytkownika
        user_prompt = input("\nWprowadź prompt: ")

        # Zakończ program jeśli użytkownik wpisze 'exit'
        if user_prompt.lower() == 'exit':
            print("Do widzenia!")
            break

        # Dodaj wiadomość do historii
        messages.append({"role": "user", "content": user_prompt})

        try:
            # Wysyłanie żądania do API
            print("\nWysyłanie zapytania do ChatGPT...")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )

            # Dodaj odpowiedź do historii
            assistant_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_response})

            # Wyświetlenie odpowiedzi
            print("\n" + "=" * 50)
            print("Pełna odpowiedź ChatGPT:\n", response)
            print("\n" + "=" * 50)
            print("Zawartość rozmowy:\n", messages)
            print("\n" + "=" * 50)
            print("ODPOWIEDŹ CHATGPT:")
            print("=" * 50)
            print(assistant_response)
            print("=" * 50)

            # Wyświetlenie statystyk
            tokens_used = response.usage.total_tokens
            print(f"Zużyte tokeny: {tokens_used}")

        except Exception as e:
            print(f"\nWystąpił błąd: {str(e)}")


if __name__ == "__main__":
    main()