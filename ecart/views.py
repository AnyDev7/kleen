from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from kart.settings import STATES_MX, COMPANY, COMPANY_BANN1, COMPANY_BANN2, COMPANY_BANN3, COMPANY_SLOGAN, COMPANY_SLOG_SUB1, COMPANY_SLOG_SUB2
from store.models import Product, Variation, StockVar
from ecart.models import Cart, CartItem
from account.models import Address
from order.models import Customer
from account.forms import AddressForm

#from account.views import addresses
from django.contrib.auth.decorators import login_required

import json
from django.views.decorators.http import require_POST


def _cart_id(request): # Conseguir la sesion actual
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Dictionary index request.POST (es un diccionario): https://stackoverflow.com/questions/4326658/how-to-index-into-a-dictionary
def get_first_key(dictionary):
    for key in dictionary:
        return key
    raise IndexError

@login_required(login_url='login')
def create_menu(request, flag=False, qty=0):
    product = None
    cart = None
    cart_item = None
    cart_item_exists = None
    current_user = request.user
    try:
        # Clear Cart / o comparar item by item
        CartItem.objects.filter(user=current_user).delete() #Clear CartItem
        products = Product.objects.all().filter(is_available=True)
        # o Cargar con bucle todos los productos en el ecart, sesión actual.
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # Conseguir el Cart actual con la cart_id de la sesion actual        
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request),
            )
            cart.save()
        for product in products:            
            #Modidicado 15Abr2026: product = product (no se puede comparar instancia con instancia) > product_id = product.id
            # product__id hace referencia a la relación del modelo CartItem con el modelo Products
            cart_item_exists = CartItem.objects.filter(product__id = product.id, cart=cart).exists()
            if cart_item_exists:
                #cart_item = CartItem.objects.filter(product=product, cart=cart)
                
                # 28ABR 2026: REVISAR SI obtiene el producto del carrito.
                #Obtener el item del carrito
                cart_item = CartItem.objects.get(product__id = product.id, cart=cart)
                cart_item.quantity = 0
                cart_item.user=current_user
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(user=current_user, 
                product=product, cart=cart, quantity=0)
                cart_item.save()
    except Exception as e:
        messages.warning(request, f"Error capturado: {e}")
        return redirect ('dashboard')
    if flag:
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
    else:
        return redirect('ecart')


