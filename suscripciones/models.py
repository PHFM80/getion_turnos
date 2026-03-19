from django.db import models
from django.db.models import Q


class Plan(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='suscripciones',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='suscripciones',
    )
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_vencimiento = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['empresa'],
                condition=Q(activa=True),
                name='unique_suscripcion_activa_por_empresa',
            ),
        ]

    def __str__(self):
        return f'{self.empresa} - {self.plan}'


class Pago(models.Model):
    PERIODO_MENSUAL = 'mensual'
    PERIODO_ANUAL = 'anual'
    PERIODO_CHOICES = [
        (PERIODO_MENSUAL, 'Mensual'),
        (PERIODO_ANUAL, 'Anual'),
    ]

    suscripcion = models.ForeignKey(
        Suscripcion,
        on_delete=models.CASCADE,
        related_name='pagos',
    )
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES)

    def __str__(self):
        return f'{self.suscripcion} - {self.fecha_pago}'
