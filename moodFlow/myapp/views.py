from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from openai import OpenAI
import json

from .forms import ChatForm

def home(request):
    """Strona główna - ogolna interakcja"""

    return render(request, "myapp/home.html")

def finance(request):
    """Strona finansowa"""

    return render(request, "myapp/finanse.html")

def news(request):
    """Strona news"""
    return render(request, "myapp/wiadomosci.html")



def todo_list(request):
    """dziennik  - lista zadań + dodawanie nowych"""
    tasks = Task.objects.all().order_by("created_at")
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, "Dodano nowe zadanie!")
            return redirect("todo_list")
    else:
        form = TaskForm()

    return render(request, "myapp/todo.html", {"tasks": tasks, "form": form})

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

    return render(request, "myapp/edit_task.html", {"form": form, "task": task})


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


def get_api_key():
    """Pobiera klucz API z pliku openai_key.txt"""
    try:
        with open('../openai_key.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Błąd: Plik openai_key.txt nie został znaleziony.")
        return None
    except Exception as e:
        print(f"Błąd odczytu pliku z kluczem API: {str(e)}")
        return None


def chat(request):
    preprompt = """Jesteś asystentem mojej firmy webszyk. Masz za zadanie odpowiadac klientom na temat naszych produktow. Firma zajmuje sie:
        1. tylko i wylacznie sprzedaz oprogramowania na win11, linux Debian 13
        2. Tylko i wylacznie sprzedaz oprogramowania biurowego MS office 365

        Nie prponuj innych produktow tylko nasze.


        Tu jest pierwsze pytanie klienta:
        """
    messages = []
    api_key = get_api_key()
    error_message = None
    model = "gpt-3.5-turbo"
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
                messages.append({"role": "user", "content": preprompt})

            client = OpenAI(api_key=api_key)
            user_prompt = preprompt + user_prompt
            messages.append({"role": "user", "content": user_prompt})
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            assistant_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_response})

            form = ChatForm(initial={"conversation_history": json.dumps(messages)})

        except Exception as e:
            error_message = f"Wystąpił błąd: {str(e)}"

    return render(request, "myapp/chat.html",
                  {"form": form, "error_message": error_message,
                   "assistant_response": assistant_response, "response": response, "messages": messages})
