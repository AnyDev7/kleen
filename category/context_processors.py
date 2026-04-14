from .models import Category, SubCategory

def menu_cat_links(request):
    links = Category.objects.all()
    return dict(cat_links=links)

def menu_subcat_links(request):
    links = SubCategory.objects.all()
    return dict(subcat_links=links)

