from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from banco_dados.models import Tarefa

@require_http_methods(["GET", "POST"])
def tarefa_excluir(request, tarefa_id):
    try:
        tarefa = Tarefa.objects.get(id=tarefa_id)
    except Tarefa.DoesNotExist:
        return redirect('/tarefas/')
    if request.method == 'POST':
        projeto_url = '/tarefas/'
        tarefa.delete()
        return redirect(projeto_url)
    return render(request, 'dashboard/tarefas/excluir.html', {'tarefa': tarefa})
