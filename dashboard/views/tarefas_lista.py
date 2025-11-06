from django.shortcuts import render
from banco_dados.models import Tarefa
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def tarefas_lista(request):
    from django.db.models import Min, Max
    projeto_id = request.GET.get('projeto')
    status = request.GET.get('status')
    sort = request.GET.get('sort')
    ano = request.GET.get('ano')
    q = request.GET.get('q')
    tarefas = Tarefa.objects.all()
    # Busca global: quando houver termo, usa apenas a pesquisa
    if q:
        tarefas = tarefas.filter(
            Q(nome__icontains=q) |
            Q(projeto__nome__icontains=q) |
            Q(responsavel__icontains=q) |
            Q(status__icontains=q)
        )
    else:
        # Não filtra por projeto_id (removido a pedido)
        if status:
            # normaliza status para aceitar '25' ou '25%'
            status_value = status if status.endswith('%') else f"{status}%"
            tarefas = tarefas.filter(status=status_value)
        # Filtro por ano
        if ano:
            tarefas = tarefas.filter(data_inicio__year=ano)
    # Ordenação
    if sort == 'data_inicio_asc':
        tarefas = tarefas.order_by('data_inicio')
    elif sort == 'data_fim_asc':
        tarefas = tarefas.order_by('data_fim')
    # Anos disponíveis
    anos = tarefas.model.objects.values_list('data_inicio__year', flat=True).distinct().order_by('data_inicio__year')
    anos = [a for a in anos if a]
    tarefas_list = []
    for tarefa in tarefas:
        if hasattr(request.user, 'profile'):
            bloqueada = tarefa.projeto.unidade != request.user.profile.unidade
        else:
            bloqueada = False
        setattr(tarefa, 'bloqueada', bloqueada)
        tarefas_list.append(tarefa)
    return render(request, 'dashboard/tarefas/lista.html', {
        'tarefas': tarefas_list,
        'projeto_id': projeto_id,
        'status': status,
        'sort': sort,
        'ano': ano,
        'anos': anos,
        'q': q,
    })
