from django.db import models

from account.models import Account
from order.models import Payment

# Create your models here.

class Cashier(models.Model):
    user = models.ForeignKey(Account, verbose_name='Cajero', on_delete=models.SET_NULL, null=True)
    name = models.CharField("Nombre", max_length=100)
    #city = models.CharField("Ciudad", max_length=50, blank=True)
    #state = models.CharField("Estado", max_length=50, blank=True)
    #phone = models.CharField("Telefono", max_length=15, blank=True)
    #email = models.EmailField("Correo", max_length=60, blank=True)
    amount_sales = models.FloatField("Total ventas", default=0)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = 'Cajero'
        verbose_name_plural = 'Cajeros'

    def __str__(self):
        return self.name
    

class CashRegister(models.Model):    
    STATUS = (
        ('Enabled', 'Activa'),
        ('Disabled', 'Inactiva'),
    )
    cr_name = models.CharField("Caja", max_length=20, default="Principal")
    status = models.CharField("Estatus", max_length=20, choices=STATUS, default="Activa")
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return self.cr_name
    

class CRClosing(models.Model):
    STATUS = (
        ('Started', 'Iniciado'),
        ('Closed', 'Cerrado'),
    )
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.SET_NULL, null=True)
    cashregister = models.ForeignKey(CashRegister, verbose_name='Caja', on_delete=models.SET_NULL, null=True, blank=True)
    #cashier = models.ForeignKey(Cashier, verbose_name='Cajero', on_delete=models.SET_NULL, null=True, blank=True)

    #number = models.CharField("Orden", max_length=20)
    
    initial_balance = models.FloatField("Saldo inicial")
    incomes = models.FloatField("Total ingresos", null=True)
    outcomes = models.FloatField("Total salidas", null=True)
    sales = models.FloatField("Total ventas", null=True)
    taxes = models.FloatField("Total impuestos", null=True)
    cash_balance = models.FloatField("Total efectivo", null=True)
    card_balance = models.FloatField("Total tarjetas", null=True)
    transfer_balance = models.FloatField("Total transferencias", null=True)
    collect_balance = models.FloatField("Total cobranza", null=True)
    final_balance = models.FloatField("Saldo final", null=True)
    status = models.CharField("Estatus", max_length=15, choices=STATUS, default="Iniciado")
    start_at = models.DateTimeField("Iniciado", auto_now_add=True)
    end_at = models.DateTimeField("Finalizado", auto_now=True)

    class Meta:
        verbose_name = 'Corte'
        verbose_name_plural = 'Cortes'
    
    """ Ver que se necesita de aqui
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    full_name.short_description = 'Usuario'
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"
    """
    def __str__(self):
        return str(self.id) + " " + self.status + " " + str(self.initial_balance)


class IncomeOutcome(models.Model):
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.SET_NULL, null=True)
    crclosing = models.ForeignKey(CRClosing, verbose_name='Corte', on_delete=models.SET_NULL, null=True)
    income = models.BooleanField('Entrada', default=False)
    outcome = models.BooleanField('Salida', default=False)
    amount = models.FloatField("Importe")
    concept = models.CharField("Concepto", max_length=50)
    
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Entrada y Salida'
        verbose_name_plural = 'Entradas y Salidas'
    
