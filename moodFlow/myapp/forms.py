from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "comment", "url", "mood_choice", "status"]  # Pola, które będą w formularzu
        #
        # widgets = {
        #     "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Wpisz tytuł zadania"}),
        #     "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dodatkowe uwagi"}),
        #     "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Dodaj opcjonalny link"}),
        #     "mood_choice": forms.Select(attrs={"class": "form-select"}),  # Wybór nastroju
        #     "status": forms.Select(attrs={"class": "form-select"}),  # Wybór statusu
        # }
