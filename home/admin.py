# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

admin.site.site_header = "MW5 SoftWare"
admin.site.index_title = "Bem-vindo ao PCM - Precificaçāo de Clínicas Médicas" # Título da página de índice
admin.site.site_title = "PCM - Precificaçāo de Clínicas Médicas"      # Título da barra do navegador para o admin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'nome', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'nome')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)