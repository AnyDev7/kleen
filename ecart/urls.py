from django.urls import path
from ecart import views



urlpatterns = [
    path('', views.ecart, name="ecart"),
    path('create-menu/', views.create_menu, name="create_menu"),
    path('add-prod/<int:product_id>/<int:flag>/', views.add_prod, name="add_prod"),
    path('remove-item/<int:product_id>/<int:cart_item_id>/', views.remove_item, name="remove_item"),
    path('minus-add-to-prod/<int:product_id>/<int:cart_item_id>/<int:flag>/', views.minus_add_to_prod, name="minus_add_to_prod"),
    path('select-customer/<str:total>/<str:flag>/', views.select_customer, name="select_customer"),
    path('select-address/<str:total>/<str:flag>/', views.select_address, name="select_address"),
    path('checkout/', views.checkout, name="checkout"),
]

