from django.db import models


class Pais(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    nombre = models.CharField(max_length=150)
    pais = models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name='provincias',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'pais'],
                name='unique_provincia_por_pais',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.pais}'


class Localidad(models.Model):
    nombre = models.CharField(max_length=150)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        related_name='localidades',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'provincia'],
                name='unique_localidad_por_provincia',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.provincia}'
