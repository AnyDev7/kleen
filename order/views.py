import json
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from urllib.parse import urlencode
from django.utils import timezone
from datetime import datetime

from ecart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct, Customer
from store.models import Product
from account.models import Address
from kart.settings import COMPANY, COMPANY_STREET, COMPANY_CITY, COMPANY_STATE, COMPANY_ZIP, COMPANY_COUNTRY, COMPANY_PHONE, COMPANY_LOGO

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_protect #CHECAR 15ABR2026


#Función para pagar ordenes cobradas desde "Mis Ordenes"  / NO PROGRAMADA
# Sustituye payment_deferred y manda a pagar a payment_kleen.html
# Por programar 20Jun2026 / NO PROGRAMADA: 7Jul 2026
def collect_pay(request):
    order = get_object_or_404(Order,user=current_user, number=order_number, is_ordered=False)
    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'ship_cost': ship_cost,
        'tax': tax,
        'g_total': g_total,
        'ship_total': ship_total,
        'delivery': delivery,
    }
    return render(request, 'order/payment_kleen.html', context)

#Función sólo para renderizar payment_kleen.html con los datos de la orden y el pago por liquidar.
#Pago desde consulta my_orders en account.views > my_orders.html
# enviar datos a payment_kleen.html > payment_cash() > order_complete() > order_complete.html
def payment_deferred(request):
    if "pay" in request.POST:
        order_number = request.POST.get("pay")
        #print(f"Order Number: 'order_number', Existe: {order_number}") # OK funciona
        try:
            order = Order.objects.get(number=order_number, is_ordered=True)
            #print(f"Pago ID: 'order.payment_id', Existe: {order.payment_id}") # OK funciona
            #order.payment_id - payment_id es el campo del foreign key (contiene el id)
            #print(f"Pago ID: 'order.payment.id', Existe: {order.payment.id}") # OK funciona
            #order.payment.id - payment es el modelo del campo del foreign key, .id= trae el id
 
            ordered_products = OrderProduct.objects.filter(order_id=order.id).exclude(quantity=0)
 
            context = {
                'order': order,
                'cart_items': ordered_products,
                'total': order.sub_total,
                'ship_cost': order.ship_cost,             
                'tax': order.tax,
                'g_total': order.total,
                'ship_total': order.ship_cost+order.sub_total,
                'delivery': order.logistic_supp,
                'collect': 1,
            }
            return render(request, 'order/payment_kleen.html', context)
        
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('my_orders')
    else:
        return redirect('my_orders')


