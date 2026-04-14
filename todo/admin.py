from django.contrib import admin
from todo.models import Task

# Register your models here.

# esta clase se sobrepone overrides '__str__'
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_completed', 'deadline', 'updated_at')
    search_fields = ('name', 'task',)

admin.site.register(Task, TaskAdmin)