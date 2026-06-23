from django.urls import path
from treasury import views

urlpatterns = [
    path('initial-cr/',views.initial_cr, name='initial_cr'),
    path('cr-close/',views.cr_close, name='cr_close'),
    path('my-cr-closes/',views.my_cr_closes, name='my_cr_closes'),
    path('crclose-detail/<int:cr_close_id>/',views.crclose_detail, name='crclose_detail'),
]