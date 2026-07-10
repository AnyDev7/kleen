from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from kart.settings import COMPANY, COMPANY_LOGO, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from .models import CashCut, CashRegister, CashMovement
from order.models import Payment
from ecart.views import create_menu


# Create your views here.

def check_cr(request):
    try:
        cropened_count = 0
        # Verificar si hay cortes Iniciados
        # Obtener los cortes iniciados del usuario actual, seleccionar el último.
            #last_cashcut = CashCut.objects.last()
            #last_cashcut1 = CashCut.objects.order_by('-start_at').first()
            #last_cashcut2 = CashCut.objects.latest('start_at')
        cr_opened = CashCut.objects.filter(user_id=request.user.id, status="Iniciado").last()
        if not cr_opened:
            #No hay registros, BD nueva
            return False, False, False
        if cr_opened.status == "Cerrado" or cr_opened.status == "Iniciado":
            #Corte anterior cerrado
            return cr_opened, cr_opened.status, cr_opened.cashregister_id
        else:
            return False, False, False
        #elif cr_opened.status == "Iniciado":
            #El corte anterior NO estaba cerrado
        #    return cr_opened, cr_opened.status, cr_opened.cashregister_id
    except Exception as e:
            messages.warning(request, f"Error capturado, en check_cr: {e}")
            redirect ('logout')


def initial_cr(request):
    if request.method == 'POST':
        #Obtener datos del request POST
        initial = float(request.POST.get('initial'))
        cr_select = int(request.POST.get('cr_selected'))
        #print(f'CR_SELECT de <select> desde POST : {cr_select}')
        try:
            cr_new = CashCut()
            cr_selected=CashRegister.objects.get(id=cr_select)
            cr_new.user_id = request.user.id 
            #ForeignKey: en cr_new.user_id, _id se refiere al campo foreignkey de la relación = id del modelo Account
            cr_new.initial_balance = initial
            #print(f"Saldo inicial :{cr_new.initial_balance}")
            cr_new.cashregister = cr_selected
            cr_new.save()
            cr_selected.status = "Ocupada"
            cr_selected.save()
            #print(f"Se creo nuevo corte:{cr_new}")
        except Exception as e:
            #print("Error capturado:", e)
            messages.warning(request, f"Error capturado, en initial_cr: {e}")
            return redirect('logout')
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


@login_required
def cash_movement(request):
    # Buscar el corte activo del usuario actual
    try:
        active_cut = CashCut.objects.get(user=request.user, status='Iniciado')
    except CashCut.DoesNotExist:
        messages.warning(request, 'No hay un corte de caja abierto para registrar movimientos.')
        return redirect('dashboard')

    if request.method == 'POST':
        movement_type = request.POST.get('movement_type')
        amount = request.POST.get('amount')
        concept = request.POST.get('concept')

        try:
            amount = abs(float(amount))
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.warning(request, 'Importe inválido.')
            return redirect('cash_movement')

        CashMovement.objects.create(
            cash_cut=active_cut,
            user=request.user,
            movement_type=movement_type,
            amount=amount,
            concept=concept
        )
        messages.success(request, f'Movimiento registrado: {movement_type} ${amount:.2f} - {concept}')
        return redirect('cash_movement')

    # Movimientos del corte activo
    movements = CashMovement.objects.filter(cash_cut=active_cut).order_by('-created_at')
    total_in  = sum(m.amount for m in movements if m.movement_type == 'IN')
    total_out = sum(m.amount for m in movements if m.movement_type == 'OUT')

    context = {
        'active_cut': active_cut,
        'movements': movements,
        'total_in': total_in,
        'total_out': total_out,
        'COMPANY_LOGO': COMPANY_LOGO  # quita esta línea si no usas la variable global
    }
    return render(request, 'treasury/cash_movement.html', context)


def cash_cut(request, cut_id=None):
    total_balance= total_cash= total_transfer= total_card= total_collect= total_sales = 0

    try:
        if request.GET.get('ticket') != '1':
            #Obtener datos del corte abierto, del usuario actual
            #Claude 26Jun 2026
            last_cr = CashCut.objects.filter(user=request.user, status="Iniciado").latest('start_at')
            #Obtener pagos realizados en el periodo de ese corte, por el usuario actual
            payments_cr = Payment.objects.filter(paid_at__gte=last_cr.start_at, user_id = request.user.id)
            #print(f"Corte abierto: {last_cr}, pagos dentro del corte: {payments_cr}")
            # Sumatoria de movimientos del corte
            #Obtener entradas y salidas de efectivo, y sus totales
            movements = CashMovement.objects.filter(cash_cut=last_cr)
            total_movements_in  = sum(m.amount for m in movements if m.movement_type == 'IN')
            total_movements_out = sum(m.amount for m in movements if m.movement_type == 'OUT')
            
            #Sumar saldos en caja
            if payments_cr and last_cr and last_cr.status == "Iniciado":
                cashregister = CashRegister.objects.get(id=last_cr.cashregister_id)
                #cashregister = get_object_or_404(CashCut, id=last_cr.cashregister_id)
                #Procesar pagos, entradas y salidas.
                for pay in payments_cr:
                    if pay.status == "Completado":
                        total_balance += pay.amount_paid
                        if pay.payment_method == "Efectivo":
                            total_cash += pay.amount_paid
                        elif pay.payment_method == "Transferencia":
                            total_transfer += pay.amount_paid
                        elif pay.payment_method == "Paypal":
                            total_card += pay.amount_paid
                        
                        # No se desglosan de total_balance, porque ya están 
                        # considerados en cada tipo de pago.
                        if pay.collect:
                            total_collect += pay.amount_paid
                        else:
                            total_sales += pay.amount_paid

                #Actualizar el corte y cerrarlo
                last_cr.incomes = total_balance + total_movements_in
                last_cr.outcomes = total_movements_out  
                last_cr.cash_balance = total_cash
                last_cr.transfer_balance = total_transfer
                last_cr.card_balance = total_card
                # total_collect y total_sales no se desglosan
                # en la impresión, porque ya están incluidos
                last_cr.collect_balance = total_collect
                last_cr.sales = total_sales
                last_cr.end_at = datetime.now()
                #Si usas datetime.now() puro, puede ser naive queda en horario UTC (del servidor)
                # y causar confusión → mejor usar timezone.now() en Django de tu TIME_ZONE.
                last_cr.save()
                last_cr.final_balance = last_cr.initial_balance + last_cr.incomes - last_cr.outcomes
                last_cr.total_cash = last_cr.initial_balance + last_cr.cash_balance + total_movements_in - total_movements_out
                last_cr.status = "Cerrado"
                last_cr.save()
                cashregister.status = "Activa"
                cashregister.save()
                #print(f'Estatus del corte: {last_cr.status}')
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
            #Claude 26Jun 2026, cargar el corte cut_id, para imprimir el corte
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
        'movements_in': last_cr.incomes - total_balance,
        'COMPANY_LOGO': COMPANY_LOGO
    }
    if request.GET.get('ticket') == '1': #imprimir el ticket
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
    movements_in = 0
    if cashcut.incomes > 0:
        movements_in = cashcut.incomes - cashcut.cash_balance - cashcut.transfer_balance - cashcut.card_balance
    context = {
        'cashcut': cashcut,
        'movements_in': movements_in,
        'COMPANY_LOGO': COMPANY_LOGO
    }
    return render(request, 'treasury/cashcut_detail.html', context)