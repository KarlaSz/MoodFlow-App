from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Task
from .forms import TaskForm


def todo_list(request):
    """Strona główna - lista zadań + dodawanie nowych"""
    tasks = Task.objects.all().order_by("created_at")
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dodano nowe zadanie!")
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
            form.save()
            messages.success(request, "Zadanie zostało zaktualizowane!")
            return redirect("todo_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "myapp/edit_task.html", {"form": form, "task": task})


@require_POST
def delete_task(request, task_id):
    """Usuwanie zadania"""
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.warning(request, "Zadanie zostało usunięte!")
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
