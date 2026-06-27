from django.contrib import admin

#Claude code 20Jun 2026
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import urlencode

from .models import CashCut, CashRegister, IncomeOutcome


class IcomesOutcomesInline(admin.TabularInline):
    model = IncomeOutcome
    readonly_fields = ('user', 'cashcut', 'income', 'outcome', 'amount', 'concept', 'created_at')
    extra = 0


class CashCutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cashregister', 'print_ticket_link', 'status', 'start_at', 'end_at', 'initial_balance', 'cash_balance', 'final_balance', 'total_cash')
    list_filter = ('status', 'user', 'cashregister')
    ordering = ('-start_at', 'status', '-end_at', 'user', 'cashregister')
    search_fields = ('user', 'cashregister')
    readonly_fields = ('user', 'cashregister', 'status', 'initial_balance', 'incomes', 'cash_balance', 'final_balance', 'total_cash', 'start_at', 'end_at')
    list_display_links = ('user', 'cashregister', 'status')
    filter_horizontal = ()
    list_per_page = 10
    
    fieldsets = ()
    inlines = [IcomesOutcomesInline,]

    #Claude 26Jun 2026
    def print_ticket_link(self, obj):
        try:
            base_url = reverse('cash_cut_detail', args=[obj.id])
            params = urlencode({'ticket': '1'})
            url = f'{base_url}?{params}'
            return format_html('<a href="{}" target="_blank">🖨 Ticket</a>', url)
        except Exception:
            return '—'
    print_ticket_link.short_description = 'Ticket'

admin.site.register(CashRegister)
admin.site.register(CashCut, CashCutAdmin)