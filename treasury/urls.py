from django.urls import path
from treasury import views

urlpatterns = [
    path('initial-cr/',views.initial_cr, name='initial_cr'),
    path('cash-cut/', views.cash_cut, name='cash_cut'),
    #Claude 26Jun 2026
    path('cash-cut/<int:cut_id>/', views.cash_cut, name='cash_cut_detail'),
    path('cash-movement/', views.cash_movement, name='cash_movement'),
    #
    path('my-cashcuts/',views.my_cashcuts, name='my_cashcuts'),
    path('cashcut-detail/<int:cashcut_id>/',views.cashcut_detail, name='cashcut_detail'),
]