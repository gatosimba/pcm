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
    
from django.contrib import admin
from .models import Clinica, Parametro  # certifique-se de importar os dois

# ... (o ClinicaAdmin que já fizemos antes fica aqui em cima)

@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'valor', 'nome_clinica', 'localidade', 'uf')
    search_fields = ('clinica__nome', 'codigo', 'valor')
    list_filter = ('clinica__nome',)

    # ← Métodos mágicos que deixam o título bonitinho
    def nome_clinica(self, obj):
        return obj.clinica.nome
    nome_clinica.short_description = "Clínica"  # ← Aqui muda o título da coluna!
    nome_clinica.admin_order_field = 'clinica__nome'  # permite ordenar clicando

    def localidade(self, obj):
        return obj.clinica.localidade
    localidade.short_description = "Cidade"

    def uf(self, obj):
        return obj.clinica.uf
    uf.short_description = "UF"

    # Esconde o campo user (caso ainda exista no banco)
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'user' in fields:
            fields.remove('user')
        return fields

    # Filtra clínicas no dropdown
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica":
            if request.user.is_superuser:
                kwargs["queryset"] = Clinica.objects.all()
            else:
                kwargs["queryset"] = Clinica.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Filtra listagem
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(clinica__user=request.user)

#-------------------------
@admin.register(Categoria)
#-------------------------
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'nome_clinica', 'localidade', 'uf')
    search_fields = ('codigo', 'clinica__nome')
    list_filter = ('clinica',)

    # ← Métodos mágicos que deixam o título bonitinho
    def nome_clinica(self, obj):
        return obj.clinica.nome
    nome_clinica.short_description = "Clínica"  # ← Aqui muda o título da coluna!
    nome_clinica.admin_order_field = 'clinica__nome'  # permite ordenar clicando

    def localidade(self, obj):
        return obj.clinica.localidade
    localidade.short_description = "Cidade"

    def uf(self, obj):
        return obj.clinica.uf
    uf.short_description = "UF"




    # Esconde o campo user (caso ainda exista no banco)
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'user' in fields:
            fields.remove('user')
        return fields

    # Filtra clínicas no dropdown
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica":
            if request.user.is_superuser:
                kwargs["queryset"] = Clinica.objects.all()
            else:
                kwargs["queryset"] = Clinica.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Filtra listagem
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(clinica__user=request.user)
