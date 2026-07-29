from datetime import date

from django.shortcuts import redirect, render, HttpResponse, get_object_or_404, HttpResponseRedirect

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from kart.settings import PROD_PER_PAGE, COMPANY_LOGO, COMPANY_PHONE, COMPANY_STREET, COMPANY_COUNTRY, COMPANY_STATE, COMPANY_CITY, COMPANY_ZIP

#Clde 22Jul 2026
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
#from django.contrib.auth.decorators import login_required
#from django.db.models import Q
from order.models import Customer


from store.models import Product, VarCat, Variation, StockVar, Rating, ProductGallery
from category.models import Category, SubCategory
from ecart.models import Cart, CartItem
from ecart.views import _cart_id
from .forms import formRating
from order.models import OrderProduct
from account.models import UserProfile

# Create your views here.
"""
def get_variations(product):
    
    return HttpResponse(f"dentro de get_variations")
    try:
        return HttpResponse(f"entra a try: de _get_vars")
        varsall = StockVar.objects.all()
        return HttpResponse(f"Variaciones: {varsall} {product}")
    except Exception as e:
        raise e
    
    return HttpResponse(f"No pasa try: de _get_vars")
    return varsall
"""

def paging(request, products, number_pages):
    paginator = None
    page = None
    paged_products = None
    paginator = Paginator(products, number_pages)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    return paged_products

def store(request, category_slug=None, cat_slug=None, flag=None):
    paged_products = None
    products = None
    low_prods = None

    if category_slug != None:
        if flag == 's':
            category = get_object_or_404(SubCategory, slug=category_slug)
            products = Product.objects.filter(categories=category, is_available=True).order_by('-has_discount', '-created_at')    
            low_prods = Product.objects.filter(categories=category, is_available=True, has_discount=True)
        else:
            #category = get_object_or_404(SubCategory, category__slug=cat_slug) # Sí funciona, devuelve 2 instancias o más
            category = get_object_or_404(Category, slug=cat_slug) # Sí funciona
            #subcategory = get_object_or_404(SubCategory, category=category) # Devuelve 2 instancias
            # Puede causar sobre tráfico en la consulta
            products = Product.objects.filter(categories__category=category, is_available=True).order_by('-has_discount', '-created_at').distinct() # Quitar los productos repetidos #Sí funciona
            low_prods = Product.objects.filter(categories__category=category, is_available=True, has_discount=True).distinct() # Quitar los productos repetidos

        prod_count = products.count()
        low_prod_count = low_prods.count()
        #paged_products = paging(request, products, 1)

    else:
        products = Product.objects.all().filter(is_available=True).order_by('-has_discount', '-created_at')
        prod_count = products.count()

        low_prods = Product.objects.filter(is_available=True, has_discount=True)
        low_prod_count = low_prods.count()

    if products:    
        paged_products = paging(request, products, PROD_PER_PAGE) # Modificar la cantidad de productos por página PROD_PER_PAGE=3 en .env
    
    context = {
        'title': 'Store',
        'products': paged_products,
        'prod_count': prod_count,
        'low_prod_count': low_prod_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    varsall = None
    try:              # con doble '__' se hace recursivo a parámetro de un campo 'foreign key'
        single_product = Product.objects.get(categories__slug=category_slug, slug=product_slug)
        subcat = SubCategory.objects.get(slug=category_slug)

        # 23 marzo 2026 se agregó .order_by('variation')
        #ordenar para unificar productos por variación
        varsall = StockVar.objects.all().filter(product = single_product).order_by('variation')

        #Prefetch Foreign https://stackoverflow.com/questions/76143776/django-template-language-how-to-write-model-model-set-filter-in-a-template
        #https://forum.djangoproject.com/t/how-to-filter-this-manytomany-relation/6451
        #followed_posts = Posts.objects.filter(autor__followers__username=user_username)
        #catsall = VarCat.objects.all().filter(varcat in varsall)
        #catall = Variation.objects.all().filter(variation=)
        #catall = VarCat.objects.all().filter(varcat = varsall__variations)
        #todasvar = Variation.objects.filter(variation=indexstock)
        #varsall = get_variations(single_product)

        # no regresa un objeto del query_set, solo el valor booleano            
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    # El usuario ya compro el producto?
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
            userprofile = UserProfile.objects.get(user__id=request.user.id)
                
        except OrderProduct.DoesNotExist:
            orderproduct = False
    else:
        orderproduct = False
        userprofile = False

    # Las calificaciones de este producto
    try: 
        ratings = Rating.objects.filter(product_id=single_product.id, status=True)
        # Quitar rate = ratings.first()
        # Quitar average = rate.average()

    except:
        None

    # Galeria del producto
    try: 
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    except:
        None

    context = {
            'prod': single_product,
            'cat': subcat.category,
            'subcat': subcat,
            'in_cart': in_cart,
            'varsall': varsall,
            'orderproduct': orderproduct,
            'ratings': ratings,
            'product_gallery': product_gallery,
            'userprofile': userprofile,
    }
    
    return render(request, "store/product_detail_vars.html", context) # OK


def search(request):
    description = None
    name = None
    products = None
    paged_products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:  # si no está vacío el input name="keyword" en GET
            """
            description = Product.objects.order_by('-has_discount', '-created_at').filter(description__icontains=keyword, is_available=True)
            name = Product.objects.order_by('-has_discount', '-created_at').filter(name__icontains=keyword, is_available=True)
            # Esta opcion era el mismo resultado: products = description | name
            """
            products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(name__icontains=keyword)
                ).order_by('-has_discount', '-created_at')
            prod_count = products.count()

            low_prods = products.filter(has_discount=True)
            low_prod_count = low_prods.count()
            
        else: 
            products = Product.objects.order_by('-has_discount', '-created_at').filter( is_available=True)
            prod_count = products.count()
            low_prods = Product.objects.order_by('-has_discount', '-created_at').filter(is_available=True, has_discount=True)
            low_prod_count = low_prods.count()
            
        paged_products = paging(request, products, 2)
        context = {
            'products': paged_products,
            'prod_count': prod_count,
            'low_prod_count': low_prod_count,
        }
        
        return render(request, 'store/store.html', context)
    
