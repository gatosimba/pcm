# clinicas/admin.py
from django.contrib import admin
from .models import *

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'cep', 'localidade', 'uf')
    search_fields = ('nome', 'cep', 'uf')
    readonly_fields = ('user',)  # deixa só leitura em edição

    actions = None                                      # 1 mata seleção em massa
    list_filter = ()                                    # 2 mata o filtro lateral (se quiser (ou deixa só os que você quer)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_actions'] = False     # 3 MATA A COLUNA DE AÇÕES DO LADO DIREITO PRA SEMPRE
        return super().changelist_view(request, extra_context=extra_context)


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
            return ('nome', 'status', 'cep', 'localidade', 'uf')
        return ('nome', 'status', 'cep', 'localidade', 'uf')
    
# ... (o ClinicaAdmin que já fizemos antes fica aqui em cima)

@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'valor', 'nome_clinica', 'cidade', 'uf')
    search_fields = ('clinica__nome', 'codigo', 'valor')
    list_filter = ('clinica__nome',)

    actions = None                                      # 1 mata seleção em massa
    list_filter = ()                                    # 2 mata o filtro lateral (se quiser (ou deixa só os que você quer)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_actions'] = False     # 3 MATA A COLUNA DE AÇÕES DO LADO DIREITO PRA SEMPRE
        return super().changelist_view(request, extra_context=extra_context)

    # ← Métodos mágicos que deixam o título bonitinho
    def nome_clinica(self, obj):
        return obj.clinica.nome
    nome_clinica.short_description = "Clínica"  # ← Aqui muda o título da coluna!
    nome_clinica.admin_order_field = 'clinica__nome'  # permite ordenar clicando

    # ← CIDADE (LOCALIDADE)
    def cidade(self, obj):
        return obj.clinica.localidade
    cidade.short_description = "Cidade"
    cidade.admin_order_field = 'clinica__localidade'  # ordena por cidade!

    # ← UF
    def uf(self, obj):
        return obj.clinica.uf
    uf.short_description = "UF"
    uf.admin_order_field = 'clinica__uf'  # ordena por estado!

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
    list_display = ('codigo', 'descricao', 'nome_clinica', 'cidade', 'uf')
    search_fields = ('codigo', 'clinica__nome')
    list_filter = ('clinica',)

    actions = None                                      # 1 mata seleção em massa
    list_filter = ()                                    # 2 mata o filtro lateral (se quiser (ou deixa só os que você quer)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_actions'] = False     # 3 MATA A COLUNA DE AÇÕES DO LADO DIREITO PRA SEMPRE
        return super().changelist_view(request, extra_context=extra_context)

    # ← Métodos mágicos que deixam o título bonitinho
    def nome_clinica(self, obj):
        return obj.clinica.nome
    nome_clinica.short_description = "Clínica"  # ← Aqui muda o título da coluna!
    nome_clinica.admin_order_field = 'clinica__nome'  # permite ordenar clicando

    # ← CIDADE (LOCALIDADE)
    def cidade(self, obj):
        return obj.clinica.localidade
    cidade.short_description = "Cidade"
    cidade.admin_order_field = 'clinica__localidade'  # ordena por cidade!

    # ← UF
    def uf(self, obj):
        return obj.clinica.uf
    uf.short_description = "UF"
    uf.admin_order_field = 'clinica__uf'  # ordena por estado!

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
@admin.register(Equipamento)
#-------------------------
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'status', 'fabricante', 'marca', 'nome_clinica', 'cidade', 'uf')

    search_fields = ('codigo', 'clinica__nome')
    list_filter = ('clinica',)

    actions = None                                      # 1 mata seleção em massa
    list_filter = ()                                    # 2 mata o filtro lateral (se quiser (ou deixa só os que você quer)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_actions'] = False     # 3 MATA A COLUNA DE AÇÕES DO LADO DIREITO PRA SEMPRE
        return super().changelist_view(request, extra_context=extra_context)

    # ← Métodos mágicos que deixam o título bonitinho
# ← CLÍNICA
    def nome_clinica(self, obj):
        return obj.clinica.nome
    nome_clinica.short_description = "Clínica"
    nome_clinica.admin_order_field = 'clinica__nome'  # ordena por nome da clínica

    # ← CIDADE (LOCALIDADE)
    def cidade(self, obj):
        return obj.clinica.localidade
    cidade.short_description = "Cidade"
    cidade.admin_order_field = 'clinica__localidade'  # ordena por cidade!

    # ← UF
    def uf(self, obj):
        return obj.clinica.uf
    uf.short_description = "UF"
    uf.admin_order_field = 'clinica__uf'  # ordena por estado!

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

#--------------------
@admin.register(Sala)
#--------------------

class SalaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'clinica', 'descricao', 'ativa', 'lista_equipamentos')
    list_filter = ('clinica', 'ativa')
    search_fields = ('numero', 'descricao', 'clinica__nome')
    filter_horizontal = ('equipamentos',)  # ou filter_vertical

    actions = None                                      # 1 mata seleção em massa
    list_filter = ()                                    # 2 mata o filtro lateral (se quiser (ou deixa só os que você quer)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_actions'] = False     # 3 MATA A COLUNA DE AÇÕES DO LADO DIREITO PRA SEMPRE
        return super().changelist_view(request, extra_context=extra_context)
            
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(clinica__user=request.user)

    # Filtra a clínica no formulário
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica":
            kwargs["queryset"] = Clinica.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # O SEGREDO: filtra equipamentos com base na clínica já escolhida
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "equipamentos":
            # Se já tem um obj (edição) ou clínica já foi escolhida via GET
            if request.resolver_match.kwargs.get('object_id'):
                # Em edição: pega a clínica do objeto
                obj = Sala.objects.get(pk=request.resolver_match.kwargs['object_id'])
                kwargs["queryset"] = Equipamento.objects.filter(clinica=obj.clinica)
            elif request.GET.get('clinica'):
                # Em criação: pega do parâmetro GET (vamos forçar isso)
                clinica_id = request.GET.get('clinica')
                kwargs["queryset"] = Equipamento.objects.filter(clinica_id=clinica_id)
            else:
                # Por segurança: só mostra da clínica do usuário
                kwargs["queryset"] = Equipamento.objects.filter(clinica__user=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def lista_equipamentos(self, obj):
        return ", ".join([eq.codigo for eq in obj.equipamentos.all()]) or "-"
    lista_equipamentos.short_description = "Equipamentos"

    # BONUS: pré-seleciona a clínica se o usuário tiver só uma
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and Clinica.objects.filter(user=request.user).count() == 1:
            form.base_fields['clinica'].initial = Clinica.objects.filter(user=request.user).first()
        return form