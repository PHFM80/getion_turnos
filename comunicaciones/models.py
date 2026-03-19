from django.conf import settings
from django.db import models


class Conversacion(models.Model):
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='conversaciones',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversaciones',
    )
    estado = models.CharField(max_length=50)
    activa = models.BooleanField(default=True)
    ultimo_mensaje = models.TextField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.empresa} - {self.usuario}'


class Notificacion(models.Model):
    CANAL_WHATSAPP = 'whatsapp'
    CANAL_EMAIL = 'email'
    CANAL_CHOICES = [
        (CANAL_WHATSAPP, 'WhatsApp'),
        (CANAL_EMAIL, 'Email'),
    ]

    TIPO_CONFIRMACION = 'confirmacion'
    TIPO_RECORDATORIO = 'recordatorio'
    TIPO_CANCELACION = 'cancelacion'
    TIPO_CHOICES = [
        (TIPO_CONFIRMACION, 'Confirmación'),
        (TIPO_RECORDATORIO, 'Recordatorio'),
        (TIPO_CANCELACION, 'Cancelación'),
    ]

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_ENVIADO = 'enviado'
    ESTADO_FALLIDO = 'fallido'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ENVIADO, 'Enviado'),
        (ESTADO_FALLIDO, 'Fallido'),
    ]

    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_envio = models.DateTimeField()

    def __str__(self):
        return f'{self.empresa} - {self.usuario} - {self.tipo}'