#@login_required(login_url='login')
def rating(request, product_id):
    url = request.META.get('HTTP_REFERER')  # url: Guarda la url anterior
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                rate = Rating.objects.get(user__id=request.user.id, product__id=product_id)
                form = formRating(request.POST, instance=rate)  # instance: rellena con los datos que ya existen.
                form.save()
                messages.success(request, 'Gracias, tu calificación se actualizó')
                return redirect(url)
            except Rating.DoesNotExist:
                form = formRating(request.POST)
                if form.is_valid():
                    data = Rating()
                    data.user_id = request.user.id
                    data.product_id = product_id  # se usa: data.product_id, porque es un dato de otro Modelo (foreignkey)
                    data.rating = form.cleaned_data['rating']
                    data.subject = form.cleaned_data['subject']
                    data.review = form.cleaned_data['review']
                    data.ip = request.META.get('REMOTE_ADDR')                
                    data.save()
                    messages.success(request, 'Gracias, se envió tu calificación y comentario!')
                    return redirect(url)
    else:
        messages.error(request, 'Debes estar registrado para calificar productos!')
        return redirect('login')
    return redirect(url)

#Clde 22Jul 2026
@login_required
def pos(request):
    #presentar tabla vacia en POS
    default_customer = Customer.objects.get(id=1)
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    cart_items.delete()
    total = sum(item.sub_total() for item in cart_items)
    qty   = sum(item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'qty': qty,
        'COMPANY_LOGO': COMPANY_LOGO,
        'default_customer': default_customer,
    }
    return render(request, 'store/pos.html', context)


@login_required
@require_GET
def pos_search_product(request):
    term = request.GET.get('q', '').strip()
    if len(term) < 2:
        return JsonResponse({'products': []})
    products = Product.objects.filter(
        Q(barcode__icontains=term) |
        Q(sku__icontains=term) |
        Q(name__icontains=term) |
        Q(description__icontains=term),  # agregado
        is_available=True,
        stock__gt=0
    )[:10]
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku or '',
            'barcode': p.barcode or '',
            'price': float(p.low_price if p.has_discount else p.price),
            'stock': p.stock,
            'image': p.image1.url if p.image1 else '',
        })
    return JsonResponse({'products': data})


@login_required
@require_GET
def pos_search_customer(request):
    term = request.GET.get('q', '').strip()
    if len(term) < 2:
        return JsonResponse({'customers': []})
    customers = Customer.objects.filter(
        Q(name__icontains=term) |
        Q(phone__icontains=term) |
        Q(email__icontains=term)
    )[:8]
    data = [{'id': c.id, 'name': c.name, 'phone': c.phone or ''} for c in customers]
    return JsonResponse({'customers': data})


@login_required
@require_POST
def pos_add_product(request):
    try:
        body = json.loads(request.body)
        product_id = body.get('product_id')
        product = Product.objects.get(id=product_id, is_available=True)
    except (Product.DoesNotExist, Exception):
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

    if product.stock < 1:
        return JsonResponse({'status': 'error', 'message': 'Sin existencias disponibles'}, status=400)

    # Buscar si ya existe en el carrito
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        if cart_item.quantity >= product.stock:
            return JsonResponse({
                'status': 'error',
                'message': f'Existencias insuficientes. Disponibles: {product.stock}',
                'available_stock': product.stock
            }, status=400)
        cart_item.quantity += 1
        cart_item.save()

    # Recalcular totales
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    total = sum(item.sub_total() for item in cart_items)
    tot_qty = sum(item.quantity for item in cart_items)

    return JsonResponse({
        'status': 'ok',
        'created': created,           # True = fila nueva, False = solo actualizó cantidad
        'cart_item_id': cart_item.id,
        'product_id': product.id,
        'product_name': product.name,
        'quantity': cart_item.quantity,
        'price': float(product.low_price if product.has_discount else product.price),
        'has_discount': product.has_discount,
        'original_price': float(product.price),
        'subtotal': float(cart_item.sub_total()),
        'available_stock': product.stock,
        'total': float(total),
        'tot_qty': tot_qty,
    })


