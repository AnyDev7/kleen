from django.shortcuts import HttpResponse, render,redirect
from store.models import Product, Rating
from kart.settings import COMPANY, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from account.models import Account
from account.views import dashboard, logout
from treasury.models import CashCut
from treasury.views import check_cr

#from account.views import addresses
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='login')
def home(request):
    context = {
               'COMPANY': COMPANY,
               'COMPANY_BANN1': COMPANY_BANN1,
               'COMPANY_BANN2': COMPANY_BANN2,
               'COMPANY_BANN3': COMPANY_BANN3,
               'COMPANY_SLOGAN': COMPANY_SLOGAN,
               'COMPANY_SLOG_SUB1': COMPANY_SLOG_SUB1,
               'COMPANY_SLOG_SUB2': COMPANY_SLOG_SUB2,
            }
    # aqui va la lógica de corte de caja anterior abierto o cerrado
    previous_cr, status = check_cr(request)
    #previous_cr contiene instancia de último cr_closing
    #status su estado

    if status == "Iniciado":
        #Si el corte está abierto y es el mismo usuario logeado
        if  previous_cr.user_id == request.user.id:
            return dashboard(request)
        else:
        # Si no es el mismo usuario abrir sesión con usuario de corte abierto
            messages.warning(request, f'Corte abierto del usuario: {previous_cr.user.first_name} {previous_cr.user.last_name}, inicie sesión con ese usuario: {previous_cr.user.username}.')
            #Debía ser login pero se salta la verificación y nos envía directo a dashboard
            return logout(request)
    elif status == False or status == "Cerrado":
        #crear un corte
        messages.info(request, f'Crear nuevo corte del usuario:  {request.user.username}.')
        return render(request, 'treasury/cr_open.html', context) # 'treasury' subdirectorio en 'templates'
    else:
        return redirect('home')

    
    #return render(request, 'mainapp/create_menu.html', context) # 'mainapp' subdirectorio en 'templates'



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