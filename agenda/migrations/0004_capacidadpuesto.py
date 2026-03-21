from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0003_capacidadempresa_nombre'),
    ]

    operations = [
        migrations.CreateModel(
            name='CapacidadPuesto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField()),
                ('nombre', models.CharField(blank=True, max_length=150, null=True)),
                ('capacidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puestos', to='agenda.capacidadempresa')),
            ],
            options={
                'ordering': ['orden'],
            },
        ),
        migrations.AddConstraint(
            model_name='capacidadpuesto',
            constraint=models.UniqueConstraint(fields=('capacidad', 'orden'), name='unique_puesto_por_capacidad_orden'),
        ),
    ]
