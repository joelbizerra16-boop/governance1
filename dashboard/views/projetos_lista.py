from django.shortcuts import render
from banco_dados.models import Projeto

def projetos_lista(request):
    unidade_selecionada = request.GET.get('unidade', '')
    area_selecionada = request.GET.get('area', '')
    busca = request.GET.get('busca', '')
    projetos = Projeto.objects.all()
    if unidade_selecionada:
        projetos = projetos.filter(unidade=unidade_selecionada)
    if area_selecionada:
        projetos = projetos.filter(area_responsavel=area_selecionada)
    if busca:
        projetos = projetos.filter(nome__icontains=busca)
    areas = Projeto._meta.get_field('area_responsavel').choices
    unidades = Projeto._meta.get_field('unidade').choices
    # Calcular média do status das tarefas para cada projeto
    from banco_dados.models import Tarefa
    def parse_status(tarefa):
        s = str(getattr(tarefa, 'status', '0')).replace('%','').strip()
        try:
            return int(s)
        except Exception:
            return 0
    projetos_status = {}
    for projeto in projetos:
        tarefas_fk = Tarefa.objects.filter(projeto_id=projeto.id)
        tarefas_m2m = projeto.tarefas_associadas.all()
        tarefas = list({t.id: t for t in list(tarefas_fk) + list(tarefas_m2m)}.values())
        total = len(tarefas)
        if total > 0:
            status_sum = sum(parse_status(t) for t in tarefas)
            status_percent = int(status_sum / total)
        else:
            status_percent = 0
        projetos_status[projeto.id] = status_percent
    return render(request, 'dashboard/projetos/lista.html', {
        'projetos': projetos,
        'areas': areas,
        'unidades': unidades,
        'unidade_selecionada': unidade_selecionada,
        'area_selecionada': area_selecionada,
        'busca': busca,
        'projetos_status': projetos_status,
    })
