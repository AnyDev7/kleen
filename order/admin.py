from django.contrib import admin

from .models import Payment, Order, OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'price', 'quantity', 'ordered', 'variations')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'full_name', 'email', 'city', 'created_at', 'total', 'status', 'is_ordered', 'shipment', 'pickup')
    list_filter = ('status', 'is_ordered', 'shipment', 'pickup')
    ordering = ('-created_at', 'status', 'is_ordered', 'shipment', 'pickup')
    search_fields = ('number', 'first_name', 'last_name', 'phone', 'email', 'city')
    readonly_fields = ('number', 'total')
    list_display_links = ('full_name', 'number', 'email')
    filter_horizontal = ()
    list_per_page = 10
    
    fieldsets = ()
    inlines = [OrderProductInline,]

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'product', 'price', 'quantity', 'ordered', 'created_at')

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)