def add_prod(request, product_id, flag=False, qty=0): # ADD_CART course
    try:
        product = Product.objects.get(id=product_id) # Get the product
    except Product.DoesNotExist:
        return redirect('store')
    #print(f" Entra a add_prod: {product}")
    # if the user is authenticated
    current_user = request.user
    if current_user.is_authenticated:
        product_variations = []
        if request.method == 'POST':
            option = []
            first_key = get_first_key(request.POST) # Dic de POST: key= "name" value= "value o contenido"
            first_val = request.POST[first_key]  # No maneja error si la key no existe en el Dic
            for item in request.POST:  
                key = item
                if key is not first_key:  # Nos saltamos el primer elemento del DicSet
                    # request.POST.get(key, "valor por default")  # Maneja error, devuelve default si key no existe.
                    option = request.POST.get(key)  # key = varcat  value = variation, value_stock(data-*) = stockvar.value
                    value = option.split("-")[0]
                    value_stock = option.split("-")[1] # NO se usó stockvar.value = data-*stockvarvalue, faltó traer data-*                    
                    
                # verificar si la variación coincide con el contenido del modelo (tabla)
                try:
                    # '__iexact' no importa si son mayusculas o minusculas
                    if len(value_stock) > 0:
                        #OK variations = StockVar.objects.all().filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value), value__iexact=value_stock)
                        variations = StockVar.objects.filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value), value__iexact=value_stock)
                    else:                        
                        #OK variations = StockVar.objects.all().filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value))
                        variations = StockVar.objects.filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value))
                    
                    for var in variations: 
                        product_variations.append(var)
                except Exception as e:
                    messages.warning(request, f"Error capturado: {e}")
                    return redirect ('store')   # / 'dashboard' / 'ecart'
        #print(f" Product_Variations, USER: {product_variations}")

        cart_item_exists = CartItem.objects.filter(product = product, user=current_user).exists()
        print(f" Usuario autenticado, Item existe en ecart?: {cart_item_exists}")
        if cart_item_exists:            
            cart_items = CartItem.objects.filter(product__id=product.id, user=current_user)
            exist_var_list = []
            id_cartitem_list = []
            # Manejo de listas e índices, checar si current_vars are in existing_vars
            for item in cart_items:
                existing_variations = item.variations.all()
                exist_var_list.append(list(existing_variations))
                id_cartitem_list.append(item.id)
            
            if product_variations in exist_var_list:  # Se van recorriendo las dos listas
                index = exist_var_list.index(product_variations)  # obtener el indice de esa variacion
                item_id = id_cartitem_list[index]  # obtener el valor de esa posición del indice
                item = CartItem.objects.get(product=product, id=item_id)
                # Increase cart item quantity
                if flag:
                    item.quantity += 1
                else:
                    if item.quantity > 1:
                        item.quantity -= 1
                item.save()
            else: # Si las variaciones no existen en el cart
                # Create new CartItem item, agregar un nuevo registro a la tabla
                item = CartItem.objects.create(user=current_user, product=product, quantity=1)                
                # Agregar variaciones. Se agregan todos los registros a la tabla, se hace manual.
                item.variations.clear()
                # igual a la iteración: item.variations.add(*product_variations)  # igual a la iteración, * agrega todas:
                if len(product_variations) > 0:
                    for variation in product_variations:
                        item.variations.add(variation) 
                
                item.save()

        else: # Si no existe el CartItem 
            cart_item = CartItem.objects.create(user=current_user, product=product, quantity=1)
            # Agregar variaciones. Se agregan todos los registros a la tabla.
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)  # igual a la iteración, *agrega todas:

            cart_item.save()
        return #redirect('ecart')
    
    # If user is NOT authenticated
    else:

        product_variations = []
        #if request.POST: No se usa
        if request.method == 'POST':
            option = []
            first_key = get_first_key(request.POST)
            first_val = request.POST[first_key]  # No maneja error si la key no existe en el Dic
            for item in request.POST:  
                key = item
                if key is not first_key:  # Nos saltamos el primer elemento del DicSet
                    option = request.POST.get(key)  # key = varcat  value = variation, data-* = stockvar.value
                    value = option.split("-")[0]
                    value_stock = option.split("-")[1] # NO se usó stockvar.value = data-*stockvarvalue, faltó traer data-*                    

                # verificar si la variación coincide con el contenido del modelo (tabla)
                try:
                    #debe ser get(), no filter()           # '__iexact' no importa si son mayusculas o minusculas
                    if len(value_stock) > 0:
                        #OK variations = StockVar.objects.all().filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value), value__iexact=value_stock)
                        variations = StockVar.objects.filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value), value__iexact=value_stock)
                    else:
                        #OK variations = StockVar.objects.all().filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value))
                        variations = StockVar.objects.filter(product__id=product_id, variation = Variation.objects.get(variation__iexact=value))
                    
                    for var in variations: 
                        product_variations.append(var)
                except Exception as e:
                    messages.warning(request, f"Error capturado: {e}")
                    return redirect ('store')   # / 'dashboard' / 'ecart'
        print(f" Product_Variations, NO user: {product_variations}")
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # Conseguir el Cart actual con la cart_id de la sesion actual        
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request),
            )
            cart.save()

        cart_item_exists = CartItem.objects.filter(product = product, cart=cart).exists()
        print(f" Usuario NO autenticado, Item existe en ecart?: {cart_item_exists}")
        if cart_item_exists: 
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            
            # We need: conseguir como identificar el item que se va a modificar, si no existe: se crea
            # existing_variations <- database
            # current_variations <- product_variations
            # item_id <- database CartItem

            exist_var_list = []
            id_cartitem_list = []
            # Manejo de listas e índices, checar si current_vars are in existing_vars
            for item in cart_items:
                existing_variations = item.variations.all()
                exist_var_list.append(list(existing_variations))
                id_cartitem_list.append(item.id)

            
            if product_variations in exist_var_list:  # Se van recorriendo las dos listas
                index = exist_var_list.index(product_variations)  # obtener el indice de esa variacion
                item_id = id_cartitem_list[index]  # obtener el valor de esa posición del indice
                item = CartItem.objects.get(product=product, id=item_id)
                # Increase cart item quantity
                if flag:
                    item.quantity += 1
                else:
                    if item.quantity > 1:
                        item.quantity -= 1

                item.save()
            else: # Si las variaciones no existen en el cart
                # Create new CartItem item, agregar un nuevo registro a la tabla
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)                
                # Agregar variaciones. Se agregan todos los registros a la tabla, se hace manual.
                item.variations.clear()                
                # igual a la iteración: item.variations.add(*product_variations)  # igual a la iteración, * agrega todas:
                if len(product_variations) > 0:
                    for variation in product_variations:
                        item.variations.add(variation) 
                    
                item.save()

        else: # Si no existen los CartItem 
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            # Agregar variaciones. Se agregan todos los registros a la tabla.
            cart_item.variations.clear()
            if len(product_variations) > 0:
                cart_item.variations.add(*product_variations)  # igual a la iteración, *agrega todas:

            cart_item.save()

        return #redirect('ecart')




