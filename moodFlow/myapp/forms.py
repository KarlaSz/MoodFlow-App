from django import forms
from .models import Task, Transaction, Category
from django.utils import timezone


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "comment", "url", "mood_choice", "status"]  # fields inside form

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Wpisz tytuł zadania"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dodatkowe uwagi"}),
            "url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Dodaj opcjonalny link"}),
            "mood_choice": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

class ChatForm(forms.Form):
    prompt = forms.CharField(label="Prompt", widget=forms.Textarea(attrs={"class": "form-control",
                                                                           "placeholder": "Napisz coś i rozmawiaj...",
                                                                           "id": "prompt",
                                                                             "rows":2,
                                                                    }))

class TransactionForm(forms.ModelForm):
    # Dynamicznie filtrujemy kategorie w widoku
    category = forms.ModelChoiceField(queryset=Category.objects.none(), label="Kategoria", required=True)
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Kwota",
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),  # Dodaj step i placeholder
        required=True
    )
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'np. Zakupy w Biedronce'}),
                                  label="Opis (opcjonalnie)", required=False)
    date = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'RRRR-MM-DD'}),
        initial=timezone.now().date(),  # Initial może zostać
        label="Data (RRRR-MM-DD)",  # Zaktualizuj etykietę
        input_formats=['%Y-%m-%d'],  # Powiedz Django, jakiego formatu oczekuje
        required=True
    )

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'date']
        labels = {
            'amount': 'Kwota',
            'description': 'Opis (opcjonalnie)',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'np. Zakupy w Biedronce'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Pobieramy użytkownika przekazanego z widoku
        transaction_type = kwargs.pop('transaction_type', None) # Pobieramy typ ('income'/'expense')
        super().__init__(*args, **kwargs)

        if user and transaction_type:
            # Filtrujemy queryset kategorii dla danego użytkownika i typu transakcji
            self.fields['category'].queryset = Category.objects.filter(user=user, type=transaction_type)
            self.fields['category'].empty_label = "Wybierz kategorię..." # Domyślny tekst
        else:
             # Jeśli brak użytkownika/typu, queryset pozostaje pusty, ale zapobiega to błędowi
             self.fields['category'].queryset = Category.objects.none()
             self.fields['category'].disabled = True # Opcjonalnie można wyłączyć pole