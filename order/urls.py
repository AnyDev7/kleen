from django.urls import include, path
from . import views

urlpatterns = [
    path('place_order/<str:delivery>/<str:order_note>/<int:address_id>/', views.place_order, name="place_order"),
    path('payment/', views.payment, name="payment"),
    path('order_complete/', views.order_complete, name="order_complete"),
]