#Vista agregada 16Jun 2026 - Claude code
#Actualizada Claude 18Jun 2026
@require_POST
def update_bunch_quantity(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')

    try:
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Cantidad inválida'}, status=400)

    try:
        current_user = request.user
        cart_item = CartItem.objects.get(id=cart_item_id, product_id=product_id, user=current_user)
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item no encontrado'}, status=404)

    # Validación de stock — JOSEMARIA 18Jun 2026
    available_stock = cart_item.product.stock
    if quantity > available_stock:
        return JsonResponse({
            'status': 'error',
            'message': f'Existencias insuficientes. Disponibles: {available_stock}',
            'available_stock': available_stock
        }, status=400)

    cart_item.quantity = quantity
    cart_item.save()

    total = tot_qty = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for for_cart_item in cart_items:
            total += for_cart_item.sub_total()
            tot_qty += for_cart_item.quantity

    except (CartItem.DoesNotExist, Cart.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Item no encontrado'}, status=404)

    return JsonResponse({
        'status': 'ok',
        'new_quantity': cart_item.quantity,
        'new_subtotal': cart_item.sub_total(),
        'total': total,
        'tot_qty': tot_qty,
        'available_stock': available_stock  # lo regresamos para que JS actualice el estado del botón
    })





def minus_add_to_prod(request, product_id, cart_item_id, flag=False):

    try:
        product = get_object_or_404(Product, id=product_id)
        current_user = request.user
        if current_user.is_authenticated:
            cart_item = get_object_or_404(CartItem, id=cart_item_id, product=product, user=current_user)            
        else:    
            cart = get_object_or_404(Cart, cart_id=_cart_id(request))
            cart_item = get_object_or_404(CartItem, id=cart_item_id, product=product, cart=cart)
        # Increase/decrease cart item quantity
        if flag:
            cart_item.quantity += 1
        else:
            if cart_item.quantity >= 1:
                cart_item.quantity -= 1
        cart_item.save()
    except Exception as e:
        messages.warning(request, f"Error capturado: {e}")
    
    return redirect('ecart')
    


def remove_item(request, product_id, cart_item_id):
    
    try:
        product = get_object_or_404(Product, id=product_id) # Get the product
        
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, user=request.user) #filtrar las variaciones
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # Conseguir el Cart actual con la cart_id de la sesion actual
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, cart=cart) #filtrar las variaciones
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
        return redirect('ecart')

    return redirect('ecart')



def ecart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    g_total = 0
    ship_cost = 0
    try:
        sub_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            # el 'price' se obtiene con la recursividad de las clases en los modelos
            #total += cart_item.product.price * cart_item.quantity
            # checar funcion/método def sub_total(request) en el modelo de CartItem
            # cart_item.sub_total -> una instancia, cart_item.sub_total() -> valor resultante, 
            sub_total = cart_item.sub_total()   # checa si tiene descuento el price
            total +=  sub_total
            quantity += cart_item.quantity
        
        # Revisar si aplica esto para vendedores nacionales
        ship_cost = 99   # Crear tabla para tax y para ship_cost (por zonas por estados calcular tarifa)
        ship_total = total + ship_cost
        tax = (2 * total)/100
        
        g_total = ship_total # debería ser si se cobran impuestos: g_total = ship_total + tax
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        return redirect('store')
        
    context = {
    'total': total,
    'tax': tax,
    'ship_cost': ship_cost,
    'g_total': g_total,
    'quantity': quantity,
    'cart_items': cart_items,
    }
    return render(request, 'store/ecart.html', context)


def direct_purchase(request, product_id):
    # Se debe programar con <script> js
    return

