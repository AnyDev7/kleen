from django.db import models

from account.models import Account
from store.models import Product, Variation, VarCat, StockVar
# Create your models here.

class Customer(models.Model):
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.SET_NULL, null=True)
    name = models.CharField("Nombre", max_length=100, unique=True)
    address_line_1 = models.CharField("Direccion", max_length=100, blank=True)
    address_line_2 = models.CharField("Colonia", max_length=50, blank=True)
    city = models.CharField("Ciudad", max_length=50, blank=True)
    state = models.CharField("Estado", max_length=50, blank=True)
    phone = models.CharField("Telefono", max_length=15, blank=True)
    email = models.EmailField("Correo", max_length=60, blank=True)
    amount_purchases = models.FloatField("Total compras", default=0)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name

class Payment(models.Model):
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.CASCADE)
    payment_id = models.CharField("Pago", max_length=100)
    payment_method = models.CharField("Método de Pago", max_length=100)
    amount_paid = models.CharField("Importe", max_length=100)
    currency = models.CharField("Moneda", max_length=4, default="MXN")
    status = models.CharField("Estatus", max_length=100)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('Recibida', 'Nueva'),
        ('Pagada', 'Pagada'),
        ('Aceptada', 'Aceptada'),
        ('Enviada', 'Enviada'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    )
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, verbose_name='Pago', on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, verbose_name='Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    number = models.CharField("Orden", max_length=20)
    first_name = models.CharField("Nombre", max_length=50)
    last_name = models.CharField("Apellidos", max_length=100)
    phone = models.CharField("Telefono", max_length=15)
    email = models.EmailField("Correo", max_length=50)
    address_line_1 = models.CharField("Direccion", max_length=50)
    address_line_2 = models.CharField("Colonia", max_length=50, blank=True)
    country = models.CharField('Pais', max_length=50)
    state = models.CharField('Estado', max_length=50)
    city = models.CharField('Ciudad', max_length=50)
    zipcode = models.CharField('CP', max_length=10)
    note = models.CharField("Notas", max_length=125, blank=True)
    sub_total = models.FloatField("Subtotal", default=0)
    ship_cost = models.FloatField("Envío", default=0)
    tax = models.FloatField("Impuestos")
    total = models.FloatField("Total")
    status = models.CharField("Estatus", max_length=15, choices=STATUS, default="Nueva")
    shipment = models.BooleanField("¿Enviar?", default=True)
    pickup = models.BooleanField("¿Retiro?", default=False)
    pickup_instructions = models.CharField('Comentarios para recolección', max_length=200, blank=True)
    ip = models.CharField("IP", max_length=20, blank=True)
    is_ordered = models.BooleanField("Ordenada", default=False)
    logistic_supp = models.CharField('Proveedor de logística', max_length=50, blank=True, default="")
    #logistic_supp = models.ForeignKey(Logistic, verbose_name='Proveedor de logística', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    full_name.short_description = 'Usuario'
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.first_name + " " + self.number
    

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name='Orden', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, verbose_name='Pago', on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, verbose_name='Usuario', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Producto', on_delete=models.CASCADE)
    #varcat = models.ForeignKey(VarCat, verbose_name='Catalogo Variacion', on_delete=models.CASCADE, blank=True)
    #variation = models.ForeignKey(Variation, verbose_name='Variacion', on_delete=models.CASCADE, blank=True)
    #value = models.CharField('Diferenciador', max_length=50, blank=True, null=True)   # ???
    variations = models.ManyToManyField(StockVar, verbose_name="Variaciones", blank=True)
    quantity = models.IntegerField('Cantidad')
    price = models.FloatField('Precio')
    ordered = models.BooleanField('Ordenado', default=False)
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = 'Producto por orden'
        verbose_name_plural = 'Productos por orden'

    def __str__(self):
        return self.product.name



# CHECAR 
"""
class OrderedVar(models.Model):  # ?????????
    order_product = models.ForeignKey(OrderProduct, verbose_name='Orden-Producto', on_delete=models.CASCADE, blank=True, null=True)
    #variation = models.ForeignKey(Variation, verbose_name='Variacion', on_delete=models.CASCADE, blank=True, null=True)
    variation = models.CharField('Variacion', max_length=50, default=None)
    value = models.CharField('Valor de la variacion', max_length=50, default=None)
    quantity = models.IntegerField('Pedido por variación', blank=True, default=None)
    price = models.IntegerField('Precio por variación', blank=True, default=None)
    
    class Meta:
        verbose_name = 'Ordenado por variación'
        verbose_name_plural = 'Ordenados por variación'
    
    
    def __str__(self):
        return f"{self.id} {self.variation} + {self.value} - {self.quantity} - {self.price}"
"""