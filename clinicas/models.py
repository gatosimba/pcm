from django.db        import models
from django.conf      import settings
from django.conf      import settings
from django.utils     import timezone
from django.contrib   import admin
from decimal          import Decimal
from django.db.models import Sum

from django.core.validators     import MinValueValidator, MaxValueValidator
from django.utils.translation   import gettext_lazy as _
from django.core.exceptions     import ValidationError
from django.contrib.auth.models import User

import requests
import logging
import re

logger = logging.getLogger(__name__)

#=====================================
class UpperCharField(models.CharField):
    def get_prep_value(self, value):
        return str(value).upper() if value is not None else value

#---------------------------
# Principal Model do PCM
#---------------------------
class Clinica(models.Model):
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinicas'
    )
    nome        = UpperCharField(_('Clínica'),max_length=64, blank=False, null=False, unique=True)
    responsavel = UpperCharField(_('Responsável'),max_length=64, blank=True, null=True)
    email       = models.EmailField(_('E-mail'), blank=True, null=True)
    zap         = models.CharField(_('Whatszap'), blank=True, null=True)
# Campos do Endereço Completo
    cep         = models.CharField(_('CEP') ,max_length=9, blank=True, null=True)
    logradouro  = UpperCharField(_('Logradouro'),max_length=64, blank=True, null=True)
    complemento = UpperCharField(_('Complemento'), max_length=32, blank=True, null=True)
    bairro      = UpperCharField(_('Bairro'), max_length=64, blank=True, null=True)
    localidade  = UpperCharField(_('Cidade'), max_length=64, blank=True, null=True)
    uf          = UpperCharField(_('Estado'),max_length=2, blank=True, null=True)
#================
    status      = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='ativa')
    data_criacao = models.DateTimeField(_('Data Criação'), default=timezone.now)
    data_atualizacao = models.DateTimeField(_('Data Atualização'), auto_now=True)

    class Meta:
        db_table = 'clinicas'
        verbose_name = 'Clínica'
        verbose_name_plural = '(C1) Clínicas'

    def __str__(self):
        return f'{self.nome}'

    def cidade_estado(self, obj):
        cidade_uf = f"{obj.localidade or ''}/{obj.uf or ''}"
        return f"{obj.localidade or ''}/{obj.uf or ''}"
    cidade_estado.short_description = 'Cidade/UF'

#-- Buscar o CEP para preenchimento do endereço
    def save(self, *args, **kwargs):
        #print(f"Salvando o objeto: {self.nome}")

        url = f"https://viacep.com.br/ws/{self.cep}/json/"


        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError("Erro ao consultar o ViaCEP.")
        except ValueError:
            raise ValidationError("Resposta inválida do ViaCEP (JSON inválido).")

        # GARANTA que data é um dict
        if not isinstance(data, dict):
            raise ValidationError("Resposta do ViaCEP não é um JSON válido.")

        if data.get("erro"):  # Agora é seguro
            raise ValidationError("CEP não encontrado no ViaCEP.")

        self.logradouro = data.get("logradouro", "")
        self.bairro = data.get("bairro", "")
        self.localidade = data.get("localidade", "")
        self.uf = data.get("uf", "")

        super().save(*args, **kwargs)  # Chama o save original
        #print(f"Objeto salvo com ID: {self.id}")
#-----------------------------------------------

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,

            'cep': self.cep,
            'logradouro': self.logradouro,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'localidade': self.localidade,
            'uf': self.uf,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
        }


class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_clinica'
    )
    clinica = models.ForeignKey(
        'Clinica',
        on_delete=models.CASCADE,
        related_name='perfis'
    )

    def __str__(self):
        return f"{self.user} → {self.clinica}"

#-----------------------------
class Parametro(models.Model):
#-----------------------------
#     
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='parametros'
    )
    codigo = UpperCharField("Código", max_length=16)  # ← sem unique=True aqui!
    valor = models.CharField("Valor", max_length=32)
    descricao = UpperCharField("Descrição", max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.clinica.nome}"

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "(C2) Parâmetros"
        # ← ÚNICO POR CLÍNICA, não global!
        unique_together = ('clinica', 'codigo')

