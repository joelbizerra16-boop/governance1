from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from banco_dados.models import Tarefa, Projeto
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime

def tarefa_form(request, tarefa_id=None):
    if tarefa_id:
        tarefa = Tarefa.objects.get(id=tarefa_id)
        if hasattr(request.user, 'profile'):
            if tarefa.projeto.unidade != request.user.profile.unidade:
                return HttpResponseForbidden('Você só pode editar tarefas da sua unidade.')
    else:
        tarefa = None
    if request.method == 'POST':
        nome = request.POST.get('nome')
        projeto_id = request.POST.get('projeto')
        responsavel = request.POST.get('responsavel')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        observacao = request.POST.get('observacao', '')
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                return None
        data_inicio = parse_date(data_inicio) if data_inicio else None
        data_fim = parse_date(data_fim) if data_fim else None
        concluida = request.POST.get('concluida') == 'on'
        status_raw = request.POST.get('status', '')
        status = f"{status_raw}%" if status_raw else "0%"
        if not projeto_id:
            projetos = Projeto.objects.all()
            return render(request, 'dashboard/tarefas/form.html', {
                'tarefa': tarefa,
                'projetos': projetos,
                'erro': 'Selecione um projeto para a tarefa.'
            })
        projeto = Projeto.objects.get(id=projeto_id)
        # Validação: Data início não pode ser maior que data fim da própria tarefa
        if data_inicio and data_fim and data_inicio > data_fim:
            tarefa_preview = tarefa or Tarefa(
                nome=nome,
                projeto=projeto,
                responsavel=responsavel,
                concluida=concluida,
                data_inicio=data_inicio,
                data_fim=data_fim,
            )
            projetos = Projeto.objects.all()
            return render(request, 'dashboard/tarefas/form.html', {
                'tarefa': tarefa_preview,
                'projetos': projetos,
                'erro_data': 'A data início da tarefa não pode ser maior que a data fim da tarefa.'
            })
        # Validação: Data fim da tarefa não pode exceder a data fim do projeto
        if data_fim and projeto.data_fim and data_fim > projeto.data_fim:
            # Reapresentar o formulário com os valores informados e a mensagem de erro
            tarefa_preview = tarefa or Tarefa(
                nome=nome,
                projeto=projeto,
                responsavel=responsavel,
                concluida=concluida,
                data_inicio=data_inicio,
                data_fim=data_fim,
            )
            projetos = Projeto.objects.all()
            return render(request, 'dashboard/tarefas/form.html', {
                'tarefa': tarefa_preview,
                'projetos': projetos,
                'erro_data': 'A data fim da tarefa é superior à data de conclusão do projeto selecionado.'
            })
        if tarefa:
            tarefa.nome = nome
            tarefa.projeto = projeto
            tarefa.responsavel = responsavel
            tarefa.concluida = concluida
            tarefa.data_inicio = data_inicio
            tarefa.data_fim = data_fim
            tarefa.status = status
            tarefa.observacao = observacao
            tarefa.save()
        else:
            tarefa = Tarefa.objects.create(
                nome=nome,
                projeto=projeto,
                responsavel=responsavel,
                concluida=concluida,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                observacao=observacao
            )
        return redirect('dashboard:tarefas_lista')
    projetos = Projeto.objects.all()
    return render(request, 'dashboard/tarefas/form.html', {
        'tarefa': tarefa,
        'projetos': projetos,
    })
