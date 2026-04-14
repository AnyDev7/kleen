from django.shortcuts import HttpResponse, render,redirect
from store.models import Product, Rating
from ecart.views import create_menu

#from account.views import addresses
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    
    
    return render(request, 'mainapp/create_menu.html') # 'mainapp' subdirectorio en 'templates'





#Código original para cargar la página de inicio con productos

#    try:
#        products = Product.objects.all().filter(is_available=True).order_by('-has_discount', '-created_at')
#        for product in products:
#            ratings = Rating.objects.filter(product_id=product.id, status=True)
#    except:
#        None
#    context = {
#        'title': "Lavanderia Servicios & Productos",
#        'products': products,
#        'ratings': ratings,
#    }
#    return render(request, 'mainapp/home.html', context) # 'mainapp' subdirectorio en 'templates'