@login_required(login_url='login')
def select_customer(request, total="", flag=0):
    # flag=0 compra directa
    # flag=1 compra desde carrito
    # Crear proceso alterno de: direct_purchase
    # total debe ser string, porque las rutas no aceptan float
    if float(total) <= 0:
        messages.info(request, 'Carrito vacío.')
        return redirect('ecart')
    
    customers = None
    try:
        customers = Customer.objects.all().order_by('name')
    except Customer.DoesNotExist:
        customers = False
        messages.warning(request, 'No existe BD clientes.')
        return redirect('ecart')

    context = { 
    'total': total,
    'customers': customers,
    }
    
    return render(request, 'store/select_customer.html', context)


@login_required(login_url='login')
def select_address(request, total="", flag=0):
    # flag=0 compra directa
    # flag=1 compra desde carrito
    # Crear proceso alterno de: direct_purchase
    # total debe ser string, porque las rutas no aceptan float
    if float(total) <= 0:
        messages.info(request, 'Carrito vacío.')
        return redirect('ecart')
    try:
        address = Address.objects.filter(user__id=request.user.id,  default=True).first()
    except Address.DoesNotExist:
        address = False
        messages.warning(request, 'No tienes una direccion favorita predeterminada.')

    if address == None:
        address = False
        messages.warning(request, 'Registra una direccion favorita.')
            
    context = {
    'total': float(total),
    'address': address,
    }
    
    return render(request, 'store/select_address.html', context)
    

@login_required(login_url='login')
def checkout(request, address_id=0, total=0, tax=0, ship_cost=0, g_total=0, quantity=0):
    customer_id = 1
    delivery = 'pickup'
    order_note = "Sin notas"
    address_option = False
    #se debe obtener la dirección del customer
    address = 0

    if request.method == 'POST':
        # get from 'POST' customer id / food app -> address, pickup, order_note
        customer_id = int(request.POST.get("customer_select"))
        delivery = request.POST.get("delivery")
        order_note = request.POST.get("order_note")
    
    if delivery == 'ship':
        address_option = True
    elif delivery == 'pickup':
        address_option = False
    else:
        delivery = 'pickup'

    #obtener el customer, con su dirección
    customer_selected = get_object_or_404(Customer, id=customer_id)
    print(f'Cliente seleccionado: customer_selected.id {customer_selected.id}')
    #que ventaja tiene get_object_or_404 vs try: except:

    # Aqui se obtiene la direccion del user, no del customer
    #if address_option == True:
    #    try:
    #        address = Address.objects.get(id=int(shipment_option))
    #    except Address.DoesNotExist:
    #        address = None
    
    try:
        sub_total = 0
        sub_total = None

        if request.user.is_authenticated:
            # Productos cuyo precio no sea 100
            #productos = Producto.objects.exclude(precio=100)            
            #productos = Producto.objects.filter(~Q(precio=100))
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).exclude(quantity=0)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).exclude(quantity=0)
        
        for cart_item in cart_items:
            # el 'price' se obtiene con la recursividad de las clases en los modelos
            #total += cart_item.product.price * cart_item.quantity
            # checar funcion/método def sub_total(request) en el modelo de CartItem
            # cart_item.sub_total = una instancia, cart_item.sub_total() -> valor resultante, 
            cart_price = 0
            sub_total = cart_item.sub_total() #calcular subtotal
            total +=  sub_total
            quantity += cart_item.quantity
            cart_price = cart_item.cartitem_price() #verificar precio de promocion
            cart_item.price = cart_price
            cart_item.save()
        
        # Revisar si aplica esto para vendedores nacionales
        ship_cost = 99
        ship_total = total + ship_cost
        tax = 0
        g_total = ship_total + tax # debería ser si se cobran impuestos: g_total = ship_total + tax
        context = {
        'total': total,
        'tax': tax,
        'ship_cost': ship_cost,
        'g_total': g_total,
        'quantity': quantity,
        'cart_items': cart_items,
        'delivery': delivery,
        'address_option': address_option,
        'address': address,
        'order_note': order_note,
        'customer': customer_selected.id,
        }

        # Enviar primero a selección de dirección: return render(request, 'store/select_address.html', context)
        return render(request, 'store/checkout.html', context)

    except Cart.DoesNotExist or CartItem.DoesNotExist:
        messages.warning(request, f"Error no existe Cart o CartItem: checkout")
        return redirect ('ecart')
            
        
    
    