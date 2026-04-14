from .models import Cart, CartItem
from ecart.views import _cart_id

def counter(request):
    count = 0
    if 'admin' in request.path:        
        return {}
    else:
        try:                    # filter: 'fetch' todos los que cumplen con la condición
            #cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # [:1] solo compara una instancia de la query_set
                cart = Cart.objects.filter(cart_id=_cart_id(request))
                cart_items = CartItem.objects.all().filter(cart=cart[:1]) 

            for item in cart_items:
                count += item.quantity

        except Cart.DoesNotExist:
            count = 0

        return dict(cart_count=count)