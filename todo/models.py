from django.db import models

from account.models import Account

# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(Account, verbose_name="Usuario", on_delete=models.CASCADE, null=True)
    name = models.CharField("Tarea", max_length=50)
    task = models.CharField("Descripción", max_length=250)
    is_completed = models.BooleanField("¿Terminada?", default=False)
    deadline = models.DateTimeField("Fecha límite")
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)
    post_action = models.CharField("Seguimiento", max_length=250, blank=True)

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self): #en lugar de regresare un objeto, da un texto del registro
        return f"{self.name} | limite -> {self.deadline}"
    