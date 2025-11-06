from django.db import models

class Unidade(models.TextChoices):
	SANTO_ANDRE = 'Santo André', 'Santo André'
	GRAVATAI = 'Gravataí', 'Gravataí'
	TODAS = 'Todas', 'Todas'

class AreaResponsavel(models.TextChoices):
	SUPERVISAO = 'Supervisão', 'Supervisão'
	QUALIDADE = 'Qualidade', 'Qualidade'
	OPERACAO = 'Operação', 'Operação'
	RH = 'RH', 'RH'
	MANUTENCAO = 'Manutenção', 'Manutenção'
	HSE = 'HSE', 'HSE'

class Projeto(models.Model):
	nome = models.CharField(max_length=120, verbose_name='Nome do projeto')
	responsavel = models.CharField(max_length=100, verbose_name='Responsável')
	area_responsavel = models.CharField(max_length=20, choices=AreaResponsavel.choices, verbose_name='Área responsável')
	data_inicio = models.DateField(verbose_name='Data início')
	data_fim = models.DateField(verbose_name='Data fim')
	unidade = models.CharField(max_length=20, choices=Unidade.choices, verbose_name='Unidade')
	usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name='Usuário', editable=False, null=True, blank=True)
	status = models.PositiveIntegerField(default=0, verbose_name='% concluído')
	observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
	data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data criação')
	tarefas_associadas = models.ManyToManyField('Tarefa', blank=True, verbose_name='Tarefas associadas', related_name='projetos_associados')

	def __str__(self):
		return self.nome

class Tarefa(models.Model):
	nome = models.CharField(max_length=120, verbose_name='Nome da tarefa')
	projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='tarefas')
	responsavel = models.CharField(max_length=100, verbose_name='Responsável', default='')
	data_inicio = models.DateField(verbose_name='Data início', null=True, blank=True)
	data_fim = models.DateField(verbose_name='Data fim', null=True, blank=True)
	concluida = models.BooleanField(default=False, verbose_name='Concluída')
	status = models.CharField(max_length=10, default='0%', verbose_name='Status (%)')
	observacao = models.TextField(blank=True, null=True, verbose_name='Observação')

	def __str__(self):
		return self.nome
