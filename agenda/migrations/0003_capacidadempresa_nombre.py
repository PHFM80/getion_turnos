from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='capacidadempresa',
            name='nombre',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