#------------------------------
class TipoPessoa(models.Model):
#------------------------------
#     
    TIPO_CHOICES = [
        ('saude', 'Saúde'),
        ('terceiro', 'Terceirizado'),
        ('administrativo', 'Administrativo'),
    ]
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='tipospessoa'
    )
    pessoa = UpperCharField(_("Tipo de Pessoa"), max_length=64,
        help_text=_("Informe o Tipo do Profissional. Obrigatório!"))
    especialidade = UpperCharField(_("Especialidade"),  max_length=64, blank=True, null=True,
        help_text=_("Informe a Especialidade do Profissional. Opciona!"))
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, 
        blank=False, null=False, default='saude',
        help_text=_("Escolha a Função do Profissional. Default Saúde!"))

    def __str__(self):
        return f"{self.pessoa} - {self.clinica.nome}"

    class Meta:
        verbose_name = "Tipos de Pessoa"
        verbose_name_plural = "Tipos de Pessoa"
        # ← ÚNICO POR CLÍNICA, não global!
        unique_together = ('clinica', 'pessoa')

#-----------------------------
class Categoria(models.Model):
#-----------------------------    
    TIPO_CHOICES = [
        ('procedimento', 'Procedimento'),
        ('custo', 'Custo'),
    ]
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='categorias'
    )
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    codigo = UpperCharField('Código', max_length=16, blank=False, null=False)
    descricao = UpperCharField('Descrição', max_length=128, blank=True, null=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, blank=False, null=False)

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoria'
        verbose_name_plural = '(C3) Categorias'
        unique_together = ('clinica', 'codigo')

    def __str__(self):
        #return f'{self.codigo} {self.descricao} {self.clinica} ({self.get_tipo_display()})'
        return f'{self.descricao} ( {self.get_tipo_display()}) - {self.clinica}'

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'tipo': self.tipo,
        }
#----------------------------
class TipoSala(models.Model):
#----------------------------
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
    ]

    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='tipossala'
    )
    tipo       = UpperCharField('Tipo', max_length=16, blank=False, null=False)    
    nome       = UpperCharField('Nome Sala', max_length=64, blank=False, null=False)
    observacao = UpperCharField('Observação', max_length=128, blank=True, null=True)
    status     = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativa')
    
    class Meta:
        db_table = 'tipossala'
        verbose_name = 'Tipo de Sala'
        verbose_name_plural = '(S1) Tipos de Sala'
        unique_together = ('clinica', 'tipo')

    def __str__(self):
        return f'{self.tipo}'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo':self.tipo,
            'nome': self.nome,
            'status':self.status,
            'observacao': self.observacao,
        }

#-------------------------------
class Equipamento(models.Model):
#-------------------------------
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='equipamento'
    )
    codigo        = UpperCharField('Codigo', max_length=16, blank=False, null=False)    
    descricao     = UpperCharField('descricao', max_length=128, blank=False, null=False)
    fabricante    = UpperCharField('Fabricante', max_length=128, blank=True, null=True)
    marca         = UpperCharField('Marca', max_length=64, blank=True, null=True)
    dta_aquisicao = models.DateTimeField('Data Aquisição', blank=True, null=True)
    vlr_aquisicao = models.FloatField('Valor Aquisição', blank=True, null=True)
    custo_dia     = models.FloatField('Custo Dia', blank=True, null=True)
    custo_mes     = models.FloatField('Custo Mes', blank=True, null=True)
    status        = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativo')
    
    class Meta:
        db_table = 'equipamento'
        verbose_name = 'Equipamento'
        verbose_name_plural = '(C4) Equipamentos'
        unique_together = ('clinica', 'codigo')

    def __str__(self):
        return f'{self.codigo},{self.descricao},{self.status}'

    def salas_list(self):
        return ", ".join([s.numero for s in self.salas.all()])
    salas_list.short_description = "Usado nas salas"

    def to_dict(self):
        return {
            'id': self.id,
            'codigo':self.codigo,
            'descricao': self.descricao,
            'fabricante': self.fabricante,
            'marca': self.marca,
            'dta_aquisicao': self.dta_aquisicao,
            'vlr_aquisicao': self.vlr_aquisicao,
            'custo_dia': self.custo_dia,
            'custo_mes': self.custo_mes,
            'status':self.status,

        }
    
