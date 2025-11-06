from django.http import HttpResponse
from django.template.loader import render_to_string
from dashboard.models import Projeto
from banco_dados.models import Tarefa
from xhtml2pdf import pisa
import io

def projeto_pdf(request, projeto_id):
    projeto = Projeto.objects.get(pk=projeto_id)
    # Tarefas associadas via FK e M2M, removendo duplicados
    tarefas_fk = Tarefa.objects.filter(projeto=projeto)
    tarefas_m2m = projeto.tarefas_associadas.all()
    tarefas = list(set(list(tarefas_fk) + list(tarefas_m2m)))
    # Calcula o status do projeto como média das porcentagens das tarefas
    total = len(tarefas)
    if total > 0:
        def parse_status(t):
            val = getattr(t, 'status', '0')
            if isinstance(val, str) and '%' in val:
                try:
                    return int(val.replace('%',''))
                except:
                    return 0
            try:
                return int(val)
            except:
                return 0
        status_sum = sum(parse_status(t) for t in tarefas)
        status_percent = int(status_sum / total)
    else:
        status_percent = 0
    html_string = render_to_string('dashboard/projetos/pdf.html', {
        'projeto': projeto,
        'tarefas': tarefas,
        'status_percent': status_percent,
    })
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html_string,
        dest=result,
        encoding='utf-8'
    )
    if hasattr(pisa_status, 'err') and pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=projeto_{projeto_id}.pdf'
    return response
