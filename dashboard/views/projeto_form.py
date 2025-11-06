from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from banco_dados.models import Projeto, AreaResponsavel, Unidade, Tarefa
from django.contrib.auth.decorators import login_required

def projeto_form(request, projeto_id=None):
    if projeto_id:
        projeto = Projeto.objects.get(id=projeto_id)
        if hasattr(request.user, 'profile'):
            if projeto.unidade != request.user.profile.unidade:
                return HttpResponseForbidden('Você só pode editar projetos da sua unidade.')
    else:
        projeto = None
    if request.method == 'POST':
        nome = request.POST.get('nome')
        responsavel = request.POST.get('responsavel')
        area_responsavel = request.POST.get('area_responsavel')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        unidade = request.POST.get('unidade')
        status = request.POST.get('status')
        observacao = request.POST.get('observacao', '')
        if not status:
            status = 0
        tarefas_ids = request.POST.getlist('tarefas_associadas')
        if projeto:
            projeto.nome = nome
            projeto.responsavel = responsavel
            projeto.area_responsavel = area_responsavel
            projeto.data_inicio = data_inicio
            projeto.data_fim = data_fim
            projeto.unidade = unidade
            projeto.status = status
            projeto.observacao = observacao
            projeto.save()
        else:
            usuario = request.user if request.user.is_authenticated else None
            projeto = Projeto.objects.create(
                nome=nome,
                responsavel=responsavel,
                area_responsavel=area_responsavel,
                data_inicio=data_inicio,
                data_fim=data_fim,
                unidade=unidade,
                status=status if status is not None else 0,
                usuario=usuario,
                observacao=observacao
            )
        tarefas = Tarefa.objects.filter(id__in=[tid.strip() for tid in tarefas_ids if tid.strip().isdigit()])
        projeto.tarefas_associadas.set(tarefas)
        projeto.save()
        return redirect('dashboard:projetos_lista')
    areas = AreaResponsavel.choices
    unidades = Unidade.choices
    tarefas_associadas_ids = [t.id for t in projeto.tarefas_associadas.all()] if projeto else []
    tarefas = Tarefa.objects.all()
    return render(request, 'dashboard/projetos/form.html', {
        'projeto': projeto,
        'areas': areas,
        'unidades': unidades,
        'tarefas': tarefas,
        'tarefas_associadas_ids': tarefas_associadas_ids,
    })
