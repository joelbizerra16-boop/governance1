from django.http import HttpResponse
from django.template.loader import render_to_string
from dashboard.models import Reuniao
from xhtml2pdf import pisa
import io
from datetime import date, timedelta
import calendar


def reunioes_pdf(request):
    # Copia da lógica de recorrência utilizada na listagem para calcular 'faltam' e próxima ocorrência
    def add_months(d: date, months: int) -> date:
        y = d.year + (d.month - 1 + months) // 12
        m = (d.month - 1 + months) % 12 + 1
        last_day = calendar.monthrange(y, m)[1]
        return date(y, m, min(d.day, last_day))

    def avancar(d: date, rec: str) -> date:
        if rec == 'Diaria':
            return d + timedelta(days=1)
        if rec == 'Semanal':
            return d + timedelta(days=7)
        if rec == 'Quinzenal':
            return d + timedelta(days=15)
        if rec == 'Mensal':
            return add_months(d, 1)
        if rec == 'Bimestral':
            return add_months(d, 2)
        if rec == 'Trimestral':
            return add_months(d, 3)
        if rec == 'Semestral':
            return add_months(d, 6)
        return d  # Unica

    hoje = date.today()
    reunioes_data = []
    for r in Reuniao.objects.all().order_by('data', 'hora'):
        rec = (r.recorrencia or 'Unica')
        # Próxima ocorrência e faltam
        if rec == 'Unica':
            prox = r.data
        else:
            ocorrencia = r.data
            safe_guard = 0
            while ocorrencia <= hoje and safe_guard < 400:
                ocorrencia = avancar(ocorrencia, rec)
                safe_guard += 1
            prox = ocorrencia
        delta = (prox - hoje).days
        if delta > 0:
            faltam_str = f"{delta} dias"
        elif delta == 0:
            faltam_str = "Hoje"
        else:
            faltam_str = "Realizada"
        reunioes_data.append({
            'titulo': getattr(r, 'titulo', ''),
            'data': getattr(r, 'data', None),
            'proxima': prox,
            'hora': getattr(r, 'hora', None),
            'recorrencia': getattr(r, 'recorrencia', ''),
            'local': getattr(r, 'local', ''),
            'participantes': getattr(r, 'participantes', ''),
            'faltam': faltam_str,
        })

    html = render_to_string('dashboard/reunioes/pdf.html', {
        'reunioes': reunioes_data,
    })
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8')
    if hasattr(pisa_status, 'err') and pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=reunioes.pdf'
    return response
