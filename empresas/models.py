from django.db import models


class Rubro(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=30, unique=True)
    calle = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    pais = models.ForeignKey(
        'geo.Pais',
        on_delete=models.PROTECT,
        related_name='empresas',
    )
    provincia = models.ForeignKey(
        'geo.Provincia',
        on_delete=models.PROTECT,
        related_name='empresas',
    )
    localidad = models.ForeignKey(
        'geo.Localidad',
        on_delete=models.PROTECT,
        related_name='empresas',
    )
    rubro = models.ForeignKey(
        Rubro,
        on_delete=models.PROTECT,
        related_name='empresas',
    )

    def __str__(self):
        return self.nombre
