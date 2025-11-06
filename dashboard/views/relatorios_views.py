from django.shortcuts import render
from banco_dados.models import Projeto, Tarefa

def relatorios_lista(request):
    projetos = Projeto.objects.all()
    relatorios = []
    for projeto in projetos:
        tarefas = Tarefa.objects.filter(projeto=projeto)
        relatorios.append({
            'projeto': projeto,
            'tarefas': tarefas,
        })
    return render(request, 'dashboard/relatorios/lista.html', {'relatorios': relatorios})

def criar_relatorio(request):
    # Página de criação de relatório (pode ser expandida depois)
    return render(request, 'dashboard/relatorios/criar.html')
