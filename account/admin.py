from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address, Account, UserProfile
from django.utils.html import format_html

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line_1', 'phone', 'city', 'state', 'country', 'is_active', 'default')
    ordering = ('-created_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Address, AddressAdmin)

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_active', 'first_name', 'last_name', 'last_login', 'joined_at')
    list_display_links = ('email', 'username')
    readonly_fields = ('last_login', 'joined_at')
    ordering = ('-joined_at',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<image src="{}" width="30" hight="30" style="border-radius: 50%;">'.format(object.picture.url))
    thumbnail.short_description = 'Foto de perfil'
    list_display = ('thumbnail', 'user',)

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)



