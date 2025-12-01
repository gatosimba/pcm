# clinicas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Equipamento, Clinica
from .forms import EquipamentoForm

@login_required
def equipamento_list(request):
    # Só mostra equipamentos da clínica do usuário
    equipamentos = Equipamento.objects.filter(clinica__user=request.user).select_related('clinica')
    return render(request, 'clinicas/equipamento_list.html', {'equipamentos': equipamentos})

@login_required
def equipamento_add(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            equipamento = form.save(commit=False)
            # Garante que só salva na clínica do usuário
            clinica = Clinica.objects.filter(user=request.user).first()
            if not clinica:
                messages.error(request, "Você não tem clínica cadastrada.")
                return redirect('equipamento_add')
            equipamento.clinica = clinica
            equipamento.save()
            messages.success(request, "Equipamento cadastrado com sucesso!")
            return redirect('equipamento_list')
    else:
        form = EquipamentoForm()
        # Filtra apenas as clínicas do usuário logado
        form.fields['clinica'].queryset = Clinica.objects.filter(user=request.user)
        if Clinica.objects.filter(user=request.user).count() == 1:
            form.fields['clinica'].initial = Clinica.objects.filter(user=request.user).first()

    return render(request, 'clinicas/equipamento_form.html', {'form': form, 'title': 'Novo Equipamento'})

@login_required
def equipamento_edit(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk, clinica__user=request.user)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipamento atualizado!")
            return redirect('equipamento_list')
    else:
        form = EquipamentoForm(instance=equipamento)
        form.fields['clinica'].queryset = Clinica.objects.filter(user=request.user)

    return render(request, 'clinicas/equipamento_form.html', {'form': form, 'title': 'Editar Equipamento'})