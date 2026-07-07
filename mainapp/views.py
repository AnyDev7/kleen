from django.shortcuts import HttpResponse, render,redirect
from store.models import Product, Rating
from kart.settings import COMPANY, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from account.models import Account
from account.views import dashboard, logout
from treasury.models import CashRegister
from treasury.views import check_cr

#from account.views import addresses
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='login')
def home(request):
    cashregisters = None
    cashr_count = 0
    
    # aqui va la lógica de corte de caja anterior abierto o cerrado
    #Regresa: 'previous_cr' instancia de último cashcut abierto, 'status' su estado, cashregister el id de la caja 'Ocupada'
    previous_cr, status, cashregister = check_cr(request)
    print(f'Previous_cr:{previous_cr}, estatus:{status}, cashregister:{cashregister}')

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
        try:
            cashregisters = CashRegister.objects.filter(status="Activa") #.order_by('name')
            cashr_count = cashregisters.count()
        except CashRegister.DoesNotExist:
            cashregisters = False
            messages.warning(request, 'No existen cajas activas. En home()')
            return redirect('logout')
        if cashr_count > 0:
            context = {
                'cashregisters': cashregisters,
                'COMPANY': COMPANY,
                'COMPANY_BANN1': COMPANY_BANN1,
                'COMPANY_BANN2': COMPANY_BANN2,
                'COMPANY_BANN3': COMPANY_BANN3,
                'COMPANY_SLOGAN': COMPANY_SLOGAN,
                'COMPANY_SLOG_SUB1': COMPANY_SLOG_SUB1,
                'COMPANY_SLOG_SUB2': COMPANY_SLOG_SUB2,
                }
        else:
            messages.warning(request, 'No hay cajas activas disponibles.')
            return redirect('logout')        
        return render(request, 'treasury/cashcut_open.html', context) # 'treasury' subdirectorio en 'templates'
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