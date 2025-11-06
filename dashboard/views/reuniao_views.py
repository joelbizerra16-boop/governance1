from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from dashboard.models import Reuniao
from dashboard.forms.reuniao_form import ReuniaoForm
from django.utils import timezone
from datetime import timedelta, date
import calendar
from django.shortcuts import get_object_or_404
from django.contrib import messages

def lista_reunioes(request):
    def add_months(d: date, months: int) -> date:
        # avança 'months' meses preservando o dia quando possível
        y = d.year + (d.month - 1 + months) // 12
        m = (d.month - 1 + months) % 12 + 1
        last_day = calendar.monthrange(y, m)[1]
        return date(y, m, min(d.day, last_day))

    hoje = timezone.localdate()
    reunioes_qs = Reuniao.objects.all().order_by('-data', '-hora')
    reunioes = []
    for r in reunioes_qs:
        rec = (r.recorrencia or 'Unica')

        # Função para avançar uma ocorrência
        def avancar(d: date) -> date:
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

        # Calcular quantidade de ocorrências até hoje e próxima ocorrência
        qtde = 0
        if rec == 'Unica':
            qtde = 1 if r.data <= hoje else 0
            prox = r.data if r.data >= hoje else r.data  # para texto 'faltam'
        else:
            ocorrencia = r.data
            safe_guard = 0
            while ocorrencia <= hoje and safe_guard < 400:
                qtde += 1
                ocorrencia = avancar(ocorrencia)
                safe_guard += 1
            # após o laço, 'ocorrencia' é a primeira data > hoje (próxima)
            prox = ocorrencia if ocorrencia >= hoje else r.data

        # calcular texto "faltam" (respeitando pausa)
        if getattr(r, 'pausada', False):
            faltam_str = "Pause"
        else:
            delta = (prox - hoje).days
            if delta > 0:
                faltam_str = f"{delta} dias"
            elif delta == 0:
                faltam_str = "Hoje"
            else:
                # única e já passou, ou recorrente não conseguiu avançar
                faltam_str = "Realizada"

        r.faltam = faltam_str
        r.proxima_data = prox
        r.qtde = qtde
        reunioes.append(r)

    return render(request, 'dashboard/reunioes/lista.html', {'reunioes': reunioes})

from django.views.decorators.http import require_POST

@require_POST
def toggle_reuniao_pause(request, reuniao_id: int):
    r = get_object_or_404(Reuniao, id=reuniao_id)
    r.pausada = not r.pausada
    if request.user.is_authenticated:
        r.ultimo_editor = request.user
    r.save(update_fields=['pausada', 'ultimo_editor'])
    return redirect('dashboard:lista_reunioes')

def criar_reuniao(request):
    if request.method == 'POST':
        form = ReuniaoForm(request.POST, request.FILES)
        if form.is_valid():
            reuniao_obj = form.save(commit=False)
            # Preenche usuário apenas se autenticado (FK permite null)
            if request.user.is_authenticated:
                reuniao_obj.usuario = request.user
                reuniao_obj.ultimo_editor = request.user
            reuniao_obj.save()
            from django.contrib import messages
            messages.success(request, 'Agenda realizada com sucesso!')
            return redirect('dashboard:lista_reunioes')
        else:
            # Exibe erros de validação no próprio formulário
            from django.contrib import messages
            messages.error(request, 'Não foi possível salvar. Verifique os campos destacados.')
    else:
        form = ReuniaoForm()
    return render(request, 'dashboard/reunioes/form.html', {'form': form})


def editar_reuniao(request, reuniao_id: int):
    reuniao = get_object_or_404(Reuniao, id=reuniao_id)
    if request.method == 'POST':
        form = ReuniaoForm(request.POST, request.FILES, instance=reuniao)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.user.is_authenticated:
                obj.ultimo_editor = request.user
            obj.save()
            messages.success(request, 'Reunião atualizada com sucesso!')
            return redirect('dashboard:lista_reunioes')
        else:
            messages.error(request, 'Não foi possível atualizar. Verifique os campos destacados.')
    else:
        form = ReuniaoForm(instance=reuniao)
    return render(request, 'dashboard/reunioes/form.html', {'form': form})


def excluir_reuniao(request, reuniao_id: int):
    reuniao = get_object_or_404(Reuniao, id=reuniao_id)
    if request.method == 'POST':
        titulo = reuniao.titulo
        reuniao.delete()
        messages.success(request, f'Reunião "{titulo}" excluída com sucesso.')
        return redirect('dashboard:lista_reunioes')
    # Para métodos não-POST, redireciona sem excluir
    messages.error(request, 'Ação inválida para exclusão.')
    return redirect('dashboard:lista_reunioes')
