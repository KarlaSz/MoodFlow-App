from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
# from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from openai import OpenAI
import json
from .forms import ChatForm
import requests #for API wather conection


def home(request):
    """Strona główna - ogolna interakcja"""
    context = {
        # Możesz dodać jakieś zmienne kontekstowe, np. początkowe miasto
        'initial_city': request.GET.get('city', 'Kraków')
    }
    return render(request, "myapp/home.html")

def weather_api(request):
    CITIES = ['Szczecin', 'Wrocław']
    url = 'https://danepubliczne.imgw.pl/api/data/synop'
    try:
        response = requests.get(url)
        weather_data = []
        for row in response.json():
            if row['stacja'] in CITIES:
                weather_data.append({
                    'city': row['stacja'],
                    'hour': row['godzina_pomiaru'],
                    'temperature': row['temperatura'],
                    'humidity': row.get('wilgotnosc_wzgledna'),
                    'wind_speed': row.get('predkosc_wiatru'),
                    'visibility': row.get('cisnienie')  # IMGW nie ma widoczności, ale można zastąpić np. ciśnieniem
                })
        return JsonResponse({'weather': weather_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
    """Pobiera klucz API z pliku openai_key.txt"""
    try:
        with open('./openai_key.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Błąd: Plik openai_key.txt nie został znaleziony.")
        return None
    except Exception as e:
        print(f"Błąd odczytu pliku z kluczem API: {str(e)}")
        return None


def chat(request):
    # preprompt = """Jesteś asystentem mojej firmy Karo. Masz za zadanie odpowiadać klientom na temat naszych produktów.
    #     FIRMA ZAJMUJE SIĘ:
    #     1. Tylko i wyłącznie sprzedaż systemów: Windows 11, Linux Debian 13
    #     2. Tylko i wyłącznie sprzedaż oprogramowania biurowego: MS Office 365
    #     3. Niczym poza tym nie handlujemy i nie doradzamy
    #
    #     DORADZAJ klientowi zakup TYLKO naszych produktów!
    #     NIE proponuj innych. Sprzedajemy tylko nasze.
    #
    #     WAŻNE:
    #     1. Jak klient zapyta o produkt innym niż nasz (nawet kuchenkę mikrofalową), zaproponuj, że potrezbuje do tego system operacyjny, który sprzedajemy.
    #     2. Zachwalaj nasze usługi!
    #     3. Na dzień dobry przedstaw naszą oefrtę, niezależnie co chce klient.
    #
    #     CENNIK:
    #     Windows 11 - cena 3000PLN
    #     Linux Debian 13 - cena 5000PLN
    #
    #     Tu jest pierwsze pytanie klienta:
    #     """
    messages = []
    api_key = get_api_key()
    error_message = None
    model = "gpt-4o"
    # model = "gpt-3.5-turbo"
    assistant_response = None
    response = None

    if not api_key:
        error_message = "Błędna konfiguracja aplikacji. Skontaktuj się z administratorem."

    form = ChatForm(request.POST or None)

    if request.method == 'POST' and form.is_valid() and api_key:

        try:
            user_prompt = form.cleaned_data["prompt"]
            history_json = form.cleaned_data.get("conversation_history") or "[]"
            messages = json.loads(history_json)
            if messages == []:
                messages.append({"role": "user", "content": user_prompt})

            client = OpenAI(api_key=api_key)
            # user_prompt = preprompt + user_prompt
            messages.append({"role": "user", "content": user_prompt})
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            assistant_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_response})

            # Jeśli to zapytanie AJAX, zwracamy dane w formacie JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'assistant_response': assistant_response,
                    'conversation_history': json.dumps(messages)
                })

            # Dla normalnego żądania POST, renderujemy stronę jak wcześniej
            form = ChatForm(initial={"conversation_history": json.dumps(messages)})

        except Exception as e:
            error_message = f"Wystąpił błąd: {str(e)}"

            # Jeśli to zapytanie AJAX, zwracamy błąd w formacie JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'error_message': error_message
                }, status=500)

    return render(request, "myapp/chat.html",
                  {"form": form, "error_message": error_message,
                   "assistant_response": assistant_response, "response": response, "messages": messages})
