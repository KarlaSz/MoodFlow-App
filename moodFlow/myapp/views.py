from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Task, Conversation, Message,Category, Transaction, TYPE_CHOICES
from .forms import TaskForm, ChatForm, TransactionForm
from django.utils import timezone
from openai import OpenAI
from serpapi import GoogleSearch
import json
from .forms import ChatForm
import requests #for API wather conection
from django.utils.text import Truncator
from datetime import datetime
from django.db.models import Sum, Q
from decimal import Decimal

#for footer
def global_context(request):
    return {
        'year': datetime.now().year
    }

def home(request):
    """Strona główna - ogolna interakcja"""
    return render(request, "myapp/home.html")

def weather_api(request):
    url = 'https://danepubliczne.imgw.pl/api/data/synop'
    try:
        response = requests.get(url)
        response.raise_for_status()
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
    task.done_at = timezone.now()
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


# def get_api_key():
#     """Pobiera klucz API z pliku .env.txt"""
#     try:
#         with open('./.env.txt', 'r') as f:
#             return f.read().strip()
#     except FileNotFoundError:
#         print("Błąd: Plik .env.txt nie został znaleziony.")
#         return None
#     except Exception as e:
#         print(f"Błąd odczytu pliku z kluczem API: {str(e)}")
#         return None


