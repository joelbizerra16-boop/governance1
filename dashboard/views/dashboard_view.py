from django.shortcuts import render
from django.db.models import Q, Avg
from django.utils import timezone
from banco_dados.models import Projeto, Tarefa
from dashboard.models import Reuniao, AgendaAuditoria
from datetime import timedelta, date
import calendar

def dashboard_view(request):
    # Filtros
    ano = request.GET.get('ano') or ''
    planta = request.GET.get('planta') or ''
    status_filter = request.GET.get('status') or ''

    projetos_qs = Projeto.objects.all()
    if ano:
        try:
            ano_int = int(ano)
            projetos_qs = projetos_qs.filter(data_inicio__year__lte=ano_int, data_fim__year__gte=ano_int)
        except ValueError:
            pass
    if planta and planta != 'Todas':
        # Inclui projetos marcados como 'Todas' para aparecerem em qualquer planta específica
        projetos_qs = projetos_qs.filter(Q(unidade=planta) | Q(unidade='Todas'))
    if status_filter:
        try:
            status_int = int(status_filter)
            projetos_qs = projetos_qs.filter(status=status_int)
        except ValueError:
            pass

    # Indicadores
    total_projetos = projetos_qs.count()
    tarefas_qs = Tarefa.objects.filter(projeto__in=projetos_qs)
    total_tarefas = tarefas_qs.count()
    # Conclusão média como taxa de projetos concluídos (100%) entre os filtrados
    # Critério de conclusão do projeto segue a lista de projetos: média das tarefas (FK + M2M);
    # se não houver tarefas, usa o status do próprio projeto.
    media_conclusao = 0
    if total_projetos:
        def parse_status_val(val):
            try:
                return int(str(val).replace('%','').strip())
            except Exception:
                return 0
        concluidos = 0
        for prj in projetos_qs:
            tarefas_fk = Tarefa.objects.filter(projeto_id=prj.id)
            tarefas_m2m = prj.tarefas_associadas.all()
            tarefas = list({t.id: t for t in list(tarefas_fk) + list(tarefas_m2m)}.values())
            if tarefas:
                prj_percent = int(sum(parse_status_val(getattr(t, 'status', '0')) for t in tarefas) / len(tarefas))
            else:
                prj_percent = int(getattr(prj, 'status', 0) or 0)
            if prj_percent >= 100:
                concluidos += 1
    media_conclusao = round((concluidos / total_projetos) * 100)
    # Por solicitação: inverter o resultado (1 - taxa) para refletir visão desejada
    media_conclusao = max(0, min(100, 100 - media_conclusao))

    hoje = timezone.localdate()
    projetos_atrasados = projetos_qs.filter(data_fim__lt=hoje, status__lt=100).count()

    # Tarefas críticas (próximos 7 dias e não concluídas)
    em_7_dias = hoje + timedelta(days=7)
    def status_to_int(s):
        try:
            return int((s or '0%').replace('%',''))
        except Exception:
            return 0
    tarefas_criticas = (
        tarefas_qs
        .filter(data_fim__isnull=False, data_fim__gte=hoje, data_fim__lte=em_7_dias)
        .exclude(status='100%')
        .order_by('data_fim')[:5]
    )

    # Próximas reuniões
    proximas_reunioes = Reuniao.objects.filter(data__gte=hoje).order_by('data','hora')[:5]

    # Anos disponíveis para filtro (a partir de projetos)
    anos = sorted({p.data_inicio.year for p in Projeto.objects.all()} | {p.data_fim.year for p in Projeto.objects.all()})

    # Evolução mensal (média de conclusão dos projetos ativos no mês)
    base_year = None
    try:
        base_year = int(ano) if ano else hoje.year
    except ValueError:
        base_year = hoje.year

    def month_range(y, m):
        first = date(y, m, 1)
        last = date(y, m, calendar.monthrange(y, m)[1])
        return first, last

    plantas = ["Santo André", "Gravataí"]
    evolucao_chart = {
        "labels": [
            "Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"
        ],
        "datasets": []
    }
    # Evolução (taxa): percentual acumulado de projetos concluídos (status=100)
    # até o fim de cada mês, por planta (inclui 'Todas').
    # Tratamos a data efetiva de conclusão como min(data_fim, hoje) para refletir 100% já concluído.
    for pl in plantas:
        base_pl = projetos_qs.filter(Q(unidade=pl) | Q(unidade='Todas'))
        total_pl = base_pl.count()
        concluidos = list(base_pl.filter(status=100))
        perc_series = []
        count_series = []
        for m in range(1,13):
            _, fim = month_range(base_year, m)
            count = 0
            for p in concluidos:
                cdate = getattr(p, 'data_fim', None)
                eff = cdate if (cdate and cdate <= hoje) else hoje
                if eff <= fim:
                    count += 1
            count_series.append(count)
            perc = round((count / total_pl) * 100) if total_pl else 0
            perc_series.append(perc)
        evolucao_chart["datasets"].append({
            "label": pl,
            "data": perc_series,
            "counts": count_series,
            "total": total_pl,
        })

    # Auditorias: realizadas x planejadas por mês (ano/planta)
    aud_qs = AgendaAuditoria.objects.all()
    if ano:
        try:
            aud_qs = aud_qs.filter(data__year=int(ano))
        except ValueError:
            pass
    if planta and planta != 'Todas':
        aud_qs = aud_qs.filter(unidade=planta)

    realizados = []
    planejados = []
    # Realizadas: considerar auditorias já ocorridas (data <= hoje) e não canceladas,
    # mesmo que o status não tenha sido atualizado para 'Concluída'.
    # Planejadas: auditorias marcadas como 'Agendada' ou 'Pendente'.
    for m in range(1,13):
        realizados.append(
            aud_qs.filter(data__month=m, data__lte=hoje).exclude(status='Cancelada').count()
        )
        planejados.append(
            aud_qs.filter(data__month=m, status__in=['Agendada','Pendente']).count()
        )
    auditorias_chart = {
        "labels": ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"],
        "datasets": [
            {"label":"Planejadas","data": planejados},
            {"label":"Realizadas","data": realizados},
        ]
    }


    # Dados para gráficos
    status_buckets = [0, 25, 50, 75, 100]
    status_labels = ["0%","25%","50%","75%","100%","Outros"]

    # Projetos por status por planta
    plantas = ["Santo André", "Gravataí"]
    projetos_chart = {
        "labels": status_labels,
        "datasets": []
    }
    for pl in plantas:
        # Inclui também projetos globais ('Todas') para a contagem por status
        qs_pl = projetos_qs.filter(Q(unidade=pl) | Q(unidade='Todas'))
        counts = []
        for s in status_buckets:
            counts.append(qs_pl.filter(status=s).count())
        outros = qs_pl.exclude(status__in=status_buckets).count()
        counts.append(outros)
        projetos_chart["datasets"].append({
            "label": pl,
            "data": counts,
        })

    # Tarefas por status (donut)
    tarefas_labels = ["0%","25%","50%","75%","100%","Outros"]
    t_counts = [
        tarefas_qs.filter(status='0%').count(),
        tarefas_qs.filter(status='25%').count(),
        tarefas_qs.filter(status='50%').count(),
        tarefas_qs.filter(status='75%').count(),
        tarefas_qs.filter(status='100%').count(),
        tarefas_qs.exclude(status__in=['0%','25%','50%','75%','100%']).count(),
    ]
    tarefas_chart = {
        "labels": tarefas_labels,
        "data": t_counts,
    }

    contexto = {
        'f_ano': ano,
        'f_planta': planta,
        'f_status': status_filter,
        'anos': anos,
        'total_projetos': total_projetos,
        'total_tarefas': total_tarefas,
        'media_conclusao': media_conclusao,
        'projetos_atrasados': projetos_atrasados,
        'tarefas_criticas': tarefas_criticas,
        'proximas_reunioes': proximas_reunioes,
        'projetos_chart': projetos_chart,
        'tarefas_chart': tarefas_chart,
        'evolucao_chart': evolucao_chart,
        'auditorias_chart': auditorias_chart,
    }
    return render(request, 'dashboard/dashboard.html', contexto)