from django.utils.timezone import now
from order.models import Order, OrderProduct, Payment, Customer
import uuid

@login_required
@require_POST
def pos_process_order(request):
    try:
        body        = json.loads(request.body)
        customer_id = int(body.get('customer_id', 1))
        order_note  = body.get('order_note', '')
        payments    = body.get('payments', [])  # [{'method': 'Cash', 'amount': 500}, ...]

        if not payments:
            return JsonResponse({'status': 'error', 'message': 'No se recibieron datos de pago'}, status=400)

        current_user = request.user

        # Validar cliente
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cliente no encontrado'}, status=404)

        # Obtener items del carrito
        cart_items = CartItem.objects.filter(user=current_user, is_active=True).exclude(quantity=0)
        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'El carrito está vacío'}, status=400)

        # Calcular totales
        total    = 0
        quantity = 0
        for item in cart_items:
            # Actualizar precio al valor actual (promoción o precio normal)
            item.price = item.cartitem_price()
            item.save()
            total    += item.sub_total()
            quantity += item.quantity

        # Crear la orden
        order = Order()
        order.user_id     = current_user.id
        order.customer_id = customer.id
        order.first_name  = current_user.first_name
        order.last_name   = current_user.last_name
        order.email       = current_user.email
        order.phone       = COMPANY_PHONE
        order.address_line_1 = 'Cliente retira en nuestra tienda:'
        order.address_line_2 = COMPANY_STREET
        order.country     = COMPANY_COUNTRY
        order.state       = COMPANY_STATE
        order.city        = COMPANY_CITY
        order.zipcode     = COMPANY_ZIP
        order.note        = order_note
        order.sub_total   = total
        order.ship_cost   = 0
        order.tax         = 0
        order.total       = total
        order.status      = 'New'
        order.pickup      = True
        order.shipment    = False
        order.logistic_supp = 'pickup'
        order.ip          = request.META.get('REMOTE_ADDR')
        order.save()

        # Generar número de orden (mismo algoritmo que place_order)
        current_date = date.today().strftime('%Y%m%d') #20240611
        id_len = len(str(order.id))
        zeros  = '0' * (6 - id_len) if id_len < 6 else ''  # inicializar con un '0', para que agregue los ceros indicados
        order.number = current_date + zeros + str(order.id)
        order.save()

        # Crear OrderProduct por cada item del carrito
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id   = order.id
            order_product.user_id    = current_user.id
            order_product.product_id = item.product.id
            order_product.quantity   = item.quantity
            order_product.price      = item.price
            order_product.ordered    = True
            order_product.save()
            # Variaciones (aunque en POS son productos simples, lo dejamos robusto)
            if item.variations.exists():
                order_product.variations.set(item.variations.all())

            # Descontar stock
            product = item.product
            product.stock -= item.quantity
            product.save()

        # Crear Payment(s) — uno por método de pago usado
        payment_id_base = uuid.uuid4().hex[:12].upper()

        first_payment = None
        for i, pay in enumerate(payments):
            method = pay.get('method')
            amount = float(pay.get('amount', 0))
            if amount <= 0 or method not in ('Cash', 'Transfer', 'Paypal'):
                continue
            payment = Payment.objects.create(
                user           = current_user,
                payment_id     = f'{payment_id_base}-{i+1}',
                payment_method = method,
                amount_paid    = amount,
                currency       = 'MXN',
                status         = 'Completed',
                paid_at        = now(),
                collect        = False,
                order          = order,   # vincula todos los pagos a la orden
            )
            payment.save()
            if first_payment is None:
                first_payment = payment

        # Vincular el primer pago al campo ForeignKey existente en Order
        order.payment    = first_payment
        order.is_ordered = True
        order.status = "Paid"
        order.save()


        # Vaciar el carrito
        cart_items.delete()

        # URL de confirmación (mismo patrón que el flujo normal)
        from urllib.parse import urlencode
        params = urlencode({
            'order_number': order.number,
            'payment_id':   first_payment.payment_id,
        })
        redirect_url = f"{reverse('order_complete')}?{params}"

        return JsonResponse({'status': 'ok', 'redirect_url': redirect_url})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al procesar la orden: {e}'}, status=500)