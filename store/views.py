from django.shortcuts import redirect, render, HttpResponse, get_object_or_404, HttpResponseRedirect

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from kart.settings import PROD_PER_PAG


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
        paged_products = paging(request, products, PROD_PER_PAG) # Modificar la cantidad de productos por página PROD_PER_PAG=3 en .env
    
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
