from django.urls import path
from .views import (home, finance, news, chat, todo_list, edit_task, delete_task,
                    toggle_done, api_list_tasks, api_task_details,weather_api, add_transaction)

urlpatterns = [
    # URL-e dla głównych widoków
    path('', home, name='home'),  # Strona główna - lista zadań
    path('weather_api', weather_api, name='weather_api'), #http://localhost:8000/?city=KRAKÓW
    path('dziennik', todo_list, name='todo_list'),  # dziennik aktywnosci - lista zadań
    path('finanse', finance, name='finance'), #finanse
    path('wiadomosci', news, name='news'),
    path('edit/<int:task_id>/', edit_task, name='edit_task'),  # Edycja zadania
    path('delete/<int:task_id>/', delete_task, name='delete_task'),  # Usuwanie zadania
    path('toggle/<int:task_id>/', toggle_done, name='toggle_done'),  # Zmiana statusu zadania

    path('finanse/dodaj/<str:transaction_type>/', add_transaction, name='add_transaction'),

    # API endpoints (związane z API)
    path('api/tasks/', api_list_tasks, name='api_list_tasks'),  # Lista zadań API
    path('api/task/<int:task_id>/', api_task_details, name='api_task_details'),  # Szczegóły zadania API

    path('chat/', chat, name='chat'),
    path('chat/<uuid:conversation_id>/', chat, name='chat_view_conversation'),
    # path('chat/delete/<uuid:conversation_id>/', delete_conversation, name='delete_conversation'),

]

