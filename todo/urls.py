from django.contrib import admin
from django.urls import path, include
from todo import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('todo', views.todo, name='todo'),
    # Las urls de:  include('mainapp.urls'))
    path('hecho/<int:task_id>', views.done_task, name='done-task'),
    path('nohecho/<int:task_id>', views.undone_task, name='undone-task'),
    path('crear-tarea/', views.add_task, name='add-task'),
    path('cambiar/<int:task_id>', views.edit_task, name='edit-task'),
    path('borrar/<int:task_id>', views.delete_task, name='delete-task'),
]

