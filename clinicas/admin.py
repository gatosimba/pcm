# clinicas/admin.py
from django.contrib import admin
from .models import *

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cep', 'localidade', 'uf')
    search_fields = ('nome', 'cepj', 'uf')
    readonly_fields = ('user',)  # deixa só leitura em edição

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # Esconde o campo User do formulário para usuários normais
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Remove o campo completamente para usuários normais
            form.base_fields.pop('user', None)
        return form

    # Preenche automaticamente na criação
    def save_model(self, request, obj, form, change):
        if not change:  # só na criação
            obj.user = request.user
        super().save_model(request, obj, form, change)

    # Opcional: esconde o campo também na lista (se não quiser mostrar o dono)
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('nome', 'cep', 'localidade', 'uf')
        return ('nome', 'cep', 'localidade', 'uf')
    
@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ('clinica', 'codigo', 'valor', 'descricao')
    list_filter = ('clinica', 'codigo',)
    search_fields = ('clinica', 'codigo',)    