#------------------------
class Sala(models.Model):

    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
    ]
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='salas'  # ← esse pode ficar "salas"
    )
    tipo = models.ForeignKey(
        TipoSala,
        on_delete=models.CASCADE,
        null=True,
        related_name='salas'  # ← esse pode ficar "salas"
    )

    numero = UpperCharField("Nro Sala", max_length=16)
    nome = UpperCharField("Nome Sala", max_length=64, blank=True, null=True)
    cor = UpperCharField("Cor no Agendamento", max_length=7, default="#007bff")
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativa')

    equipamentos = models.ManyToManyField(
        Equipamento,
        related_name='salas_equipamentos',  # ← mudou aqui pra não conflitar
        blank=True
    )

    class Meta:
        unique_together = ('clinica', 'numero')
        #db_table = 'sala'
        verbose_name = 'Sala'
        verbose_name_plural = '(S2) Salas'
        unique_together = ('clinica', 'numero')


    def __str__(self):
        #return f"Sala {self.numero} - {self.clinica.nome}"
        return f"{self.nome}"

# Cálculos

    def calcular_custo_hora(self, mes=None, ano=None):
        from django.utils import timezone
        from django.db.models import Sum

        agora = timezone.now()
        mes = mes or agora.month
        ano = ano or agora.year

        # CONVERTE TUDO PRA INT MESMO SE FOR STRING
        try:
            dias = int(float(Parametro.get_valor('DIAS', '22')))
            horas = int(float(Parametro.get_valor('HORAS', '8')))
        except:
            dias = 22
            horas = 8

        total_horas = max(dias * horas, 1)

        fixo = self.custos_fixos.filter(mes_referencia=mes, ano_referencia=ano)\
                                .aggregate(s=Sum('valor_mensal'))['s'] or 0
        var  = self.custos_variaveis.filter(mes_referencia=mes, ano_referencia=ano)\
                                    .aggregate(s=Sum('valor_mensal'))['s'] or 0

        resultado = (fixo + var) / total_horas
        res = round(float(resultado), 2)
        return res   # ← TEM QUE RETORNAR SÓ O NÚMERO!

    calcular_custo_hora.short_description = "Custo/Hora"


# Deixo só o FK pra Sala:
class CustoFixoSala(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='custos_fixos')
    nome_item = UpperCharField(max_length=64)
    valor_mensal = models.FloatField()
    mes_referencia = models.PositiveSmallIntegerField()
    ano_referencia = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100)
        ]
    )
    class Meta:
        unique_together = ('sala', 'nome_item', 'mes_referencia', 'ano_referencia')
    #    db_table = 'custovariavelsala'
        verbose_name = 'Custo Fixo Sala'
        verbose_name_plural = '(S3) Custo Fixo Sala'

# Deixo só o FK pra Sala:

class CustoVariavelSala(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='custos_variaveis')
    nome_item = UpperCharField(max_length=64)
    valor_mensal = models.FloatField()
    mes_referencia = models.PositiveSmallIntegerField()
    ano_referencia = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100)
        ]
    )

    class Meta:
        unique_together = ('sala', 'nome_item', 'mes_referencia', 'ano_referencia')
    #    db_table = 'custovariavelsala'
        verbose_name = 'Custo Variável Sala'
        verbose_name_plural = '(S4) Custo Variável Sala'

#-------------------- Novos Models