def get_api_keys():
    """Pobiera klucze API z pliku .env.txt"""
    keys = {}
    try:
        with open('./.env.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key_name, key_value = line.split('=', 1)
                    keys[key_name.strip()] = key_value.strip()
    except FileNotFoundError:
        print("OSTRZEŻENIE: Plik .env.txt nie został znaleziony.")
    except Exception as e:
        print(f"Błąd odczytu pliku z kluczami API: {str(e)}")
    return keys.get('OPENAI_API_KEY'), keys.get('SERPAPI_API_KEY')


def chat(request, conversation_id=None):
    openai_api_key, serpapi_api_key = get_api_keys()
    error_message = None
    model = "gpt-4o" # lub gpt-3.5-turbo
    form = ChatForm()
    current_conversation = None
    messages_queryset = Message.objects.none()

    # Zawsze pobieraj historię dla sidebara menu - history
    conversation_history_list = Conversation.objects.all()

    if not openai_api_key:
        error_message = "Błędna konfiguracja aplikacji (brak klucza API OpenAI)."
        # Dodajemy ostrzeżenie, jeśli brakuje klucza SerpApi, ale nie blokujemy całkowicie
    if not serpapi_api_key:
        print("OSTRZEŻENIE: Brak klucza API SerpApi. Wyszukiwanie w Google będzie niedostępne.")
        # Możesz dodać error_message = "..." jeśli chcesz to pokazać użytkownikowi

    # --- Obsługa GET ---
    if request.method == 'GET':
        if conversation_id:
            # --- Ładowanie istniejącej rozmowy ---
            print(f"[DEBUG] GET: Próba załadowania conversation_id: {conversation_id}")
            try:
                current_conversation = Conversation.objects.get(id=conversation_id)
                # Pobierz wiadomości dla tej konwersacji (używa domyślnego sortowania z Meta)
                messages_queryset = current_conversation.messages.all()
                print(f"[DEBUG] GET: Znaleziono: '{current_conversation.title}'. Wiadomości: {messages_queryset.count()}")
                request.session['conversation_id'] = str(current_conversation.id)
                request.session.save()
            except Conversation.DoesNotExist:
                print(f"[DEBUG] GET: Conversation {conversation_id} nie istnieje.")
                error_message = "Wybrana rozmowa nie istnieje."
                if 'conversation_id' in request.session:
                    del request.session['conversation_id']
                # Przekieruj na stronę nowej rozmowy dla spójności
                return redirect('chat')
            except Exception as e:
                print(f"[DEBUG] GET: Błąd ładowania rozmowy {conversation_id}: {e}")
                error_message = "Wystąpił błąd serwera podczas ładowania rozmowy."
                # Nie ustawiamy current_conversation ani messages_queryset
        else:
            # --- Nowa rozmowa ---
            print("[DEBUG] GET: Ładowanie widoku dla nowej rozmowy.")
            if 'conversation_id' in request.session:
                # Jeśli użytkownik przeszedł z istniejącej rozmowy na nową, wyczyść sesję
                del request.session['conversation_id']
                request.session.save()
            # current_conversation i messages_queryset są już None/puste

    # --- Obsługa POST ---
    elif request.method == 'POST':
        # Poprawiona obsługa braku klucza OpenAI
        if not openai_api_key:
            error_msg_no_key = "Błąd konfiguracji serwera (brak klucza API OpenAI)."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'error_message': error_msg_no_key}, status=500)
            else:
                # Ustaw error_message, który zostanie użyty w kontekście renderowania szablonu
                error_message = error_msg_no_key
                # Przejdź do renderowania szablonu z błędem (nie wykonuj reszty logiki POST)
                context = {  # Przygotuj minimalny kontekst dla szablonu błędu
                    "form": form,  # Przekaż pusty formularz
                    "error_message": error_message,
                    "messages": messages_queryset,
                    "conversation": current_conversation,
                    "conversation_history_list": conversation_history_list
                }
                return render(request, "myapp/chat.html", context)

        form = ChatForm(request.POST)
        if form.is_valid():
            user_prompt = form.cleaned_data["prompt"]
            session_conversation_id = request.session.get('conversation_id')

            try:
                # --- Znajdź lub stwórz konwersację ---
                if session_conversation_id:
                    current_conversation = Conversation.objects.get(id=session_conversation_id)
                else:
                    current_conversation = Conversation.objects.create()
                    request.session['conversation_id'] = str(current_conversation.id)
                    request.session.save()

                # Ustaw tytuł, jeśli go nie ma
                if not current_conversation.title and user_prompt:
                     current_conversation.title = Truncator(user_prompt).chars(50)
                     current_conversation.save()

                # Zapisz wiadomość użytkownika
                user_message_obj = Message.objects.create(
                    conversation=current_conversation, role='user', content=user_prompt
                )
                user_timestamp = user_message_obj.get_formatted_timestamp()

                # --- NOWOŚĆ: Wyszukiwanie w Google z SerpApi ---
                search_context = ""
                if serpapi_api_key:  # Wykonaj tylko jeśli mamy klucz SerpApi
                    print(f"[DEBUG] Wykonywanie wyszukiwania SerpApi dla: '{user_prompt}'")
                    try:
                        params = {
                            "q": user_prompt,  # Zapytanie użytkownika
                            "api_key": serpapi_api_key,
                            "hl": "pl",  # Język wyników (polski)
                            "gl": "pl",  # Geolokalizacja (Polska)
                            "num": 5  # Liczba wyników (np. 5)
                        }
                        search = GoogleSearch(params)
                        results = search.get_dict()

                        # Przetwarzanie wyników - bierzemy "organic_results" (główne linki)
                        organic_results = results.get("organic_results", [])
                        if organic_results:
                            search_context += "Oto streszczenie wyników wyszukiwania Google:\n"
                            for i, result in enumerate(organic_results[:3]):  # Weźmy top 3
                                title = result.get("title", "")
                                snippet = result.get("snippet", "Brak opisu.")
                                link = result.get("link", "")  # Można dodać link, ale może zaśmiecić kontekst
                                search_context += f"{i + 1}. {title}: {snippet}\n"  # Dodajemy tytuł i opis
                        elif "answer_box" in results:  # Czasem Google daje bezpośrednią odpowiedź
                            answer_box = results["answer_box"]
                            answer = answer_box.get("answer") or answer_box.get("snippet")
                            if answer:
                                search_context += "Znaleziona szybka odpowiedź Google:\n"
                                search_context += answer + "\n"

                        if not search_context:
                            search_context = "Nie znaleziono trafnych wyników wyszukiwania w Google."
                        print(f"[DEBUG] Kontekst z SerpApi:\n{search_context}")

                    except Exception as serp_e:
                        print(f"[DEBUG] Błąd podczas wyszukiwania SerpApi: {serp_e}")
                        search_context = "Wystąpił błąd podczas próby wyszukania aktualnych informacji."
                else:
                    search_context = "Wyszukiwanie w Google jest wyłączone (brak klucza API)."
                    print("[DEBUG] Pomijanie wyszukiwania SerpApi - brak klucza.")


                # Przygotuj historię dla OpenAI
                # Pobierz wszystkie wiadomości z bazy DANYCH dla tej konwersacji
                db_messages = current_conversation.messages.all()  # Używa sortowania z Meta
                openai_history = [{"role": msg.role, "content": msg.content} for msg in db_messages]

                # --- NOWOŚĆ: Dodaj kontekst z wyszukiwania do promptu ---
                # Modyfikujemy OSTATNIĄ wiadomość użytkownika w historii wysyłanej do OpenAI
                # NIE modyfikujemy wiadomości zapisanej w bazie danych!
                if openai_history and openai_history[-1]['role'] == 'user':
                    # Tworzymy nowy, rozszerzony prompt tylko na potrzeby API call
                    augmented_user_prompt = f"""Na podstawie poniższych, aktualnych wyników wyszukiwania z Google:
                --- POCZĄTEK WYNIKÓW WYSZUKIWANIA ---
                {search_context}
                --- KONIEC WYNIKÓW WYSZUKIWANIA ---

                Odpowiedz na ostatnie pytanie użytkownika: {user_prompt}
                Pamiętaj, aby w swojej odpowiedzi bazować głównie na dostarczonych wynikach wyszukiwania, jeśli są one relewantne do pytania."""

                    # Podmieniamy treść ostatniej wiadomości w kopii historii
                    openai_history[-1]['content'] = augmented_user_prompt
                else:
                    # Sytuacja awaryjna - jeśli historia jest pusta lub ostatnia wiadomość nie jest od usera
                    # Można dodać wiadomość systemową z kontekstem lub zwrócić błąd
                    print("[OSTRZEŻENIE] Nie można było dołączyć kontekstu wyszukiwania do historii OpenAI.")

                # Wywołaj OpenAI
                print("[DEBUG] Wysyłanie zapytania do OpenAI...")
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=openai_history,  # Użyj zmodyfikowanej historii
                    temperature=0.7
                )
                assistant_response_content = response.choices[0].message.content
                print("[DEBUG] Otrzymano odpowiedź od OpenAI.")


                # Zapisz odpowiedź asystenta
                # Zapisz odpowiedź asystenta (bez zmian)
                assistant_message_obj = Message.objects.create(
                    conversation=current_conversation, role='assistant', content=assistant_response_content
                )
                assistant_timestamp = assistant_message_obj.get_formatted_timestamp()

                # Ustaw tytuł konwersacji, jeśli jeszcze go nie ma (po zapisaniu pierwszej pary wiadomości)

                if not current_conversation.title and user_prompt:
                    # Sprawdź ponownie, bo mogło zostać ustawione w innym requescie
                    current_conversation.refresh_from_db()
                    if not current_conversation.title:
                        current_conversation.title = Truncator(user_prompt).chars(50)
                        current_conversation.save()
                        # Odśwież listę w sidebarze, aby nowa konwersacja się pojawiła
                        conversation_history_list = Conversation.objects.all().order_by('-last_updated')


                # Odpowiedź AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'user_message': {'role': 'user', 'content': user_prompt, 'timestamp': user_timestamp},
                        'assistant_message': {'role': 'assistant', 'content': assistant_response_content, 'timestamp': assistant_timestamp}
                    })

                # Fallback dla zwykłego POST (mało prawdopodobne z JS)
                messages_queryset = current_conversation.messages.all()
                form = ChatForm() # Wyczyść formularz

            except Conversation.DoesNotExist:
                 # Bardzo rzadki przypadek: sesja miała ID, ale konwersacja zniknęła między GET a POST
                 print(f"[DEBUG] POST: Conversation z sesji {session_conversation_id} nie istnieje.")
                 error_message = "Wystąpił błąd sesji. Spróbuj rozpocząć nową rozmowę."
                 if 'conversation_id' in request.session: del request.session['conversation_id']
                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                     return JsonResponse({'status': 'error', 'error_message': error_message}, status=500)
                 # Renderuj z błędem

            except Exception as e:
                error_message = f"Wystąpił błąd serwera: {str(e)}"
                print(f"[DEBUG] POST Error: {e}") # Loguj błąd
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Zwróć błąd, ale bez wiadomości, bo nie wiemy, czy user_message się zapisało
                    return JsonResponse({'status': 'error', 'error_message': error_message}, status=500)
                 # Renderuj z błędem

        else: # Formularz nieprawidłowy
            if not form.is_valid():
                error_message = "Wysłano pustą wiadomość lub formularz jest nieprawidłowy."
                print(f"ChatForm errors: {form.errors}")
                status_code = 400  # Bad Request
            else:  # Błąd braku klucza OpenAI (obsłużony wyżej, ale dla pewności)
                error_message = "Błąd konfiguracji serwera (brak klucza API OpenAI)."
                status_code = 500  # Internal Server Error

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'error_message': error_message}, status=status_code)

        # Po udanym POST, odśwież historię na wypadek utworzenia nowej rozmowy
        if current_conversation:
            conversation_history_list = Conversation.objects.all().order_by('-last_updated')
            # Pobierz ponownie wiadomości dla bieżącej konwersacji, aby były aktualne w kontekście
            messages_queryset = current_conversation.messages.all()


    # --- Przygotowanie kontekstu ---
    context = {
        "form": form,
        "error_message": error_message,
        "messages": messages_queryset,
        "conversation": current_conversation,
        "conversation_history_list": conversation_history_list
    }
    print(f"[DEBUG] Rendering template. Conversation loaded: {current_conversation}. Messages in context: {messages_queryset.count() if messages_queryset else 0}")
    return render(request, "myapp/chat.html", context)

