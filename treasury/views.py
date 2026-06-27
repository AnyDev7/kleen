from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from kart.settings import COMPANY, COMPANY_LOGO, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from .models import CashCut
from order.models import Payment
from ecart.views import create_menu


# Create your views here.

def check_cr(request):
    try:
        # Verificar si hay corte no cerrado, devuelve el último corte sin cerrar
        cr_opened = CashCut.objects.last()
        #last_cashcut = CashCut.objects.last()
        #last_cashcut1 = CashCut.objects.order_by('-start_at').first()
        #last_cashcut2 = CashCut.objects.latest('start_at')
        if not cr_opened:
            #No hay registros, BD nueva
            return False, False
        if cr_opened.status == "Cerrado":
            #Corte anterior cerrado
            return cr_opened, "Cerrado"
        elif cr_opened.status == "Iniciado":
            #El corte anterior NO estaba cerrado
            return cr_opened, "Iniciado"
    except Exception as e:
            print("Error capturado:", e)
            redirect ('home')


def initial_cr(request):
    if request.method == 'POST':
        #Obtener datos del request POST
        initial = float(request.POST.get('initial')) 
        try:
            cr_new = CashCut()
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


def cash_cut(request, cut_id=None):
    total_balance= total_cash= total_transfer= total_card= total_collect= total_sales = 0

    try:
        if request.GET.get('ticket') != '1':
            #Obtener datos del corte abierto, del usuario actual
            #Claude 26Jun 2026
            last_cr = CashCut.objects.filter(user=request.user, status="Iniciado").latest('start_at')
            #Obtener pagos realizados en el periodo de ese corte
            payments_cr = Payment.objects.filter(created_at__gte=last_cr.start_at, user_id = request.user.id)
            #print(f"Corte abierto: {last_cr}, pagos dentro del corte: {payments_cr}")
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
                last_cr.outcomes = 0  #por desarrollar función de entradas y salidas
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
                print(f'Estatus del corte: {last_cr.status}')
                messages.info(request, f'Estatus del corte: {last_cr.status}')
            else:
                if last_cr.status == "Cerrado" or not last_cr:
                    messages.info(request, f"No hay corte abierto para procesar. Saliendo...  Entre para crear nuevo corte.")
                    return redirect('logout')
                elif not payments_cr:
                    messages.info(request, f"No hay pagos ni ingresos para procesar.")
                    #Agregar: Validar  si desea hacer el corte en ceros.
                
                return redirect('dashboard')
        else:
            #Claude 26Jun 2026
            if cut_id:
                last_cr = get_object_or_404(CashCut, id=cut_id)
            else:
                last_cr = CashCut.objects.filter(user=request.user).latest('start_at')
                    
    except Exception as e:
        #print("Error capturado:", e)
        messages.warning(request, f"Error capturado: {e}")
        return redirect('dashboard')
    context = {
        'last_cr': last_cr,
        'total_cash': last_cr.initial_balance + last_cr.cash_balance,
        'COMPANY_LOGO': COMPANY_LOGO
    }
    if request.GET.get('ticket') == '1':
        return render(request, 'treasury/ticket_cashcut.html', context)
    return render(request, 'treasury/cashcut.html', context) # 'treasury' subdirectorio en 'templates' de mainapp


def my_cashcuts(request):

    try:
        cashcuts = CashCut.objects.order_by('-start_at').filter(user_id = request.user.id)
        # Unir o sumar queryset's : https://stackoverflow.com/questions/29587382/how-to-add-an-model-instance-to-a-django-queryset
        #orderproducts = OrderProduct.objects.filter(user__id=request.user.id, ordered=True)
        context = {
            'cashcuts': cashcuts,
            #'orderproducts': orderproducts,
        }
    except Exception as e:
        print("Error capturado:", e)
        messages.warning(request, f"Error capturado MIS CORTES: {e}")
        return redirect('dashboard')
    return render(request, "treasury/my_cashcuts.html", context)


@login_required(login_url='login')
def cashcut_detail(request, cashcut_id):
    cashcut = get_object_or_404(CashCut, id=cashcut_id)
    #ordered_products = OrderProduct.objects.filter(order__id=order_id) # order__id: doble 'underscore' para accesar al campo de foreignkey
    context = {
        'cashcut': cashcut,
        'COMPANY_LOGO': COMPANY_LOGO,
    }
    return render(request, 'treasury/cashcut_detail.html', context)