#--------------------------------
class Procedimento(models.Model):
#--------------------------------
#     
    clinica = models.ForeignKey(
        'Clinica',  # ajuste conforme seu app de Clínica
        on_delete=models.CASCADE,
        related_name='procedimentos',
        verbose_name='Clínica'
    )
    codigo    = UpperCharField('Código', max_length=20, unique=True, blank=False, null=False, default='Novo',
            help_text=_("Informe o Código do Procedimento. Obrigatório!"))
    nome      = UpperCharField('Nome do Procedimento', max_length=200, blank=False, null=False,
            help_text=_("Informe o Nome do Procedimento. Obrigatório!"))
    categoria = models.ForeignKey(
        'clinicas.Categoria',
        on_delete=models.PROTECT,        # impede exclusão acidental
        null=False,        # explícito: não aceita NULL no banco
        blank=False,       # explícito: não aceita vazio no form/admin
        default='1',
        related_name='procedimentos',
        verbose_name=_('Categoria'),
        help_text=_('Escolha a Categoria do Procedimento. Obrigatório!'),
    )
    descricao = UpperCharField('Descrição', max_length=256, blank=True, null=True,
            help_text=_("Informe a Descrição do Procedimento. Opcional!"))
    tempo_estimado = models.PositiveIntegerField(
        null=True, blank=True, help_text="Tempo em minutos!"
    )
    status = models.CharField(
        max_length=20,
        choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')],
        default='ativo'
    )
    #data_criacao = models.DateTimeField(auto_now_add=True)
    #data_atualizacao = models.DateTimeField(auto_now=True)
    data_criacao = models.DateTimeField(_('Data Criação'), default=timezone.now)
    data_atualizacao = models.DateTimeField(_('Data Atualização'), auto_now=True)

    class Meta:
        unique_together = ('clinica', 'codigo')
        ordering = ['nome']
        verbose_name = _('Procedimento')
        verbose_name_plural = _('(P1) Procedimentos')

    def __str__(self):
        return f"[{self.codigo or 'S/N'}] {self.nome}"
    


#----------------------------
class Convenio(models.Model):
#----------------------------
#     
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='convenios',
        verbose_name=_('Clínica')
    )
    nome      = UpperCharField('Nome', max_length=128,
            help_text=_("Informe o Nome do Convênio. Obrigatório!"))
    descricao = UpperCharField('Descrição', max_length=128, null=True, blank=True,
            help_text=_("Informe a Descrição do Convênio. Opcional!"))
    fator_reajuste = models.DecimalField('Fator de Reajuste',
        max_digits=5, decimal_places=4, default=Decimal('1.0000'),
            help_text=_("Informe o Fator de Reajuste. Obrigatório!"))
        
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Convênio')
        verbose_name_plural = _('(C5) Convênios')
        unique_together = ('clinica', 'nome')

    def __str__(self):
        return f"{self.nome} ({self.clinica})"

