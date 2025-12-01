# clinicas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('equipamentos/', views.equipamento_list, name='equipamento_list'),
    path('equipamentos/novo/', views.equipamento_add, name='equipamento_add'),
    path('equipamentos/editar/<int:pk>/', views.equipamento_edit, name='equipamento_edit'),
]