@csrf_protect #CHECAR si es necesario: @csrf_protect  15Abr2026
def payment_cash(request, collect):
    if request.method == 'POST':
        #Obtener datos del request POST
        type_payment = request.POST.get('type_payment') # viene de option radio  name=type_payment cash or card
        payment_id = request.POST.get('payment_id')
        order_number = request.POST.get('order_number')
        payment_id = type_payment + order_number
        payment_method = 'Efectivo'
        if type_payment == 'transfer':
            payment_method = 'Transferencia'
        elif type_payment == 'paypal':
            payment_method = 'Paypal'
        
        #agregado 9 jul 2026, pagar ordenes de otros usuarios.
        # Corregir las query de order sin request.user  if collect == 1:
        try:
            if collect == 1: # Pago de Cobranza
                # obtener orden procesada y no pagada, y el pago pendiente.
                # Pagar orden de cualquier usuario 
                #order = Order.objects.get(user=request.user, number=order_number)
                #Checar si Payment almacena user, para poner request.user (actual)
                order = Order.objects.get(number=order_number)
                payment = Payment.objects.get(id=order.payment_id)
                payment.user = request.user
                payment.collect = True
                payment.status = "Completado"
                payment.payment_method = payment_method
                payment.paid_at = datetime.now()
                payment.save()
                order.paid_at = datetime.now()
            else: # Pago de nueva orden
                # obtener Orden no procesada y no pagada, crear el pago.
                order = get_object_or_404(Order, user=request.user, is_ordered=False, number=order_number)
                # store transaction data
                payment = Payment(
                    user = request.user,
                    payment_id = payment_id, #request.POST.get('payment_id'), #En el modelo Payment, payment_id no es un indice, almacena el id
                    payment_method = payment_method,
                    amount_paid = order.total,  #float(body['payment_amount']), #Order model: order.total
                    status = "Completado",
                )
                payment.save()
                order.payment = payment  # Foreign_key se asigna el objeto completo al campo ForeignKey
                order.is_ordered = True
            if "submit_cash" in request.POST: # Si la orden se pagó al momento
                order.status = "Pagada"
                order.paid_at = datetime.now() # NO usar datetime.now() - timezone.now() en lugar de datetime.now() porque respeta la configuración de TIME_ZONE y USE_TZ
                payment.paid_at = datetime.now() # # TIME_ZONE ya está definido, se usa= datetime.now() - Usar timezone.now() en lugar de datetime.now() Si no está configurado TIME_ZONE y USE_TZ
                payment.save()
                #print(f"Submit Cash: 'submit_cash', Existe:{request.POST}")
            elif "submit_deferred" in request.POST: #Pago de la orden diferido
                order.status = "No Pagada"
                order.paid_at = None
                payment.paid_at = None
                payment.payment_method = "Por Cobrar"
                payment.status = "Por Cobrar"
                payment.save()
                #print(f"Submit Deferred: 'submit_deferred', Existe:{request.POST}")
                #print(f"Payment Status: 'payment.status', Existe:{payment.status}")
                #print(f"Payment Status: 'order.paid_at', Existe:{order.paid_at}")
            
            order.save()
            if collect == 0:
                # Move cart items to OrderProduct table 
                cart_items = CartItem.objects.filter(user=request.user).exclude(quantity=0)
                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id #ForeignKey 
                    orderproduct.payment = payment #ForeignKey
                    orderproduct.user_id = request.user.id #ForeignKey 
                    orderproduct.product_id = item.product_id #ForeignKey 
                    orderproduct.quantity = item.quantity
                    orderproduct.price = item.price
                    orderproduct.ordered = True
                    orderproduct.save()

                    cart_item = CartItem.objects.get(id=item.id)
                    product_variations = cart_item.variations.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variations)
                    orderproduct.save()

                    # decrease o reduce quantity of sale product & variation
                    product = Product.objects.get(id=item.product_id)
                    product.stock -= item.quantity
                    product.save()  # Hasta aqui OK

                    # Decrease quantity of variation
                    for stockvar in product_variations:
                        stockvar.stock -= item.quantity
                        stockvar.save()
                
                # Clear Cart
                CartItem.objects.filter(user=request.user).delete()

                # Send Order recieved email to customer
                mail_subject = '¡Se generó una Orden nueva!'
                mail_message = render_to_string('order/order_recieved_email.html', {
                    'user': request.user,
                    'order': order,
                    'cart_items': cart_items,
                    'company': COMPANY,
                })
                to_email = request.user.email
                send_email = EmailMessage(mail_subject, mail_message, to=[to_email])
                send_email.send()

            #Agregado 20Jun 2026 Claude - JMBS, para imprimir regresa a:
            base_url = reverse('order_complete')
            params = urlencode({
                'order_number': order.number,
                'payment_id': payment.payment_id,
            })
            #print(f'Base_URL + params: {base_url}?{params}')
            #messages.info(request, f'Base_URL + params: {base_url}?{params}')
            return redirect(f'{base_url}?{params}')
            #Fin agregado 20Jun 2026

        except Exception as e:
            #Error al procesar pagos de ordenes de otro usuario: 
            #Error: No se registró su orden. En payment_cash Order matching query does not exist.
            print("Error capturado:", e)
            messages.error(request, f'No se registró su orden. En payment_cash {e}')
            return redirect('ecart')

        
        try:
            order = Order.objects.get(number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id).exclude(quantity=0)
            payment = Payment.objects.get(payment_id=payment_id)
            context = {
                'order': order,
                'ordered_products': ordered_products,
                'payment': payment,
                'COMPANY_LOGO': COMPANY_LOGO
            }
            #Agregado el 20Jun 2026 Claude code
            #if request.GET.get('ticket') == '1':
            #    return render(request, 'order/ticket_order.html', context)
            #Return modificado 20Jun 2026 - JMBS, se cambia por ridirect
            #Como en el script de payment: redirect_url = "{% url 'order_complete' %}"
            #window.location.href = redirect_url + '?order_number='+ data.order_number + '&payment_id=' + data.payment_id; //Sí funciona + '&status='+ data.status + '&date=' + data.date;
            return render(request, "order/order_complete.html", context)
            # Sí funciona si ponesmos argumentos en order_complete() return redirect('order_complete', order_number=order_number, payment_id=payment_id)
            # url absoluta o relativa: order-complete
            #return redirect(f'order-complete/?order_number={order_number}&payment_id={payment_id}')
            

        except Exception as e :
            print("Error capturado:", e)
            messages.error(request, f'No existe orden o pago. {e}')
            return redirect('ecart')
        #redirect('order_complete') comentado 20Abr 2026
        
    else:
        return redirect('ecart')


