from django.db import models
from django.contrib.auth import get_user_model

class Reuniao(models.Model):
    titulo = models.CharField(max_length=120)
    objetivo = models.TextField("Objetivo/Pauta", blank=True)
    data = models.DateField()
    hora = models.TimeField()
    local = models.CharField(max_length=120, blank=True)
    link = models.URLField("Link da reunião", blank=True)
    participantes = models.CharField(max_length=255, help_text="Separe os nomes por vírgula")
    anexos = models.FileField(upload_to='anexos_reunioes/', blank=True, null=True)
    status = models.CharField(max_length=40, choices=[('Agendada','Agendada'),('Realizada','Realizada'),('Cancelada','Cancelada')], default='Agendada')
    planta = models.CharField(max_length=40, choices=[('Todas','Todas'),('Santo André','Santo André'),('Gravataí','Gravataí')], default='Todas')
    recorrencia = models.CharField(max_length=20, choices=[('Unica','Única'),('Diaria','Diária'),('Semanal','Semanal'),('Quinzenal','Quinzenal'),('Mensal','Mensal'),('Bimestral','Bimestral'),('Semestral','Semestral')], default='Unica')
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='reunioes_criadas')
    ultimo_editor = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='reunioes_editadas')
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.data} {self.hora})"
