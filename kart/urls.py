"""
URL configuration for kart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import mainapp.views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('avipork_adm/', admin.site.urls), #cambiar nombre al url default de 'admin'
    path('', mainapp.views.home),
    path('home/', mainapp.views.home, name='home'),
    path('store/', include('store.urls') ),
    path('ecart/', include('ecart.urls')),
    path('', include('todo.urls')),
    path('account/', include('account.urls')),
    path('order/', include('order.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejo de erores 404 y 500 desde urls.py basada en funciones y vistas basadas en clases
# https://youtu.be/cE66WnX8Euo?si=r4M8c_BoxsbjXLFi

# Cambiar titulos del panel Admin
admin.site.site_header = "AP Equipos Panel Admin | powered by ▲▼anyDev7"
admin.site.site_title = "▲▼anyDev7"
admin.site.index_title = "Admin sitio"