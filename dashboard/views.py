from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseForbidden, HttpResponseRedirect
from banco_dados.models import Projeto, AreaResponsavel, Unidade, Tarefa
from django.db.models import Q
from dashboard.models import AgendaAuditoria

def tarefa_visualizar(request, tarefa_id):
	tarefa = get_object_or_404(Tarefa, id=tarefa_id)
	return render(request, 'dashboard/tarefas/visualizar.html', {'tarefa': tarefa})

@login_required
@require_POST
def toggle_tarefa_concluida(request, tarefa_id):
	tarefa = Tarefa.objects.get(id=tarefa_id)
	# Permissão: só pode alterar se for da mesma unidade
	if tarefa.projeto.unidade != request.user.profile.unidade:
		return HttpResponseForbidden('Você só pode alterar tarefas da sua unidade.')
	tarefa.concluida = not tarefa.concluida
	tarefa.save()
	# Redireciona para a lista mantendo filtros
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/tarefas/'))
@login_required
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
			from datetime import datetime
			def parse_date(date_str):
				try:
					return datetime.strptime(date_str, '%Y-%m-%d').date()
				except Exception:
					return None
			data_inicio = parse_date(data_inicio) if data_inicio else None
			data_fim = parse_date(data_fim) if data_fim else None
			concluida = request.POST.get('concluida') == 'on'
			status = int(request.POST.get('status', 0))
			if not projeto_id:
				projetos = Projeto.objects.all()
				return render(request, 'dashboard/tarefas/form.html', {
					'tarefa': tarefa,
					'projetos': projetos,
					'erro': 'Selecione um projeto para a tarefa.'
				})
			projeto = Projeto.objects.get(id=projeto_id)
			if tarefa:
				tarefa.nome = nome
				tarefa.projeto = projeto
				tarefa.responsavel = responsavel
				tarefa.concluida = concluida
				tarefa.data_inicio = data_inicio
				tarefa.data_fim = data_fim
				tarefa.status = status
				tarefa.save()
			else:
				tarefa = Tarefa.objects.create(
					nome=nome,
					projeto=projeto,
					responsavel=responsavel,
					concluida=concluida,
					data_inicio=data_inicio,
					data_fim=data_fim,
					status=status
				)
			return redirect('dashboard:tarefas_lista')
		projetos = Projeto.objects.all()
		return render(request, 'dashboard/tarefas/form.html', {
			'tarefa': tarefa,
			'projetos': projetos,
		})
@login_required
def tarefas_lista(request):
	projeto_id = request.GET.get('projeto')
	auditoria = request.GET.get('auditoria')
	responsavel = request.GET.get('responsavel')
	status = request.GET.get('status')
	q = request.GET.get('q')
	tarefas = Tarefa.objects.all()
	sort = request.GET.get('sort')
	if q:
		# Quando há termo de busca, aplica apenas a pesquisa global
		tarefas = Tarefa.objects.filter(
			Q(nome__icontains=q) |
			Q(projeto__nome__icontains=q) |
			Q(responsavel__icontains=q) |
			Q(status__icontains=q)
		)
	else:
		if auditoria:
			tarefas = tarefas.filter(auditoria=auditoria)
		if responsavel:
			tarefas = tarefas.filter(responsavel__icontains=responsavel)
		if status:
			tarefas = tarefas.filter(status=status)
	if sort == 'data_fim_asc':
		tarefas = tarefas.order_by('data_fim')
	elif sort == 'data_inicio_asc':
		tarefas = tarefas.order_by('data_inicio')

	tarefas_list = []
	for tarefa in tarefas:
		if hasattr(request.user, 'profile'):
			bloqueada = tarefa.projeto.unidade != request.user.profile.unidade
		else:
			bloqueada = False
		setattr(tarefa, 'bloqueada', bloqueada)
		tarefas_list.append(tarefa)

	return render(request, 'dashboard/tarefas/lista.html', {
		'tarefas': tarefas_list,
		'projeto_id': projeto_id,
		'auditoria': auditoria,
		'responsavel': responsavel,
		'status': status,
		'q': q,
		'sort': sort,
	})
@require_http_methods(["GET", "POST"])
def projeto_excluir(request, projeto_id):
	try:
		projeto = Projeto.objects.get(id=projeto_id)
	except Projeto.DoesNotExist:
		return redirect('/')
	if request.method == 'POST':
		projeto.delete()
		return redirect('/')
	return render(request, 'dashboard/projetos/excluir.html', {'projeto': projeto})
def projeto_visualizar(request, projeto_id):
	projeto = Projeto.objects.get(id=projeto_id)
	tarefas_fk = Tarefa.objects.filter(projeto_id=projeto_id)
	tarefas_m2m = projeto.tarefas_associadas.filter(projeto_id=projeto_id)
	tarefas = list(set(list(tarefas_fk) + list(tarefas_m2m)))
	# Calcular porcentagem média dos status das tarefas
	total = len(tarefas)
	if total > 0:
		# status pode ser string '25%' ou int 25
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
	return render(request, 'dashboard/projetos/visualizar.html', {
		'projeto': projeto,
		'tarefas_relacionadas': tarefas,
		'status_percent': status_percent,
	})