#-------------------------------
class TabelaPreco(models.Model):
#-------------------------------
#     
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='tabelas_preco',
        verbose_name='Clínica'
    )
    procedimento = models.ForeignKey(
        Procedimento,
        on_delete=models.PROTECT,
        related_name='tabelas_preco'
    )
    convenio = models.ForeignKey(
        Convenio,
        on_delete=models.PROTECT,
        related_name='tabelas_preco'
    )

    custo_total = models.DecimalField(max_digits=12, decimal_places=2)
    margem_desejada = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    preco_base = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    taxas_adicionais = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    preco_venda = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    margem_efetiva = models.DecimalField(max_digits=6, decimal_places=2, editable=False)
    status_margem = models.CharField(max_length=20, default='OK', editable=False)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('clinica', 'procedimento', 'convenio')
        verbose_name = 'Tabela de Preço'
        verbose_name_plural = '(P2) Tabela de Preços'

    def __str__(self):
        return f"{self.procedimento} - {self.convenio} - R$ {self.preco_venda}"

    def save(self, *args, **kwargs):
        self.calcular_preco()
        super().save(*args, **kwargs)

    def calcular_preco(self):
        from clinicas.models import Parametro

        # Margem padrão
        if self.margem_desejada is None:
            param = Parametro.objects.filter(nome='Margem Lucro Padrão').first()
            self.margem_desejada = Decimal(param.valor) if param else Decimal('30.00')

        # Taxas padrão
        if self.taxas_adicionais is None:
            param = Parametro.objects.filter(nome='ISS').first()
            self.taxas_adicionais = Decimal(param.valor) if param else Decimal('5.00')

        # Cálculos
        self.preco_base = self.custo_total * (1 + self.margem_desejada / 100)
        self.preco_venda = self.preco_base * (1 + self.taxas_adicionais / 100)

        # Aplica fator do convênio
        if self.convenio.fator_reajuste != Decimal('1.0000'):
            self.preco_venda = self.preco_venda * self.convenio.fator_reajuste

        # Margem efetiva
        if self.custo_total > 0:
            self.margem_efetiva = ((self.preco_venda - self.custo_total) / self.custo_total) * 100
        else:
            self.margem_efetiva = Decimal('0.00')

        # Status da margem
        padrao = Parametro.objects.filter(nome='Margem Lucro Padrão').first()
        margem_min = Decimal(padrao.valor) * Decimal('0.5') if padrao else Decimal('15.00')

        if self.margem_efetiva <= 0:
            self.status_margem = 'Prejuízo'
        elif self.margem_efetiva < margem_min:
            self.status_margem = 'Baixa'
        else:
            self.status_margem = 'OK'

    def to_dict(self):
        return {
            'id': self.id,
            'procedimento_nome': self.procedimento.nome,
            'convenio_nome': self.convenio.nome,
            'custo_total': float(self.custo_total),
            'preco_venda': float(self.preco_venda),
            'margem_efetiva': float(self.margem_efetiva),
            'status_margem': self.status_margem,
            'data_atualizacao': self.data_atualizacao.isoformat(),
        }

#----------------------------------
class HistoricoPreco(models.Model):
#----------------------------------
#
    clinica = models.ForeignKey(
        'Clinica',  # ajuste conforme seu app de Clínica
        on_delete=models.CASCADE,
        related_name='historicos',
        verbose_name='Clínica'
    )
     
    tabela_preco = models.ForeignKey(
        TabelaPreco,
        on_delete=models.CASCADE,
        related_name='historicos'
    )
    custo_total_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    preco_venda_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    motivo_alteracao = UpperCharField('Motivo', max_length=128)

    class Meta:
        verbose_name = 'Histórico de Preço'
        verbose_name_plural = '(P3) Histórico de Preços'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f"Alteração {self.tabela_preco} em {self.data_alteracao.date()}"
    
#-----------------------------
class ItemCusto(models.Model):
#-----------------------------
#
    clinica = models.ForeignKey(
        'Clinica',  # ajuste conforme seu app de Clínica
        on_delete=models.CASCADE,
        related_name='itens_custo',
        verbose_name='Clínica'
    )
    procedimento = models.ForeignKey(
        Procedimento,
        on_delete=models.CASCADE,
        related_name='itens_custo'
    )
    categoria_custo = models.ForeignKey(
        'Categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_custos'
    )
    
    referencia_parametro = models.ForeignKey(
        'clinicas.Parametro',  # ou só Parametro se estiver no mesmo app
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_custo_referencia',
        help_text="Se preenchido, ignora custo_unitario e usa o valor atual do parâmetro"
    )
    nome       = UpperCharField('Nome Ítem', max_length=32)
    quantidade = models.DecimalField('Qtde Ítem',
        max_digits=10, decimal_places=4, default=Decimal('1.0000'),
        validators=[MinValueValidator(Decimal('0.0001'))]
    )
    unidade_medida = UpperCharField('Unid Medida', max_length=8, blank=True, null=True)
    custo_unitario = models.DecimalField(
        max_digits=12, decimal_places=4,
        help_text="Valor fixo OU será Sobrescrito"
    )

    class Meta:
        unique_together = ('clinica', 'nome')
        verbose_name = 'Ítem de Custo'
        verbose_name_plural = '(S5) Ítens de Custo'



#aqui

#-------------------- Fim -------------------------    