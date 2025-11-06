from django.db import models
from banco_dados.models import Projeto
from django.contrib.auth.models import User

class AgendaAuditoria(models.Model):
    TIPO_CHOICES = [
        ('Interna', 'Interna'),
        ('Externa', 'Externa'),
        ('Cliente', 'Cliente'),
        ('Fornecedor', 'Fornecedor'),
    ]
    STATUS_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Concluída', 'Concluída'),
        ('Cancelada', 'Cancelada'),
        ('Pendente', 'Pendente'),
    ]
    tipo_auditoria = models.CharField(max_length=30, choices=TIPO_CHOICES)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='auditorias', null=True, blank=True)
    data = models.DateField()
    hora = models.TimeField()
    unidade = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comentarios = models.TextField(blank=True)
    ultimo_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo_auditoria} - {self.projeto} - {self.data}"

class Reuniao(models.Model):
    titulo = models.CharField(max_length=120)
    objetivo = models.TextField("Objetivo/Pauta", blank=True)
    data = models.DateField()
    hora = models.TimeField()
    local = models.CharField(max_length=120, blank=True)
    # campo link removido
    participantes = models.CharField(max_length=255, help_text="Separe os nomes por vírgula")
    anexos = models.FileField(upload_to='anexos_reunioes/', blank=True, null=True)
    status = models.CharField(max_length=40, choices=[('Agendada','Agendada'),('Realizada','Realizada'),('Cancelada','Cancelada')], default='Agendada')
    # Novos campos
    planta = models.CharField(max_length=40, choices=[('Todas','Todas'),('Santo André','Santo André'),('Gravataí','Gravataí')], default='Todas')
    recorrencia = models.CharField(max_length=20, choices=[('Unica','Única'),('Diaria','Diária'),('Semanal','Semanal'),('Quinzenal','Quinzenal'),('Mensal','Mensal'),('Bimestral','Bimestral'),('Semestral','Semestral')], default='Unica')
    observacoes = models.TextField(blank=True)
    pausada = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reunioes_criadas')
    ultimo_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reunioes_editadas')
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.data} {self.hora})"
