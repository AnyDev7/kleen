from django.contrib import admin # agregado
from .models import Category, SubCategory # agregado


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',)
    }
    list_display = ('name', 'slug')

admin.site.register(Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',)
    }
    list_display = ('name', 'slug', 'category')

admin.site.register(SubCategory, SubCategoryAdmin)

