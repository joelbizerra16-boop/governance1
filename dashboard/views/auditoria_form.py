from django.contrib.auth.decorators import login_required
from dashboard.models import AgendaAuditoria
from banco_dados.models import Projeto
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden

def auditoria_form(request, auditoria_id=None):
    if auditoria_id:
        auditoria = get_object_or_404(AgendaAuditoria, id=auditoria_id)
        if hasattr(request.user, 'profile'):
            if auditoria.unidade != request.user.profile.unidade:
                return HttpResponseForbidden('Você só pode editar auditorias da sua unidade.')
    else:
        auditoria = None
    if request.method == 'POST':
        from datetime import date, datetime
        tipo_auditoria = request.POST.get('tipo_auditoria')
        projeto_id = request.POST.get('projeto')
        data = request.POST.get('data')
        hora = request.POST.get('hora')
        unidade = request.POST.get('unidade')
        responsavel = request.POST.get('responsavel') or ''
        projeto = Projeto.objects.get(id=projeto_id) if projeto_id else None
        ultimo_editor = request.user if request.user.is_authenticated else None
        erro_data = None
        # Se data vazia, salva como 'Ag. Agenda'. Se menor que hoje, erro.
        if not data:
            from datetime import date
            data_valor = date(1900, 1, 1)  # valor mínimo para evitar None
            status_valor = 'Ag. Agenda'
        else:
            try:
                data_valor = datetime.strptime(data, '%Y-%m-%d').date()
                if data_valor < date.today():
                    erro_data = 'A data não pode ser menor que hoje.'
            except Exception:
                erro_data = 'Data inválida.'
            status_valor = None
        if erro_data:
            projetos = Projeto.objects.all()
            return render(request, 'dashboard/auditorias/form.html', {
                'auditoria': auditoria,
                'projetos': projetos,
                'form': auditoria,
                'erro_data': erro_data,
            })
        if auditoria:
            auditoria.tipo_auditoria = tipo_auditoria
            auditoria.projeto = projeto
            auditoria.data = data_valor
            auditoria.hora = hora
            auditoria.unidade = unidade
            auditoria.responsavel = responsavel
            if status_valor:
                auditoria.status = status_valor
            auditoria.ultimo_editor = ultimo_editor
            auditoria.save()
        else:
            auditoria = AgendaAuditoria.objects.create(
                tipo_auditoria=tipo_auditoria,
                projeto=projeto,
                data=data_valor,
                hora=hora,
                unidade=unidade,
                responsavel=responsavel,
                status=status_valor if status_valor else '',
                ultimo_editor=ultimo_editor
            )
        return redirect('dashboard:lista_auditorias')
    projetos = Projeto.objects.all()
    return render(request, 'dashboard/auditorias/form.html', {
        'auditoria': auditoria,
        'projetos': projetos,
        'form': auditoria,
    })
