from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Task, Conversation, Message
from .forms import TaskForm, ChatForm
from django.utils import timezone
from openai import OpenAI
import json
from .forms import ChatForm
import requests #for API wather conection
from django.utils.text import Truncator



def home(request):
    """Strona główna - ogolna interakcja"""
    return render(request, "myapp/home.html")

def weather_api(request):
    url = 'https://danepubliczne.imgw.pl/api/data/synop'
    try:
        response = requests.get(url)
        response.raise_for_status() # Dodaj sprawdzanie statusu HTTP
        weather_data = []
        data = response.json()

        if request.GET.get('list_cities') == 'true':
            cities = [{'city': row['stacja']} for row in data]
             # Sortowanie miast alfabetycznie po stronie serwera
            cities.sort(key=lambda x: x['city'])
            return JsonResponse({'cities': cities})

        city = request.GET.get('city')
        if city:
            found = False # Flaga do sprawdzenia czy znaleziono miasto
            for row in data:
                # Porównanie bez uwzględniania wielkości liter jest dobre
                if row['stacja'].upper() == city.upper():
                    weather_data = {
                        'city': row['stacja'],
                        'hour': row.get('godzina_pomiaru', '?'), # Użyj .get() dla bezpieczeństwa
                        'temperature': row.get('temperatura', '?'),
                        'humidity': row.get('wilgotnosc_wzgledna', '?'),
                        'wind_speed': row.get('predkosc_wiatru', '?'),
                        'pressure': row.get('cisnienie', '?'),
                        'precipitation_sum': float(row.get('suma_opadu', 0.0) or 0.0)
                    }
                    found = True # Znaleziono miasto
                    break # Można przerwać pętlę po znalezieniu
            if found:
                return JsonResponse({'weather': weather_data})
            else:
                # Miasto nie znalezione - zwróć błąd 404
                return JsonResponse({'error': f'Miasto "{city}" nie zostało znalezione'}, status=404)

        # Domyślne zachowanie (jeśli nie ma ?list_cities ani ?city)
        # Można by zwrócić błąd lub dane dla domyślnego miasta,
        # ale obecna implementacja zwracająca wszystko też jest akceptowalna,
        # chociaż frontend nie powinien wywoływać API w ten sposób.
        # W tym przykładzie zostawiamy jak jest, ale dodajemy .get() dla bezpieczeństwa
        for row in data:
             weather_data.append({
                'city': row['stacja'],
                'hour': row.get('godzina_pomiaru', '?'),
                'temperature': row.get('temperatura', '?'),
                'humidity': row.get('wilgotnosc_wzgledna', '?'),
                'wind_speed': row.get('predkosc_wiatru', '?'),
                'pressure': row.get('cisnienie', '?')
             })
        return JsonResponse({'weather': weather_data}) # Zwraca listę, a nie pojedynczy obiekt 'weather'

    except requests.exceptions.RequestException as e:
        # Lepsze logowanie błędów połączenia
        print(f"Błąd połączenia z API IMGW: {e}")
        return JsonResponse({'error': 'Błąd połączenia z serwisem pogodowym.'}, status=502) # Bad Gateway
    except json.JSONDecodeError as e:
         # Błąd parsowania JSON
        print(f"Błąd dekodowania JSON z API IMGW: {e}")
        return JsonResponse({'error': 'Nieprawidłowa odpowiedź z serwisu pogodowego.'}, status=502)
    except Exception as e:
        # Ogólny błąd serwera
        print(f"Nieoczekiwany błąd w weather_api: {e}") # Logowanie błędu na serwerze
        return JsonResponse({'error': f'Wystąpił wewnętrzny błąd serwera: {str(e)}'}, status=500)

def finance(request):
    """Strona finansowa"""

    return render(request, "myapp/finanse.html")

def news(request):
    """Strona news"""
    return render(request, "myapp/wiadomosci.html")



