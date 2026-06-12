from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from kart.settings import COMPANY, COMPANY_LOGO, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from .models import CRClosing
from order.models import Payment
from ecart.views import create_menu


# Create your views here.

def check_cr(request):
    try:
        # Verificar si hay corte no cerrado, devuelve el último corte sin cerrar
        cr_opened = CRClosing.objects.last()
        #last_crclosing = CRClosing.objects.last()
        #last_crclosing1 = CRClosing.objects.order_by('-start_at').first()
        #last_crclosing2 = CRClosing.objects.latest('start_at')
        if not cr_opened:
            print(f"No hay registros, BD nueva")
            return False, False
        
        if cr_opened.status == "Cerrado":
            print(f"Corte anterior cerrado: {cr_opened}")
            return cr_opened, "Cerrado"
        elif cr_opened.status == "Iniciado":
            print(f"El corte anterior NO estaba cerrado 'cr_opened': {cr_opened}")
            return cr_opened, "Iniciado"
    except Exception as e:
            print("Error capturado:", e)
            redirect ('home')


def initial_cr(request):
    if request.method == 'POST':
        #Obtener datos del request POST
        initial = float(request.POST.get('initial')) 
        try:
            cr_new = CRClosing()
            cr_new.user_id = request.user.id 
            print(f"User id :{cr_new.user_id}")
            #ForeignKey en cr_new.user_id, _id se refiere al id del modelo Account
            cr_new.initial_balance = initial
            print(f"Saldo inicial :{cr_new.initial_balance}")
            cr_new.save()
            print(f"Se creo nuevo corte:{cr_new}")
        except Exception as e:
            print("Error capturado:", e)
    #create_menu(request)
    context = {
        'COMPANY': COMPANY,
        'COMPANY_BANN1': COMPANY_BANN1,
        'COMPANY_BANN2': COMPANY_BANN2,
        'COMPANY_BANN3': COMPANY_BANN3,
        'COMPANY_SLOGAN': COMPANY_SLOGAN,
        'COMPANY_SLOG_SUB1': COMPANY_SLOG_SUB1,
        'COMPANY_SLOG_SUB2': COMPANY_SLOG_SUB2,
            }
    return render(request, 'mainapp/create_menu.html', context) # 'mainapp' subdirectorio en 'templates'


def cr_close(request):
    total_balance= total_cash= total_transfer= total_card= total_collect= total_sales = 0

    try:
        #Obtener datos del corte abierto
        last_cr = CRClosing.objects.last()
        #Obtener pagos realizados durante ese corte
        payments_cr = Payment.objects.filter(created_at__gte=last_cr.start_at, user_id = request.user.id)
        print(f"Corte abierto: {last_cr}, pagos dentro del corte: {payments_cr}")
        #Sumar saldos en caja
        if payments_cr and last_cr and last_cr.status == "Iniciado":
            for pay in payments_cr:
                if pay.status == "Completado":
                    total_balance += pay.amount_paid
                    if pay.payment_method == "Efectivo":
                        total_cash += pay.amount_paid
                    elif pay.payment_method == "Transferencia":
                        total_transfer += pay.amount_paid
                    elif pay.payment_method == "Paypal":
                        total_card += pay.amount_paid
                    if pay.collect:
                        total_collect += pay.amount_paid
                    else:
                        total_sales += pay.amount_paid

            #Actualizar el corte y cerrarlo
            last_cr.incomes = total_balance
            last_cr.outcomes = 0
            last_cr.sales = total_sales
            last_cr.cash_balance = total_cash
            last_cr.transfer_balance = total_transfer
            last_cr.card_balance = total_card
            last_cr.collect_balance = total_collect
            last_cr.end_at = datetime.now()
            #Si usas datetime.now() puro, puede ser naive queda en horario UTC (del servidor)
            # y causar confusión → mejor usar timezone.now() en Django de tu TIME_ZONE.
            last_cr.save()
            last_cr.final_balance = last_cr.initial_balance + last_cr.incomes - last_cr.outcomes
            last_cr.total_cash = last_cr.initial_balance + last_cr.cash_balance
            last_cr.status = "Cerrado"
            last_cr.save()
        else:
            if last_cr.status == "Cerrado" or not last_cr:
                messages.info(request, f"No hay corte abierto para procesar.")
            elif not payments_cr:
                messages.info(request, f"No hay pagos ni ingresos para procesar.")
            
            return redirect('dashboard')
                    
    except Exception as e:
        print("Error capturado:", e)
        messages.warning(request, f"Error capturado: {e}")
        return redirect('dashboard')
    context = {
        'last_cr': last_cr,
        'total_cash': last_cr.initial_balance + last_cr.cash_balance,
        'COMPANY_LOGO': COMPANY_LOGO
    }
    return render(request, 'treasury/cr_close.html', context) # 'treasury' subdirectorio en 'templates'

def my_cr_closes(request):

    try:
        cr_closes = CRClosing.objects.order_by('-start_at').filter(user_id = request.user.id)
        # Unir o sumar queryset's : https://stackoverflow.com/questions/29587382/how-to-add-an-model-instance-to-a-django-queryset
        #orderproducts = OrderProduct.objects.filter(user__id=request.user.id, ordered=True)
        context = {
            'cr_closes': cr_closes,
            #'orderproducts': orderproducts,
        }
    except Exception as e:
        print("Error capturado:", e)
        messages.warning(request, f"Error capturado: {e}")
        return redirect('dashboard')
    return render(request, "treasury/my_cr_closes.html", context)