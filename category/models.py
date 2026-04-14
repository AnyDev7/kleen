from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name = models.CharField("Nombre", max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    desc = models.TextField("Descripción", max_length=255, blank=True)
    image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def get_url(self):
        return reverse('prod_by_cat', args=[None,self.slug,"c"])
    
    def __str__(self):
        return self.name
    
    

class SubCategory(models.Model):
    name = models.CharField("Nombre", max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    desc = models.TextField("Descripción", max_length=255, blank=True)
    image = models.ImageField("Imagenes", upload_to='photos/subcategories', blank=True)
    category = models.ForeignKey(Category, verbose_name="Categoria", on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'subcategoria'
        verbose_name_plural = 'subcategorias'

    def get_url(self):
        return reverse('prod_by_cat', args=[self.slug,None,"s"]) # Solo funciona para el filtrado por subcategoria

    def __str__(self):
        return self.name

"""
    1o. Crear clase de Modelo
    2o. Agregar el modelo al panel admin, en admin.py de la app
    3o. Crear las migraciones: py manage.py makemigrations
        3.5 Ver la instrucciones SQL generadas, no es obligatorio: py manage.py sqlmigrate category 0001
    4o. Migrar a SQL: py manage.py migrate

"""