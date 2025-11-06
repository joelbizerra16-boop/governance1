from django.shortcuts import render
from banco_dados.models import Projeto, Tarefa

def projeto_visualizar(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    # Tarefas associadas via FK (projeto) ou via M2M (tarefas_associadas)
    tarefas_fk = Tarefa.objects.filter(projeto_id=projeto_id)
    tarefas_m2m = projeto.tarefas_associadas.all()
    tarefas = list({t.id: t for t in list(tarefas_fk) + list(tarefas_m2m)}.values())
    # Calcular média do status das tarefas
    def parse_status(tarefa):
        s = str(getattr(tarefa, 'status', '0')).replace('%','').strip()
        try:
            return int(s)
        except Exception:
            return 0
    total = len(tarefas)
    if total > 0:
        status_sum = sum(parse_status(t) for t in tarefas)
        status_percent = int(status_sum / total)
    else:
        status_percent = 0
    return render(request, 'dashboard/projetos/visualizar.html', {
        'projeto': projeto,
        'tarefas_relacionadas': tarefas,
        'status_percent': status_percent,
    })