def payment(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        
        order = get_object_or_404(Order, user=request.user, is_ordered=False, number=body['orderID'])
        
        try:
            # store transaction data
            payment = Payment(
                user = request.user,
                payment_id = body['transID'],
                payment_method = body['payment_method'],
                amount_paid = order.total,  #float(body['payment_amount']), #Order model: order.total
                #currency = body['payment_currency'], # Aún no queda el POST en el script de payment.html
                status = body['status'],
            )
            payment.save()
            
            order.payment = payment  # Foreign_key se asigna el objeto completo al campo ForeignKey
            order.is_ordered = True
            order.status = "Pagada"
            order.paid_at = payment.created_at
            order.save()

            # Move cart items to OrderProduct table 
            cart_items = CartItem.objects.filter(user=request.user).exclude(quantity=0)
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.price = item.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variations = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variations)
                orderproduct.save()

                # decrease o reduce quantity of sale product & variation
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()  # Hasta aqui OK

                # Decrease quantity of variation
                for stockvar in product_variations:
                    stockvar.stock -= item.quantity
                    stockvar.save()
            
            # Clear Cart
            CartItem.objects.filter(user=request.user).delete()

            # Send Order recieved email to customer
            mail_subject = '¡Gracias por tu compra!'
            mail_message = render_to_string('order/order_recieved_email.html', {
                'user': request.user,
                'order': order,
                'cart_items': cart_items,
                'company': COMPANY,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, mail_message, to=[to_email])
            send_email.send()

            # Send order number and transaction id back to sendData method via JsonResponse
            data = {
                'order_number': order.number,
                'payment_id': payment.payment_id,
                #Sí funciona: 'status': order.status,
                #Sí funciona: 'date': order.created_at,
            }

        except:
            None

    return JsonResponse(data)


def place_order(request, delivery, order_note, customer_id=1, address_id=None, total=0, quantity=0):
    current_user = request.user
    cart_count = 0
    ship_cost = 99  # Crear tabla para tax y para ship_cost (por zonas por estados calcular tarifa)
    tax = 0 #Cálculo de impuestos: (2 * total)/100
    sub_total = 0
    g_total = 0
    address = None
    try:
        customer = Customer.objects.get(id=customer_id)
        #print("Cliente:", customer)
    except Exception as e:
        messages.error(request, f'No existe el cliente. place_order() {e}')
        return redirect('ecart')

    try:
        cart_items = CartItem.objects.filter(user=current_user).exclude(quantity=0)
        cart_count = cart_items.count()
    except Exception as e:
        print("Error capturado en place_order():", e)
        messages.error(request, f'No se registró su orden. place_order() {e}')
        return redirect('ecart')
    if cart_count <= 0:
        return redirect('ecart')
    
    if delivery == 'pickup':
        ship_cost = 0
        logistic_supp = 'pickup'
    elif delivery == 'ship':
        option = request.POST.get('shipment')  
        ship_cost = float(option.split("-")[0]) # Costo del envío
        logistic_supp = option.split("-")[1] # Proveedor de logística
    else:
        ship_cost = 0
        logistic_supp = 'pickup'

        """
        #Obtener dirección del cliente si delivery== 'ship'
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return redirect('store')
        """
    
    for cart_item in cart_items:
        cart_price = 0
        # Aqui se puede verificar si el precio sigue siendo de promocion.
        sub_total = cart_item.sub_total() 
        #sub_total() verifica precio de promoción del model CartItem de ecart
        total +=  sub_total  # Total de productos
        quantity += cart_item.quantity
        # Aqui se puede verificar si el precio sigue siendo de promocion.
        cart_price = cart_item.cartitem_price() 
        #cartitem_price() verifica precio de promoción del model CartItem de ecart
        cart_item.price = cart_price
        cart_item.save()

    
    ship_total = total + ship_cost
    g_total = ship_total + tax # debería ser si se cobran impuestos: g_total = ship_total + tax

    if request.method == 'POST':
        """
        # Borrar: Cómo iterar un request.POST
        post = []
        for key in request.POST:
            post.append(request.POST[key])
        return HttpResponse(post)
        # Borrar
        """

        try:
            data = Order()
            data.user_id = current_user.id # en el modelo la relación se hace un campo user_id
            data.customer_id = customer.id # en el modelo la relación se hace un campo customer_id
            data.first_name = current_user.first_name
            data.last_name = current_user.last_name
            data.email = current_user.email
            # 8 Abril 2026
            #CORREGIR MANEJO DE OPCIONES DE ENVIO DESDE select_customer.html, 
            # no se pueden enviar valores booleanos
            if delivery == 'pickup':
                data.shipment = False
                data.pickup = True
                data.pickup_instructions = request.POST.get("pickup_instructions")
                data.address_line_1 = "Cliente retira en nuestra tienda:"
                data.address_line_2 = COMPANY_STREET
                data.phone = COMPANY_PHONE #current_user.phone
                data.country = COMPANY_COUNTRY #current_user.country
                data.state = COMPANY_STATE #current_user.state
                data.city = COMPANY_CITY #current_user.city
                data.zipcode = COMPANY_ZIP
            else:
                data.address_line_1 = address.address_line_1
                data.address_line_2 = address.address_line_2
                data.country = address.country
                data.state = address.state
                data.city = address.city
                data.zipcode = address.zipcode
                data.phone = address.phone
            data.note = order_note
            data.sub_total = total # total de productos antes de envio e impuestos
            data.ship_cost = ship_cost                
            data.tax = tax
            data.total = g_total
            data.status = "Recibida"
            data.logistic_supp = logistic_supp
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d') #20240611
            
            # Rellenar de ceros 5 espacios
            # "42".zfill(5) >>> '00042'
            # Cambiar
            # Crear numero de orden
            id_len = len(str(data.id))
            zeros = ''  # inicializar con un '0', para que agregue los ceros indicados
            if id_len < 6:                
                for i in range(6-id_len):
                    zeros += '0'
                order_number = current_date + zeros + str(data.id)
            else:
                order_number = current_date + str(data.id)
            
            data.number = order_number
            data.save()
        except Exception as e:
            messages.error(request, f'Error al crear la orden. place_order() {e}')
            return redirect('ecart')
            

        # Orden generada (que esta en DB) enviar a template para PAGO
        order = get_object_or_404(Order,user=current_user, number=order_number, is_ordered=False)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'ship_cost': ship_cost,
            'tax': tax,
            'g_total': g_total,
            'ship_total': ship_total,
            'delivery': delivery,
            'collect': 0,
        }
        return render(request, 'order/payment_kleen.html', context)
    else:
        return redirect('checkout')


#Función para usarse SOLO con json y Paypal 
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id).exclude(quantity=0)
        payment = Payment.objects.get(payment_id=payment_id)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'payment': payment,
            'COMPANY_LOGO': COMPANY_LOGO,
        }
        #Agregado 20Jun Claude code
        if request.GET.get('ticket') == '1':
            return render(request, 'order/ticket_order.html', context)
        return render(request, "order/order_complete.html", context)
    except Exception as e:
            print("Error capturado:", e)
            messages.error(request, f'Orden exitosa!, pero no se imprimió su orden. {e}')
            return redirect('ecart')
    #except (Payment.DoesNotExist, Order.DoesNotExist):
    #    return redirect('dashboard')

    
