from django.contrib import admin

from .models import Projeto


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'responsavel', 'status', 'unidade')
	search_fields = ('nome', 'responsavel', 'unidade')
	list_filter = ('unidade', 'status', 'responsavel')