def todo_list(request):
    """dziennik  - lista zadań + dodawanie nowych"""

    status_filter = request.GET.get("status")  # np. ?status=pending queryParameter

    if status_filter:
        # print("STATUS FILTER:", status_filter)  # zobaczysz w terminalu
        tasks = Task.objects.filter(status=status_filter).order_by("created_at")
    else:
        tasks = Task.objects.all().order_by("created_at")

    task_count = tasks.count()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, "Dodano nowe zadanie!")
            return redirect("todo_list")
    else:
        form = TaskForm()

    STATUS_LABELS = {
        'pending': '💭 Zaplanowane',
        'in_progress': '⏳ W trakcie',
        'completed': '✅ Ukończone',
    }


    return render(request, "myapp/todo.html",
                  {"tasks": tasks,
                   "form": form,
                   'task_count': task_count,
                   "status_filter": status_filter,
                   "filter_label": STATUS_LABELS.get(status_filter),
                   })

def edit_task(request, task_id):
    """Edycja istniejącego zadania"""
    task = get_object_or_404(Task, id=task_id)


    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.updated_at = timezone.now()
            task.save()
            # messages.success(request, "Zadanie zostało zaktualizowane!")
            return redirect("todo_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "myapp/edit_task.html", {"form": form, "task": task, "task.updated_at": task.updated_at})


@require_POST
def delete_task(request, task_id):
    """Usuwanie zadania"""
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    # messages.warning(request, "Zadanie zostało usunięte!")
    return redirect("todo_list")


@require_POST
def toggle_done(request, task_id):
    """Zmiana statusu zadania"""
    task = get_object_or_404(Task, id=task_id)
    task.status = "completed" if task.status != "completed" else "pending"
    task.save()
    return redirect("todo_list")


# API - lista wszystkich zadań
def api_list_tasks(request):
    """Zwraca listę zadań w formacie JSON"""
    tasks = Task.objects.all()
    tasks_data = list(tasks.values("id", "title", "comment", "url", "mood_choice", "status", "created_at"))
    return JsonResponse(tasks_data, safe=False)


# API - szczegóły pojedynczego zadania
def api_task_details(request, task_id):
    """Zwraca szczegóły jednego zadania"""
    task = get_object_or_404(Task, id=task_id)
    task_data = {
        "id": task.id,
        "title": task.title,
        "comment": task.comment,
        "url": task.url,
        "mood_choice": task.mood_choice,
        "status": task.status,
        "created_at": task.created_at,
    }
    return JsonResponse(task_data)

def toggle_done(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Przełączanie między "completed" i "pending"
    if task.status == 'completed':
        task.status = 'pending'
    else:
        task.status = 'completed'

    task.save()
    return redirect('todo_list')  # wraca na główną listę


def get_api_key():
    """Pobiera klucz API z pliku .env.txt"""
    try:
        with open('./.env.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Błąd: Plik .env.txt nie został znaleziony.")
        return None
    except Exception as e:
        print(f"Błąd odczytu pliku z kluczem API: {str(e)}")
        return None


# def chat(request):
#     # preprompt = """Jesteś asystentem mojej firmy Karo. Masz za zadanie odpowiadać klientom na temat naszych produktów.
#     #     FIRMA ZAJMUJE SIĘ:
#     #     1. Tylko i wyłącznie sprzedaż systemów: Windows 11, Linux Debian 13
#     #     2. Tylko i wyłącznie sprzedaż oprogramowania biurowego: MS Office 365
#     #     3. Niczym poza tym nie handlujemy i nie doradzamy
#     #
#     #     DORADZAJ klientowi zakup TYLKO naszych produktów!
#     #     NIE proponuj innych. Sprzedajemy tylko nasze.
#     #
#     #     WAŻNE:
#     #     1. Jak klient zapyta o produkt innym niż nasz (nawet kuchenkę mikrofalową), zaproponuj, że potrezbuje do tego system operacyjny, który sprzedajemy.
#     #     2. Zachwalaj nasze usługi!
#     #     3. Na dzień dobry przedstaw naszą oefrtę, niezależnie co chce klient.
#     #
#     #     CENNIK:
#     #     Windows 11 - cena 3000PLN
#     #     Linux Debian 13 - cena 5000PLN
#     #
#     #     Tu jest pierwsze pytanie klienta:
#     #     """
#     messages = []
#     api_key = get_api_key()
#     error_message = None
#     model = "gpt-4o"
#     # model = "gpt-3.5-turbo"
#     assistant_response = None
#     response = None
#
#     if not api_key:
#         error_message = "Błędna konfiguracja aplikacji. Skontaktuj się z administratorem."
#
#     form = ChatForm(request.POST or None)
#
#     if request.method == 'POST' and form.is_valid() and api_key:
#
#         try:
#             user_prompt = form.cleaned_data["prompt"]
#             history_json = form.cleaned_data.get("conversation_history") or "[]"
#             messages = json.loads(history_json)
#             if messages == []:
#                 messages.append({"role": "user", "content": user_prompt})
#
#             client = OpenAI(api_key=api_key)
#             # user_prompt = preprompt + user_prompt
#             messages.append({"role": "user", "content": user_prompt})
#             response = client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 temperature=0.7
#             )
#             assistant_response = response.choices[0].message.content
#             messages.append({"role": "assistant", "content": assistant_response})
#
#             # Jeśli to zapytanie AJAX, zwracamy dane w formacie JSON
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'status': 'success',
#                     'assistant_response': assistant_response,
#                     'conversation_history': json.dumps(messages)
#                 })
#
#             # Dla normalnego żądania POST, renderujemy stronę jak wcześniej
#             form = ChatForm(initial={"conversation_history": json.dumps(messages)})
#
#         except Exception as e:
#             error_message = f"Wystąpił błąd: {str(e)}"
#
#             # Jeśli to zapytanie AJAX, zwracamy błąd w formacie JSON
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'status': 'error',
#                     'error_message': error_message
#                 }, status=500)
#
#     return render(request, "myapp/chat.html",
#                   {"form": form, "error_message": error_message,
#                    "assistant_response": assistant_response, "response": response, "messages": messages})

def chat(request, conversation_id=None):
    api_key = get_api_key()
    error_message = None
    model = "gpt-4o"
    form = ChatForm() # Zawsze zaczynaj z pustym formularzem dla GET
    current_conversation = None
    messages_queryset = Message.objects.none()

    # --- Pobierz listę konwersacji dla sidebara (Zawsze) ---
    # TODO: W przyszłości filtruj po zalogowanym użytkowniku, jeśli dodasz logowanie
    conversation_history_list = Conversation.objects.all().order_by('-created_at')

    if not api_key:
        error_message = "Błędna konfiguracja aplikacji. Skontaktuj się z administratorem."
        # Można od razu renderować z błędem, ale obsłużymy poniżej

    # --- Logika dla GET (ładowanie strony / kliknięcie linku rozmowy / kliknięcie "Nowa rozmowa") ---
    if request.method == 'GET':
        if conversation_id:
            # Użytkownik kliknął link do konkretnej rozmowy
            try:
                current_conversation = Conversation.objects.get(id=conversation_id)
                messages_queryset = current_conversation.messages.all().order_by('timestamp')
                # Ustaw tę rozmowę jako aktywną w sesji
                request.session['conversation_id'] = str(current_conversation.id)
                request.session.save() # Jawne zapisanie dla pewności
            except Conversation.DoesNotExist:
                # ID w URL jest nieprawidłowe, traktuj jak nową rozmowę
                error_message = "Wybrana rozmowa nie istnieje."
                if 'conversation_id' in request.session:
                    del request.session['conversation_id'] # Wyczyść błędne ID z sesji
                current_conversation = None
                messages_queryset = Message.objects.none()
                # Można też przekierować: return redirect('chat')
        else:
            # Użytkownik wszedł na /chat/ lub kliknął "Nowa rozmowa"
            # Kluczowe: Usuń ID poprzedniej rozmowy z sesji, aby wymusić utworzenie nowej przy POST
            if 'conversation_id' in request.session:
                del request.session['conversation_id']
                request.session.save()
            # Stan dla nowej rozmowy (już ustawiony domyślnie)
            current_conversation = None
            messages_queryset = Message.objects.none()

    # --- Logika dla POST (wysyłanie wiadomości) ---
    elif request.method == 'POST' and api_key:
        form = ChatForm(request.POST)
        if form.is_valid():
            user_prompt = form.cleaned_data["prompt"]
            session_conversation_id = request.session.get('conversation_id')

            # --- Znajdź lub stwórz konwersację ---
            if session_conversation_id:
                try:
                    current_conversation = Conversation.objects.get(id=session_conversation_id)
                except Conversation.DoesNotExist:
                    # Sesja miała ID, ale rozmowy już nie ma -> stwórz nową
                    current_conversation = Conversation.objects.create()
                    request.session['conversation_id'] = str(current_conversation.id)
                    request.session.save()
            else:
                # Brak ID w sesji (bo to pierwszy POST po wejściu na /chat/ lub po błędzie) -> stwórz nową
                current_conversation = Conversation.objects.create()
                request.session['conversation_id'] = str(current_conversation.id)
                request.session.save()

            # --- Ustawienie tytułu (jeśli go nie ma) ---
            if not current_conversation.title and user_prompt:
                 current_conversation.title = Truncator(user_prompt).chars(50) # Możesz dostosować długość
                 current_conversation.save()

            # --- Zapisz wiadomość użytkownika ---
            user_message_obj = Message.objects.create(
                conversation=current_conversation, role='user', content=user_prompt
            )
            user_timestamp = user_message_obj.get_formatted_timestamp()

            # --- Przygotuj historię dla OpenAI ---
            openai_history = [{"role": msg.role, "content": msg.content}
                              for msg in current_conversation.messages.all().order_by('timestamp')]

            # --- Wywołanie OpenAI ---
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model, messages=openai_history, temperature=0.7
                )
                assistant_response_content = response.choices[0].message.content

                # --- Zapisz odpowiedź asystenta ---
                assistant_message_obj = Message.objects.create(
                    conversation=current_conversation, role='assistant', content=assistant_response_content
                )
                assistant_timestamp = assistant_message_obj.get_formatted_timestamp()

                # --- Odpowiedź AJAX ---
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Odśwież listę historii PO dodaniu nowej wiadomości/konwersacji
                    # aby sidebar mógł się potencjalnie zaktualizować (jeśli dodasz taką logikę w JS)
                    # Chociaż prostsze jest odświeżenie strony po przejściu do innej konwersacji.
                    # conversation_history_list = Conversation.objects.all().order_by('-created_at')
                    # Na razie nie wysyłamy historii w AJAX, sidebar aktualizuje się przy przeładowaniu strony.
                    return JsonResponse({
                        'status': 'success',
                        'user_message': {'role': 'user', 'content': user_prompt, 'timestamp': user_timestamp},
                        'assistant_message': {'role': 'assistant', 'content': assistant_response_content, 'timestamp': assistant_timestamp}
                    })

                # --- Odpowiedź dla zwykłego POST (jeśli AJAX nie był użyty - mało prawdopodobne z twoim JS) ---
                messages_queryset = current_conversation.messages.all().order_by('timestamp')
                form = ChatForm() # Wyczyść formularz

            except Exception as e:
                error_message = f"Błąd OpenAI: {str(e)}"
                print(f"OpenAI Error: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'error_message': error_message}, status=500)

        else: # Formularz nieprawidłowy
             error_message = "Błąd formularza."
             print(f"ChatForm errors: {form.errors}")
             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                 return JsonResponse({'status': 'error', 'error_message': 'Nieprawidłowe dane.'}, status=400)

        # --- Odśwież listę historii po udanym POST ---
        # To ważne, jeśli nowa konwersacja została właśnie utworzona
        conversation_history_list = Conversation.objects.all().order_by('-created_at')


    # --- Przygotowanie kontekstu dla szablonu (dla GET i zwykłego POST) ---
    context = {
        "form": form,
        "error_message": error_message,
        "messages": messages_queryset,       # Wiadomości *bieżącej* rozmowy (lub puste)
        "conversation": current_conversation, # *Bieżący* obiekt rozmowy (lub None)
        "conversation_history_list": conversation_history_list # *Lista* wszystkich rozmów dla sidebara
    }
    return render(request, "myapp/chat.html", context)
