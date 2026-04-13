from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Refugee, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'is_staff', 'is_active', 'two_factor_enabled')
    list_filter = ('is_staff', 'is_active', 'two_factor_enabled')
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
        ('Segurança', {'fields': ('two_factor_enabled',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'two_factor_enabled'),
            },
        ),
    )


@admin.register(Refugee)
class RefugeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age', 'religion', 'political_ideology')
    list_filter = ('religion', 'political_ideology', 'education')
    search_fields = ('name', 'profession', 'user__email')
    raw_id_fields = ('user',)

    @admin.display(description='e-mail')
    def email(self, obj):
        return obj.user.email
