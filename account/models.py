from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('Usuario requiere un correo')
        if not username:
            raise ValueError('Usuario debe tener un nombre de usuario')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            password = password,
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


# Borrar, es para Mesas de FoodTruck App
# https://stackoverflow.com/questions/11278074/how-do-i-display-django-model-choice-list-in-a-template
# https://docs.djangoproject.com/en/5.0/ref/forms/widgets/
# https://stackoverflow.com/questions/15393134/django-how-can-i-create-a-multiple-select-form

STATESMX = ( # Por checar o borrar / Debe ser una tupla para el parámetro 'choices'
    ('Puebla', 'Puebla'),
    ('CDMX', 'CDMX'),
)


class Account(AbstractBaseUser):
    first_name = models.CharField('Nombre(s)', max_length=50)
    last_name = models.CharField('Apellidos', max_length=50)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField('Email', max_length=100, unique=True)
    phone = models.CharField('Teléfono', max_length=50)
    city = models.CharField('Ciudad', max_length=50, default="")
    state = models.CharField('Estado', max_length=50, default="")
    country = models.CharField('Pais', max_length=50, default="")
    #addresses = models.ManyToManyField(Address, verbose_name='Direcciones', blank=True)

    # requeridos
    joined_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager() # la clase del modelo que declaramos al inicio 

    class Meta:
        verbose_name = 'cuenta de usuario'
        verbose_name_plural = 'cuentas de usuario'
    
    def full_name(self): #https://stackoverflow.com/questions/2892999/verbose-name-for-a-models-method
        return f"{self.first_name} {self.last_name}"
    
    full_name.short_description = 'Usuario'

    def basic_address(self):
        return f"{self.city} {self.state}"   
    
    def __str__(self):
        return f"{self.username} - {self.email}"
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    #models.PhoneNumberField(_(""))
    #models.EmailField(_(""), max_length=254)

class UserProfile(models.Model):
    user = models.OneToOneField(Account, verbose_name="Usuario", on_delete=models.CASCADE)
    # use 'addresses' field of 'user' instead of line_address_, etc
    picture = models.ImageField("Foto de Perfil", blank=True, upload_to='user_profile') # dentro del directorio de media en raíz del proyecto

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return self.user.first_name
    
class Address(models.Model):
    user = models.ForeignKey(Account, verbose_name="Usuario", on_delete=models.CASCADE)
    address_line_1 = models.CharField("Direccion", max_length=50)
    address_line_2 = models.CharField("Colonia", max_length=50, blank=True)
    city = models.CharField('Ciudad', max_length=50)
    state = models.CharField('Estado', max_length=50)
    country = models.CharField('Pais', max_length=50, default="México")
    zipcode = models.CharField('CP', max_length=6, default="")
    phone = models.CharField('Telefono',max_length=50)
    nearby = models.CharField("Referencia", max_length=100, blank=True)
    default = models.BooleanField('Preferida', default=False)
    is_active = models.BooleanField('Acitva', default=True)    
    created_at = models.DateTimeField('Creada el', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizada el', auto_now=True)
    

    class Meta:
        verbose_name = 'Direccion'
        verbose_name_plural = 'Direcciones'
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}" 
    
    def __str__(self):
        return f"{self.address_line_1} - {self.city}"