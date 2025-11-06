from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponseRedirect
from banco_dados.models import Tarefa

@login_required
@require_POST
def toggle_tarefa_concluida(request, tarefa_id):
    tarefa = Tarefa.objects.get(id=tarefa_id)
    if tarefa.projeto.unidade != request.user.profile.unidade:
        return HttpResponseForbidden('Você só pode alterar tarefas da sua unidade.')
    tarefa.concluida = not tarefa.concluida
    tarefa.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/tarefas/'))
