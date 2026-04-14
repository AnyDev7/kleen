from django.db import models
from category.models import Category, SubCategory
from django.urls import reverse


# Create your models here.

# Modelo original del curso

# Conectar el Manager a través del campo "objects" del modelo.
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choices = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    variation_category = models.CharField(max_length=50, choices=variation_category_choices)
    variation_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()
    
    class Meta:
        verbose_name = 'Catálago de variacion'
        verbose_name_plural = 'Catálago de variaciones'

    def __unicode__(self): # si se devuelve un objeto, debe ser 'unicode' en lugar de 'str'
        return self.product
    

class Product(models.Model):
    name = models.CharField('Nombre prod', max_length=200, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    brand = models.CharField('Marca', max_length=200, blank=True)
    description = models.TextField('Descripción', max_length=500, blank=True)
    data_sheet = models.TextField('Ficha técnica', max_length=1500, blank=True)
    price = models.FloatField('Precio', blank=True)
    stock = models.IntegerField('Existencias', blank=True)
    variations = models.ManyToManyField(Variation, blank=True)
    tax = models.FloatField('Impuesto', blank=True,default=0.02)
    is_available = models.BooleanField('Disponible', default=True)

    has_discount = models.BooleanField('¿Descuento?', default=False)
    discount = models.FloatField(blank=True, null=True)
    low_price = models.FloatField(blank=True, default=0)
    start_by = models.DateTimeField(blank=True, null=True)
    end_by = models.DateTimeField(blank=True, null=True)

    image1 = models.ImageField(upload_to='photos/products', blank=True)
    image2 = models.ImageField(upload_to='photos/products', blank=True)
    image3 = models.ImageField(upload_to='photos/products', blank=True)
    image4 = models.ImageField(upload_to='photos/products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(SubCategory, blank=True)
    

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    def get_url(self):
        subcat = None
        sub = self.categories.first()
        try:
            #subcat = SubCategory.objects.filter(id=self.id) No funciona para todos los casos
            subcat = SubCategory.objects.get(name=sub)
        except Exception as e:
            raise e
                                        # se deben regresar 2 slug: subcategory y product
        return reverse('product_detail', args=[subcat.slug, self.slug]) 
        # Sí funciona return reverse('product_detail', args=['pollo-engorda', self.slug])
        # No funciona return reverse('product_detail', args=[self.category.slug, self.slug])
    
    
    def __str__(self):
        return f"{self.name} | {self.price} | {self.stock} | {self.is_available} | {self.has_discount}"
    
        
    
    #Termina PRODUCT


"""

class VarCat(models.Model):
    varcat = models.CharField(max_length=50)
    slug = models.CharField(max_length=100)    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Línea variacion'
        verbose_name_plural = 'Líneas de variaciones'
        
    def __str__(self):
        return self.varcat
    
class Variation(models.Model):
    variation = models.CharField('CatVariacion', max_length=50)
    slug = models.CharField(max_length=100)
    varcat = models.ForeignKey(VarCat, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Catálago de variacion'
        verbose_name_plural = 'Catálago de variaciones'

    def __str__(self):
        return self.variation


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    brand = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    data_sheet = models.TextField(max_length=1500, blank=True)
    price = models.FloatField(blank=True)
    stock = models.IntegerField(blank=True)
    stockvariations = models.ManyToManyField(Variation, through='StockVar', blank=True)
    tax = models.FloatField(blank=True,default=0.02)
    is_available = models.BooleanField(default=True)

    has_discount = models.BooleanField(default=False)
    discount = models.FloatField(blank=True, null=True)
    low_price = models.FloatField(blank=True, default=0)
    start_by = models.DateTimeField(blank=True, null=True)
    end_by = models.DateTimeField(blank=True, null=True)

    image1 = models.ImageField(upload_to='photos/products', blank=True)
    image2 = models.ImageField(upload_to='photos/products', blank=True)
    image3 = models.ImageField(upload_to='photos/products', blank=True)
    image4 = models.ImageField(upload_to='photos/products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(SubCategory, blank=True)
    

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    def get_url(self):
        subcat = None
        sub = self.categories.first()
        try:
            #subcat = SubCategory.objects.filter(id=self.id) No funciona para todos los casos
            subcat = SubCategory.objects.get(name=sub)
        except Exception as e:
            raise e
                                        # se deben regresar 2 slug: subcategory y product
        return reverse('product_detail', args=[subcat.slug, self.slug]) 
        # Sí funciona return reverse('product_detail', args=['pollo-engorda', self.slug])
        # No funciona return reverse('product_detail', args=[self.category.slug, self.slug])
    

    def __str__(self):
        return f"{self.name} | {self.price} | {self.stock} | {self.is_available} | {self.has_discount}"

        

    #Termina PRODUCT


class StockVar(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, blank=True, null=True)
    value = models.CharField('Valor de la variacion',max_length=50)
    stock = models.IntegerField('existencia', blank=True)
    
    class Meta:
        verbose_name = 'Existencia por variación'
        verbose_name_plural = 'Existencias por variación'
    
    def __str__(self):
        return f"{self.id} {self.product.name} + {self.variation.variation}"
    
"""

    # *****  OJO  *****
    # Todo sobre Many-to-Many relationships
    # https://docs.djangoproject.com/en/5.0/topics/db/examples/many_to_many/  
        