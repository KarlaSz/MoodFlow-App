from django.db import models
from django.utils import timezone
from django.utils.text import Truncator # Do skracania tytułu
import uuid
from django.conf import settings


MOOD_CHOICES = [
    ("very_happy", "😊 Bardzo szczęśliwy"),
    ("happy", "🙂 Szczęśliwy"),
    ("neutral", "😐 Neutralny"),
    ("sad", "☹️ Smutny"),
    ("very_sad", "😢 Bardzo smutny"),
    ("stressed", "😖 Zestresowany"),
    ("anxious", "😟 Zaniepokojony"),
    ("tired", "😴 Zmęczony"),
    ("angry", "😡 Zły"),
]

IDEA_STATUS = [
    ("pending", "💡 Oczekujące"),
    ("in_progress", "⏳ W trakcie"),
    ("completed", "✅ Zakończone"),
]

class Task(models.Model):
    title = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    url = models.URLField(null=True, blank=True)
    mood_choice = models.CharField(choices=MOOD_CHOICES, max_length=20, default="neutral")
    status = models.CharField(choices=IDEA_STATUS, max_length=30, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title


#DB for chat gpt conversation with ORM django
class Conversation(models.Model):
    """
    Reprezentuje pojedynczą sesję rozmowy powiązaną z sesją Django.
    """
    # Zamiast ForeignKey do User, używamy klucza sesji
    id = models.UUIDField(  # Zmieniamy na UUID
        primary_key=True,
        default=uuid.uuid4,  # Automatycznie generuj UUID
        editable=False
    )
    #
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Tytuł rozmowy (np. skrócony pierwszy prompt)"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rozmowa (Sesja)"
        verbose_name_plural = "Rozmowy (Sesje)"

    def __str__(self):
        truncated_title = Truncator(self.title).chars(50)
        return f"Rozmowa {self.id} - {truncated_title or '[Brak tytułu]'}"

    def save(self, *args, **kwargs):
        # Opcjonalnie: Automatycznie ustaw tytuł na podstawie pierwszej wiadomości
        # Można to zrobić w widoku po zapisaniu pierwszej wiadomości.
        super().save(*args, **kwargs)

# Model Message pozostaje bez zmian
class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'Użytkownik'),
        ('assistant', 'Asystent'),
    ]
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Wiadomość"
        verbose_name_plural = "Wiadomości"

    def __str__(self):
        return f"{self.get_role_display()} ({self.conversation_id}): {Truncator(self.content).chars(50)}"

        # Dodajmy metodę do formatowania czasu dla szablonu/API

    def get_formatted_timestamp(self, format="%H:%M"):
        return self.timestamp.strftime(format)