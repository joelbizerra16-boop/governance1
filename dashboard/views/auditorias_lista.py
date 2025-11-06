from django.contrib.auth.decorators import login_required
from dashboard.models import AgendaAuditoria
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

@login_required
def auditorias_lista(request):
    from datetime import date
    order = request.GET.get('order', 'asc')
    unidade = request.GET.get('unidade', '')
    ano = request.GET.get('ano', '')
    order_falta = request.GET.get('order_falta', '')
    qs = AgendaAuditoria.objects.all()
    # Gerar lista de anos únicos presentes nas auditorias
    anos = qs.dates('data', 'year').distinct()
    if unidade:
        qs = qs.filter(unidade=unidade)
    if ano:
        qs = qs.filter(data__year=ano)
    if order == 'asc':
        auditorias = qs.order_by('data', 'hora')
    else:
        auditorias = qs.order_by('-data', '-hora')
    auditorias_com_dias = []
    hoje = date.today()
    for auditoria in auditorias:
        dias_falta = (auditoria.data - hoje).days
        auditorias_com_dias.append({
            'id': auditoria.pk,
            'tipo_auditoria': getattr(auditoria, 'tipo_auditoria', ''),
            'data': getattr(auditoria, 'data', ''),
            'hora': getattr(auditoria, 'hora', ''),
            'unidade': getattr(auditoria, 'unidade', ''),
            'status': getattr(auditoria, 'status', ''),
            'dias_falta': dias_falta,
        })
    if order_falta == 'asc':
        auditorias_com_dias.sort(key=lambda x: x['dias_falta'])
    return render(request, 'dashboard/auditorias/lista.html', {
        'auditorias': auditorias_com_dias,
        'anos': [a.year for a in anos],
    })
