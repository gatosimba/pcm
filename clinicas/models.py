from django.db import models
from django.conf import settings   # ← essa é a forma padrão e mais segura
from django.contrib.auth.models import User

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import admin


import requests
import logging
import re

#from pcm import settings

logger = logging.getLogger(__name__)

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
        related_name='clinicas'   # importante!
    )
    nome = UpperCharField('Clínica',max_length=64, blank=False, null=False, unique=True)
    cep  = models.CharField('CEP' ,max_length=9, blank=True, null=True)
    logradouro = UpperCharField('Logradouro',max_length=64, blank=True, null=True)
    complemento = UpperCharField('Complemento', max_length=32, blank=True, null=True)
    bairro = UpperCharField('Bairro', max_length=64, blank=True, null=True)
    localidade = UpperCharField('Cidade', max_length=64, blank=True, null=True)
    uf = UpperCharField('Estado',max_length=2, blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativa')
    data_criacao = models.DateTimeField(default=timezone.now)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clinicas'
        verbose_name = 'Clínica'
        verbose_name_plural = 'Clínicas'

    def __str__(self):
        return f'{self.nome},{self.status}'

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
    valor = models.CharField("Valor", max_length=200)
    descricao = UpperCharField("Descrição", max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.clinica.nome}"

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"
        # ← ÚNICO POR CLÍNICA, não global!
        unique_together = ('clinica', 'codigo')
        # ou, se estiver usando Django 4.0+:
        # constraints = [
        #     models.UniqueConstraint(fields=['clinica', 'codigo'], name='unique_codigo_per_clinica')
        # ]
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
#    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    codigo = UpperCharField('Código', max_length=16, blank=False, null=False)
    descricao = UpperCharField('Descrição', max_length=128, blank=True, null=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, blank=False, null=False)

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        unique_together = ('clinica', 'codigo')

    def __str__(self):
        return f'{self.codigo} {self.descricao} ({self.get_tipo_display()})'

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
        verbose_name_plural = 'Tipos de Sala'
        unique_together = ('clinica', 'tipo')

    def __str__(self):
        return f'{self.tipo},{self.nome},{self.status}'

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
        verbose_name_plural = 'Equipamentos'
        unique_together = ('clinica', 'codigo')

    def __str__(self):
        return f'{self.codigo},{self.descricao},{self.status}'

#-- No seu model Equipamento, já pode deixar assim (opcional, mas fica lindo no admin):
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
#------------------------
#     
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='salas'
    )
    numero = models.CharField("Número/Nome da Sala", max_length=20)
    descricao = models.CharField("Descrição", max_length=100, blank=True)
    cor = models.CharField(
        "Cor no Agendamento",
        max_length=7,
        default="#007bff",
        help_text="Cor em formato HEX (ex: #ff0000 para vermelho)"
    )
    ativa = models.BooleanField("Ativa?", default=True)

    # ← AQUI É O PODER: vários equipamentos!
    equipamentos = models.ManyToManyField(
        Equipamento,
        related_name='salas',
        blank=True,
        help_text="Selecione os equipamentos que ficam nesta sala"
    )

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        unique_together = ('clinica', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f"Sala {self.numero} - {self.clinica.nome}"

    def get_cor_display(self):
        return f'<span style="color:{self.cor}">■</span> {self.cor}'
    get_cor_display.allow_tags = True
    get_cor_display.short_description = "Cor"    
