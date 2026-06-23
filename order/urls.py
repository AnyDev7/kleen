from django.urls import include, path
from . import views

urlpatterns = [
    path('place-order/<str:delivery>/<str:order_note>/<int:address_id>/', views.place_order, name="place_order"),
    path('payment-deferred/',views.payment_deferred,name="payment_deferred"),
    path('payment-cash/<int:collect>', views.payment_cash, name="payment_cash"),
    path('payment/', views.payment, name="payment"),
    path('order-complete/', views.order_complete, name="order_complete"),
]
