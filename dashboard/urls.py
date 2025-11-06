from django.urls import path
from dashboard.views.dashboard_view import dashboard_view
from dashboard.views.projetos_lista import projetos_lista
from dashboard.views.projeto_form import projeto_form
from dashboard.views.projeto_visualizar import projeto_visualizar
from dashboard.views.projeto_excluir import projeto_excluir
from dashboard.views.tarefas_lista import tarefas_lista
from dashboard.views.tarefa_form import tarefa_form
from dashboard.views.tarefa_visualizar import tarefa_visualizar
from dashboard.views.tarefa_excluir import tarefa_excluir
from dashboard.views.toggle_tarefa_concluida import toggle_tarefa_concluida
from dashboard.views.reuniao_views import lista_reunioes, criar_reuniao, editar_reuniao, excluir_reuniao, toggle_reuniao_pause
from dashboard.views.auditorias_lista import auditorias_lista
from dashboard.views.auditoria_form import auditoria_form
from dashboard.views.excluir_auditoria import excluir_auditoria
from dashboard.views.toggle_auditoria_status import toggle_auditoria_status
from dashboard.views.relatorios_views import relatorios_lista, criar_relatorio
from dashboard.views.auditorias_pdf import auditorias_pdf
from dashboard.views.reunioes_pdf import reunioes_pdf

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('projetos/', projetos_lista, name='projetos_lista'),
    path('projetos/criar/', projeto_form, name='criar_projeto'),
    path('projetos/<int:projeto_id>/', projeto_visualizar, name='visualizar_projeto'),
    path('projetos/<int:projeto_id>/editar/', projeto_form, name='editar_projeto'),
    path('projetos/<int:projeto_id>/excluir/', projeto_excluir, name='excluir_projeto'),
    path('projetos/<int:projeto_id>/pdf/', __import__('dashboard.views.projeto_pdf').views.projeto_pdf.projeto_pdf, name='projeto_pdf'),
    path('tarefas/', tarefas_lista, name='tarefas_lista'),
    path('tarefas/criar/', tarefa_form, name='criar_tarefa'),
    path('tarefas/<int:tarefa_id>/editar/', tarefa_form, name='editar_tarefa'),
    path('tarefas/<int:tarefa_id>/', tarefa_visualizar, name='visualizar_tarefa'),
    path('tarefas/<int:tarefa_id>/excluir/', tarefa_excluir, name='excluir_tarefa'),
    path('tarefas/<int:tarefa_id>/toggle_concluida/', toggle_tarefa_concluida, name='toggle_tarefa_concluida'),
    path('reunioes/', lista_reunioes, name='lista_reunioes'),
    path('reunioes/criar/', criar_reuniao, name='criar_reuniao'),
    path('reunioes/<int:reuniao_id>/editar/', editar_reuniao, name='editar_reuniao'),
    path('reunioes/<int:reuniao_id>/excluir/', excluir_reuniao, name='excluir_reuniao'),
    path('reunioes/<int:reuniao_id>/toggle_pause/', toggle_reuniao_pause, name='toggle_reuniao_pause'),
    path('auditorias/', auditorias_lista, name='lista_auditorias'),
    path('auditorias/criar/', auditoria_form, name='criar_auditoria'),
    path('auditorias/<int:auditoria_id>/editar/', auditoria_form, name='editar_auditoria'),
    path('auditorias/<int:auditoria_id>/excluir/', excluir_auditoria, name='excluir_auditoria'),
    path('auditorias/<int:auditoria_id>/toggle_status/', toggle_auditoria_status, name='toggle_auditoria_status'),
    path('relatorios/', relatorios_lista, name='relatorios_lista'),
    path('relatorios/criar/', criar_relatorio, name='criar_relatorio'),
    path('auditorias/pdf/', auditorias_pdf, name='auditorias_pdf'),
    path('reunioes/pdf/', reunioes_pdf, name='reunioes_pdf'),
]
