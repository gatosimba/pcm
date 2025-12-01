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

# clinicas/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# clinicas/admin.py (adiciona no final)

@admin.register(TipoSala)
class TipoSalaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'nome', 'clinica', 'status_colorido', 'acoes')
    list_filter = ('clinica', 'status')
    search_fields = ('tipo', 'nome', 'clinica__nome')
    ordering = ('clinica', 'tipo')

    # Filtra por clínica do usuário logado
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.select_related('clinica')
        return qs.filter(clinica__user=request.user).select_related('clinica')

    # Filtra clínica no formulário
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "clinica":
            kwargs["queryset"] = Clinica.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Status com cor
    def status_colorido(self, obj):
        cor = "green" if obj.status == "ativa" else "red"
        return format_html(f'<b style="color:{cor}">{obj.get_status_display()}</b>')
    status_colorido.short_description = "Status"

    # Ação Editar
    def acoes(self, obj):
        edit_url = reverse('admin:clinicas_tipossala_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Editar</a>', edit_url)
    acoes.short_description = "Ações"

    # Remove toda poluição visual do Django
    actions = None
    def changelist_view(self, request, extra_context=None):
        extra_context = {'show_admin_actions': False}
        return super().changelist_view(request, extra_context=extra_context)
    
# clinicas/admin.py

from django.contrib import admin
from django.db.models import Sum

# INLINE DOS CUSTOS (fica dentro da sala, lindo!)
from django import forms

class CustoFixoInline(admin.TabularInline):
    model = CustoFixoSala
    extra = 1
    fields = ('nome_item', 'valor_mensal', 'mes_referencia', 'ano_referencia')
    formfield_overrides = {
        models.PositiveSmallIntegerField: {'widget': forms.NumberInput(attrs={'min': 2000, 'max': 2100})},
    }

class CustoVariavelInline(admin.TabularInline):
    model = CustoVariavelSala
    extra = 1
    fields = ('nome_item', 'valor_mensal', 'mes_referencia', 'ano_referencia')
    formfield_overrides = {
        models.PositiveSmallIntegerField: {'widget': forms.NumberInput(attrs={'min': 2000, 'max': 2100})},
    }

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'clinica', 'tipo', 'status_colorido', 'custo_hora_atual', 'lista_equipamentos', 'acoes')
    list_filter = ('clinica', 'tipo', 'status')
    search_fields = ('numero', 'nome', 'clinica__nome')
    filter_horizontal = ('equipamentos',)
    inlines = [CustoFixoInline, CustoVariavelInline]

    # ← TODOS esses métodos TEM que estar AQUI DENTRO, com recuo!
# === Dentro do SalaAdmin (tem que estar com esse recuo certinho!) ===
# === NO admin.py → dentro da classe SalaAdmin ===
    def custo_hora_atual(self, obj):
        try:
            valor = obj.calcular_custo_hora()
            #print('Volta Valor: ', valor)
            if valor > 0:
                return valor  #format_html('<b style="color:#28a745">R$ {:,.2f}</b>', valor)
            return format_html('<span style="color:#ccc">R$ 0,00</span>')
        except Exception as e:
            return format_html('<span style="color:red;font-size:9px">Erro!</span>')
    
    custo_hora_atual.short_description = "Custo/Hora"
    custo_hora_atual.admin_order_field = 'id'  # só pra poder ordenar

    def status_colorido(self, obj):
        cor = "green" if obj.status == "ativa" else "red"
        return format_html(f'<b style="color:{cor}">{obj.get_status_display()}</b>')
    status_colorido.short_description = "Status"

    def lista_equipamentos(self, obj):
        eqs = obj.equipamentos.all()[:3]
        lista = ", ".join([e.codigo for e in eqs])
        if obj.equipamentos.count() > 3:
            lista += f" +{obj.equipamentos.count()-3}"
        return lista or "Nenhum"
    lista_equipamentos.short_description = "Equipamentos"

    def acoes(self, obj):
        edit_url = reverse('admin:clinicas_sala_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Editar</a>', edit_url)
    acoes.short_description = "Ações"

    # Remove poluição
    actions = None
    def changelist_view(self, request, extra_context=None):
        extra_context = {'show_admin_actions': False}
        return super().changelist_view(request, extra_context=extra_context)