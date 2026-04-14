from django.urls import path
from store import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/<str:cat_slug>/<str:flag>/', views.store, name='prod_by_cat'),
    #path('category/<slug:subcategory_slug>/', views.store, name='prod_by_subcat'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('rating/<int:product_id>/', views.rating, name="rating")
]