# clinicas/forms.py
from django import forms
from .models import Equipamento

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = '__all__'
        widgets = {
            'dta_aquisicao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'codigo': 'Código',
            'descricao': 'Descrição',
            'dta_aquisicao': 'Data de Aquisição',
            'vlr_aquisicao': 'Valor de Aquisição (R$)',
            'custo_dia': 'Custo por Dia (R$)',
            'custo_mes': 'Custo por Mês (R$)',
        }