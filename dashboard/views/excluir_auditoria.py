from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from dashboard.models import AgendaAuditoria

def excluir_auditoria(request, auditoria_id):
    try:
        auditoria = AgendaAuditoria.objects.get(id=auditoria_id)
    except AgendaAuditoria.DoesNotExist:
        return render(request, 'dashboard/auditorias/nao_encontrada.html', {
            'auditoria_id': auditoria_id
        })
    if hasattr(request.user, 'profile'):
        if auditoria.unidade != request.user.profile.unidade:
            return HttpResponseForbidden('Você só pode excluir auditorias da sua unidade.')
    auditoria.delete()
    return redirect('dashboard:lista_auditorias')