#finanse
@login_required
def finance(request):
    user = request.user
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # 1. Ostatnie transakcje - bez zmian
    recent_transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:10]

    # 2. Podsumowanie miesiąca
    monthly_transactions = Transaction.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    )
    monthly_income_sum = monthly_transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    monthly_expenses_sum = monthly_transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Opcja B: Bilans = Przychody - Wydatki - Oszczędności_z_miesiąca

    monthly_savings_sum = monthly_transactions.filter(type='saving').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    monthly_balance = monthly_income_sum - monthly_expenses_sum - monthly_savings_sum

    # --- Obliczanie ŁĄCZNYCH oszczędności ---
    # Sumujemy WSZYSTKIE transakcje typu 'saving' dla użytkownika
    total_savings_sum = Transaction.objects.filter(
        user=user,
        type='saving'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    # ------------------------------------------

    summary_data = {
        'balance': monthly_balance, # Bilans miesięczny
        'expenses': monthly_expenses_sum, # Wydatki miesięczne
        'income': monthly_income_sum, # Przychody miesięczne
        'savings': total_savings_sum, # <-- Używam łącznej sumy oszczędności
        'previous_balance': Decimal('0.00'), # Placeholder
    }

    # 3. Przygotuj dane dla budżetu (placeholder)
    budget_data = []

    # 4. Przygotuj dane dla celów (placeholder)
    goals_data = []

    # 5. Przygotuj dane dla nadchodzących płatności (placeholder)
    upcoming_payments_data = []

    # Kontekst przekazywany do szablonu
    context = {
        'recent_transactions': recent_transactions,
        'summary': summary_data,  # Przekazujemy obliczone podsumowanie
        'budgets': budget_data,
        'goals': goals_data,
        'upcoming_payments': upcoming_payments_data,
        # 'year' jest już w global_context, ale można zostawić dla pewności
        'year': today.year
    }
    return render(request, "myapp/finanse.html", context)

# --- Upewnij się, że typy w add_transaction pasują do modelu ---
@login_required
def add_transaction(request, transaction_type):
    user = request.user

    # Zaktualizowane mapowanie typów z URL na typy wewnętrzne
    type_mapping = {
        'przychod': 'income',
        'wydatek': 'expense',
        'oszczednosc': 'saving', # <-- Dodane mapowanie dla oszczędności
    }
    internal_transaction_type = type_mapping.get(transaction_type)

    if not internal_transaction_type:
        raise Http404(f"Nieprawidłowy typ transakcji w URL: {transaction_type}")

    # Pobierz przyjazną nazwę typu (np. "Oszczędność")
    type_display_name = dict(TYPE_CHOICES).get(internal_transaction_type, internal_transaction_type.capitalize())

    if request.method == 'POST':
        # Przekazujemy transaction_type do formularza, jeśli formularz go potrzebuje
        # (np. do filtrowania kategorii)
        form = TransactionForm(request.POST, user=user, transaction_type=internal_transaction_type)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = user
                transaction.type = internal_transaction_type # Ustaw poprawny typ
                transaction.save()
                # messages.success(request, f"Dodano {type_display_name.lower()}!")
                return redirect('finance')
            except Exception as e:
                print(f"Błąd zapisu transakcji: {e}")
                form.add_error(None, "Wystąpił błąd podczas zapisu.")
        else:
             print("Błędy formularza:", form.errors.as_json())
    else: # GET
        form = TransactionForm(user=user, transaction_type=internal_transaction_type)

    context = {
        'form': form,
        'type_display': type_display_name,
        'transaction_type_from_url': transaction_type, # Dla warunków w szablonie
    }
    return render(request, 'myapp/add_transaction.html', context)