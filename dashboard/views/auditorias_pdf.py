from django.http import HttpResponse
from django.template.loader import render_to_string
from dashboard.models import AgendaAuditoria
from xhtml2pdf import pisa
import io
from datetime import date

def auditorias_pdf(request):
    order = request.GET.get('order', 'asc')
    unidade = request.GET.get('unidade', '')
    ano = request.GET.get('ano', '')
    qs = AgendaAuditoria.objects.all()
    if unidade:
        qs = qs.filter(unidade=unidade)
    if ano:
        qs = qs.filter(data__year=ano)
    if order == 'asc':
        auditorias = qs.order_by('data', 'hora')
    else:
        auditorias = qs.order_by('-data', '-hora')
    hoje = date.today()
    auditorias_com_dias = []
    for auditoria in auditorias:
        dias_falta = (auditoria.data - hoje).days
        auditorias_com_dias.append({
            'tipo_auditoria': getattr(auditoria, 'tipo_auditoria', ''),
            'data': getattr(auditoria, 'data', ''),
            'hora': getattr(auditoria, 'hora', ''),
            'unidade': getattr(auditoria, 'unidade', ''),
            'status': getattr(auditoria, 'status', ''),
            'dias_falta': dias_falta,
        })
    html_string = render_to_string('dashboard/auditorias/pdf.html', {
        'auditorias': auditorias_com_dias,
    })
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html_string,
        dest=result,
        encoding='utf-8'
    )
    # Observação: em algumas versões, CreatePDF retorna bytes; se falhar, result ficará vazio
    if not result.getvalue():
        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=auditorias.pdf'
    return response
