from django.shortcuts import get_object_or_404, render
from banco_dados.models import Tarefa

def tarefa_visualizar(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    return render(request, 'dashboard/tarefas/visualizar.html', {'tarefa': tarefa})
