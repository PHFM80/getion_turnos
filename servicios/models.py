from django.db import models


class ServicioBase(models.Model):
    nombre = models.CharField(max_length=150)
    rubro = models.ForeignKey(
        'empresas.Rubro',
        on_delete=models.PROTECT,
        related_name='servicios_base',
    )

    def __str__(self):
        return self.nombre


class ServicioEmpresa(models.Model):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='servicios',
    )
    servicio_base = models.ForeignKey(
        ServicioBase,
        on_delete=models.PROTECT,
        related_name='servicios_empresa',
    )
    duracion = models.DurationField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.empresa} - {self.servicio_base}'
