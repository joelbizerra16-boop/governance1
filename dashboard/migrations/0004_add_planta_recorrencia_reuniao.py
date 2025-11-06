from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0003_alter_agendaauditoria_projeto'),
    ]

    operations = [
        migrations.AddField(
            model_name='reuniao',
            name='planta',
            field=models.CharField(max_length=40, choices=[('Todas','Todas'),('Santo André','Santo André'),('Gravataí','Gravataí')], default='Todas'),
        ),
        migrations.AddField(
            model_name='reuniao',
            name='recorrencia',
            field=models.CharField(max_length=20, choices=[('Unica','Única'),('Diaria','Diária'),('Semanal','Semanal'),('Quinzenal','Quinzenal'),('Mensal','Mensal'),('Bimestral','Bimestral'),('Semestral','Semestral')], default='Unica'),
        ),
    ]
