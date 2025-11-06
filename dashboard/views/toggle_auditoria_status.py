from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from dashboard.models import AgendaAuditoria


# POST-only; responde 401 JSON em vez de redirecionar se não autenticado
@require_POST
def toggle_auditoria_status(request, auditoria_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'auth required'}, status=401)
    """Toggle status between 'Pendente' (Aguardando) and 'Agendada' (Confirmado).

    We reuse existing STATUS_CHOICES without a schema change. UI maps:
    - Pendente -> Aguardando
    - Agendada -> Confirmado
    """
    auditoria = get_object_or_404(AgendaAuditoria, pk=auditoria_id)
    current = (auditoria.status or '').strip()
    if current == 'Agendada':
        auditoria.status = 'Pendente'
    else:
        auditoria.status = 'Agendada'
    auditoria.save(update_fields=['status'])

    # Para o frontend: 'Agendada' = Confirmado (azul), 'Pendente' = Aguardando (amarelo)
    ui_status = 'Confirmado' if auditoria.status == 'Agendada' else 'Aguardando'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': ui_status})
    # Fallback para POSTs normais (sem AJAX): redireciona de volta
    return redirect(request.META.get('HTTP_REFERER', reverse('dashboard:lista_auditorias')))
