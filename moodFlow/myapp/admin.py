from django.contrib import admin
from .models import Task, Transaction, Category
# Register your models here.
admin.site.register(Task)
admin.site.register(Transaction)
admin.site.register(Category)