from django.urls import path
from .views import todo_list, edit_task, delete_task, toggle_done, api_list_tasks, api_task_details

urlpatterns = [
    # URL-e dla głównych widoków
    path('', todo_list, name='todo_list'),  # Strona główna - lista zadań
    path('edit/<int:task_id>/', edit_task, name='edit_task'),  # Edycja zadania
    path('delete/<int:task_id>/', delete_task, name='delete_task'),  # Usuwanie zadania
    path('toggle/<int:task_id>/', toggle_done, name='toggle_done'),  # Zmiana statusu zadania

    # API endpoints (związane z API)
    path('api/tasks/', api_list_tasks, name='api_list_tasks'),  # Lista zadań API
    path('api/task/<int:task_id>/', api_task_details, name='api_task_details'),  # Szczegóły zadania API
]


# urlpatterns = [
#     path('', views.todo_list, name='todo_list'),
#     path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
#     path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
#     path('toggle/<int:task_id>/', views.toggle_done, name='toggle_done'),
#
#     # API endpoints
#     path('api/tasks/', views.api_list_tasks, name='api_list_tasks'),
#     path('api/task/<int:task_id>/', views.api_task_details, name='api_task_details'),
# ]
