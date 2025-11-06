from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from banco_dados.models import Projeto

@require_http_methods(["GET", "POST"])
def projeto_excluir(request, projeto_id):
    try:
        projeto = Projeto.objects.get(id=projeto_id)
    except Projeto.DoesNotExist:
        return redirect('/')
    if request.method == 'POST':
        projeto.delete()
        return redirect('/')
    return render(request, 'dashboard/projetos/excluir.html', {'projeto': projeto})
