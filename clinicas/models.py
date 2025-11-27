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
    nome = UpperCharField(max_length=64, blank=False, null=False, unique=True)
    cep  = models.CharField(max_length=9, blank=True, null=True)
    logradouro = UpperCharField(max_length=64, blank=True, null=True)
    complemento = UpperCharField(max_length=32, blank=True, null=True)
    bairro = UpperCharField(max_length=64, blank=True, null=True)
    localidade = UpperCharField(max_length=64, blank=True, null=True)
    uf = UpperCharField(max_length=2, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    data_criacao = models.DateTimeField(default=timezone.now)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clinicas'
        verbose_name = 'Clínica'
        verbose_name_plural = 'Clínicas'

    def __str__(self):
        return f'Clínica {self.nome}'

#-- Buscar o CEP para preenchimento do endereço
    def save(self, *args, **kwargs):
        print(f"Salvando o objeto: {self.nome}")

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
        print(f"Objeto salvo com ID: {self.id}")
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

class Parametro(models.Model):
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='parametros'
    )
    codigo = UpperCharField("codigo", max_length=16)  # ← sem unique=True aqui!
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