@login_required
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
		tarefas_ids = request.POST.get('tarefas_associadas', '').split(',')
		if projeto:
			projeto.nome = nome
			projeto.responsavel = responsavel
			projeto.area_responsavel = area_responsavel
			projeto.data_inicio = data_inicio
			projeto.data_fim = data_fim
			projeto.unidade = unidade
			projeto.status = status
			projeto.save()
		else:
			# Criação do projeto: data_criacao é automática, usuario é o usuário ativo, unidade vem do formulário
			projeto = Projeto.objects.create(
				nome=nome,
				responsavel=responsavel,
				area_responsavel=area_responsavel,
				data_inicio=data_inicio,
				data_fim=data_fim,
				unidade=unidade,
				status=status,
				usuario=request.user
			)
		tarefas = Tarefa.objects.filter(id__in=[tid.strip() for tid in tarefas_ids if tid.strip().isdigit()])
		projeto.tarefas_associadas.set(tarefas)
		projeto.save()
		return redirect('dashboard:projetos_lista')
	areas = AreaResponsavel.choices
	unidades = Unidade.choices
	tarefas_associadas = ','.join(str(t.id) for t in projeto.tarefas_associadas.all()) if projeto else ''
	return render(request, 'dashboard/projetos/form.html', {
		'projeto': projeto,
		'areas': areas,
		'unidades': unidades,
		'tarefas_associadas': tarefas_associadas,
	})

def dashboard_view(request):
    projetos_concluido = 70
    alertas = [
        {'nome': 'Tarefa X', 'dias': 2},
        {'nome': 'Tarefa Y', 'dias': 1},
    ]
    projetos = Projeto.objects.all()
    return render(request, 'dashboard/dashboard.html', {
        'projetos_concluido': projetos_concluido,
        'alertas': alertas,
        'projetos': projetos,
    })

def projetos_lista(request):
    unidade_selecionada = request.GET.get('unidade', '')
    area_selecionada = request.GET.get('area', '')
    busca = request.GET.get('busca', '')
    projetos = Projeto.objects.all()
    if unidade_selecionada:
        projetos = projetos.filter(unidade=unidade_selecionada)
    if area_selecionada:
        projetos = projetos.filter(area_responsavel=area_selecionada)
    if busca:
        projetos = projetos.filter(nome__icontains=busca)
    areas = Projeto._meta.get_field('area_responsavel').choices
    unidades = Projeto._meta.get_field('unidade').choices
    return render(request, 'dashboard/projetos/lista.html', {
        'projetos': projetos,
        'areas': areas,
        'unidades': unidades,
        'unidade_selecionada': unidade_selecionada,
        'area_selecionada': area_selecionada,
        'busca': busca,
    })

# Novas views para AgendaAuditoria
@login_required
def auditorias_lista(request):
    auditorias = AgendaAuditoria.objects.all()
    return render(request, 'dashboard/auditorias/lista.html', {
        'auditorias': auditorias,
    })

@login_required
def auditoria_form(request, auditoria_id=None):
    if auditoria_id:
        auditoria = get_object_or_404(AgendaAuditoria, id=auditoria_id)
        if hasattr(request.user, 'profile'):
            if auditoria.unidade != request.user.profile.unidade:
                return HttpResponseForbidden('Você só pode editar auditorias da sua unidade.')
    else:
        auditoria = None
    if request.method == 'POST':
        tipo_auditoria = request.POST.get('tipo_auditoria')
        projeto_id = request.POST.get('projeto')
        data = request.POST.get('data')
        hora = request.POST.get('hora')
        unidade = request.POST.get('unidade')
        responsavel = request.POST.get('responsavel')
        status = request.POST.get('status')
        comentarios = request.POST.get('comentarios')
        projeto = Projeto.objects.get(id=projeto_id) if projeto_id else None
        if auditoria:
            auditoria.tipo_auditoria = tipo_auditoria
            auditoria.projeto = projeto
            auditoria.data = data
            auditoria.hora = hora
            auditoria.unidade = unidade
            auditoria.responsavel = responsavel
            auditoria.status = status
            auditoria.comentarios = comentarios
            auditoria.ultimo_editor = request.user
            auditoria.save()
        else:
            auditoria = AgendaAuditoria.objects.create(
                tipo_auditoria=tipo_auditoria,
                projeto=projeto,
                data=data,
                hora=hora,
                unidade=unidade,
                responsavel=responsavel,
                status=status,
                comentarios=comentarios,
                ultimo_editor=request.user
            )
        return redirect('lista_auditorias')
    projetos = Projeto.objects.all()
    return render(request, 'dashboard/auditorias/form.html', {
        'auditoria': auditoria,
        'projetos': projetos,
        'form': auditoria,
    })

@login_required
def excluir_auditoria(request, auditoria_id):
    auditoria = get_object_or_404(AgendaAuditoria, id=auditoria_id)
    if hasattr(request.user, 'profile'):
        if auditoria.unidade != request.user.profile.unidade:
            return HttpResponseForbidden('Você só pode excluir auditorias da sua unidade.')
    auditoria.delete()
    return redirect('lista_auditorias')

# Exportação explícita para import direto
# Isso garante que o Python reconheça as funções como atributos do módulo

dashboard_view = dashboard_view
projetos_lista = projetos_lista
projeto_form = projeto_form
projeto_visualizar = projeto_visualizar
projeto_excluir = projeto_excluir
tarefas_lista = tarefas_lista
tarefa_form = tarefa_form
tarefa_visualizar = tarefa_visualizar
toggle_tarefa_concluida = toggle_tarefa_concluida
auditorias_lista = auditorias_lista
auditoria_form = auditoria_form
excluir_auditoria = excluir_auditoria

__all__ = [
    "dashboard_view", "projetos_lista", "projeto_form", "projeto_visualizar", "projeto_excluir",
    "tarefas_lista", "tarefa_form", "tarefa_visualizar", "toggle_tarefa_concluida",
    "auditorias_lista", "auditoria_form", "excluir_auditoria"
]
