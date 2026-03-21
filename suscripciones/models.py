from django.db import models
from django.db.models import Q


class Plan(models.Model):
    nombre = models.CharField(max_length=150)
    limite_simultaneo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad maxima de turnos simultaneos. Vacio = sin limite.",
    )
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_anual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    PERIODO_MENSUAL = 'mensual'
    PERIODO_ANUAL = 'anual'
    PERIODO_CHOICES = [
        (PERIODO_MENSUAL, 'Mensual'),
        (PERIODO_ANUAL, 'Anual'),
    ]

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
    periodicidad = models.CharField(max_length=20, choices=PERIODO_CHOICES, default=PERIODO_MENSUAL)
    fecha_inicio = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

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
