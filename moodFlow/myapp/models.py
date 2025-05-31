from django.db import models
from django.utils import timezone
from django.utils.text import Truncator # Do skracania tytułu
import uuid
from django.conf import settings
# from decimal import Decimal


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

TYPE_CHOICES = [
        ('expense', 'Wydatek'),
        ('income', 'Przychód'),
        ('saving', 'Oszczędność'),
    ]

class Task(models.Model):
    title = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    url = models.URLField(null=True, blank=True)
    mood_choice = models.CharField(choices=MOOD_CHOICES, max_length=20, default="neutral")
    status = models.CharField(choices=IDEA_STATUS, max_length=30, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Zadanie"
        verbose_name_plural = "Zadania w dzienniku"
        # ================================
        ordering = ['created_at']

    def __str__(self):
        return self.title


#DB for chat gpt conversation with ORM django
class Conversation(models.Model):
    """
    Reprezentuje pojedynczą sesję rozmowy powiązaną z sesją Django.
    """
    # Zamiast ForeignKey do User, używamy klucza sesji
    id = models.UUIDField(
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
        return self.title or f"Conversation {self.id}"

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

    def get_formatted_timestamp(self, format="%H:%M:%S"):
        """Zwraca sformatowany czas lokalny."""
        local_time = timezone.localtime(self.timestamp)
        # Używamy formatu przekazanego jako argument lub domyślnego "%H:%M:%S"
        return local_time.strftime(format)


    class Meta:
        ordering = ['timestamp']
        verbose_name = "Wiadomość"
        verbose_name_plural = "Wiadomości"

    def __str__(self):
        return f"{self.get_role_display()} ({self.conversation_id}): {Truncator(self.content).chars(50)}"

        # Dodajmy metodę do formatowania czasu dla szablonu/API




class Category(models.Model):
    """Kategoria przychodu lub wydatku."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_categories')
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Typ")

    class Meta:
        verbose_name = "Kategoria finansowa"
        verbose_name_plural = "Kategorie finansowe"
        unique_together = ('user', 'name') # Unikalna nazwa kategorii dla użytkownika

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(models.Model):
    """Pojedyncza transakcja finansowa (przychód lub wydatek)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name="Kategoria")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kwota")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Opis")
    date = models.DateField(default=timezone.now, verbose_name="Data transakcji")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dodajemy pole 'type' dla łatwiejszego filtrowania, chociaż można by je wywnioskować z kategorii
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Typ transakcji")

    class Meta:
        verbose_name = "Transakcja"
        verbose_name_plural = "Transakcje"
        ordering = ['-date', '-created_at'] # Najnowsze najpierw

    def __str__(self):
        prefix = "+" if self.type == 'income' else "-"
        return f"{prefix}{self.amount} zł ({self.date}) - {self.category.name if self.category else 'Bez kategorii'}"

    # Można dodać metodę do automatycznego ustawiania typu na podstawie kategorii, jeśli chcesz
    # def save(self, *args, **kwargs):
    #     if self.category:
    #         self.type = self.category.type
    #     super().save(*args, **kwargs)