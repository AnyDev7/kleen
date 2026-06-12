from django.urls import path
from treasury import views

urlpatterns = [
    path('initial-cr/',views.initial_cr, name='initial_cr'),
    path('cr-close/',views.cr_close, name='cr_close'),
]