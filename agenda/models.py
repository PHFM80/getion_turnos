from django.conf import settings
from django.db import models


class CapacidadEmpresa(models.Model):
    empresa = models.OneToOneField(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='capacidad',
    )
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.empresa} - {self.capacidad}'


class HorarioEmpresa(models.Model):
    DIA_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='horarios',
    )
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f'{self.empresa} - {self.get_dia_semana_display()}'


class BloqueoEmpresa(models.Model):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='bloqueos',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.empresa} - {self.fecha}'


class Turno(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CONFIRMADO = 'confirmado'
    ESTADO_CANCELADO = 'cancelado'
    ESTADO_COMPLETADO = 'completado'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADO, 'Confirmado'),
        (ESTADO_CANCELADO, 'Cancelado'),
        (ESTADO_COMPLETADO, 'Completado'),
    ]

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='turnos',
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='turnos',
    )
    servicio_empresa = models.ForeignKey(
        'servicios.ServicioEmpresa',
        on_delete=models.PROTECT,
        related_name='turnos',
    )
    empleado = models.ForeignKey(
        'core.UsuarioEmpresa',
        on_delete=models.PROTECT,
        related_name='turnos',
        null=True,
        blank=True,
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.empresa} - {self.fecha} {self.hora_inicio}'
