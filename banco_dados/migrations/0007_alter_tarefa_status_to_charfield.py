from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('banco_dados', '0006_tarefa_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarefa',
            name='status',
            field=models.CharField(max_length=10, default='0%', verbose_name='Status (%)'),
        ),
    ]
