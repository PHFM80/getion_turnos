from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suscripciones', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suscripcion',
            name='fecha_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
    ]
