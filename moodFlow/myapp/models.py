from django.db import models

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
