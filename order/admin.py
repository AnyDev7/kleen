from django.contrib import admin

#Claude code 20Jun 2026
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import urlencode

from .models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'price', 'quantity', 'ordered', 'variations')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'full_name', 'print_ticket_link', 'email', 'city', 'created_at', 'total', 'status', 'is_ordered', 'shipment', 'pickup')
    list_filter = ('status', 'is_ordered', 'shipment', 'pickup')
    ordering = ('-created_at', 'status', 'is_ordered', 'shipment', 'pickup')
    search_fields = ('number', 'first_name', 'last_name', 'phone', 'email', 'city')
    readonly_fields = ('number', 'total')
    list_display_links = ('number', 'full_name', 'email')
    filter_horizontal = ()
    list_per_page = 10
    
    fieldsets = ()
    inlines = [OrderProductInline,]

    #Claude 20Jun 2026
    def print_ticket_link(self, obj):
        try:
            base_url = reverse('order_complete')
            params = urlencode({
                'order_number': obj.number,
                'payment_id': obj.payment.payment_id,
                'ticket': '1',
            })
            url = f'{base_url}?{params}'
            return format_html('<a href="{}" target="_blank">🖨 Ticket</a>', url)
        except Exception:
            return '—'
    print_ticket_link.short_description = 'Ticket'

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'product', 'price', 'quantity', 'ordered', 'created_at')

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)