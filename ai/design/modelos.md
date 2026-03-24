## Entidades y campos (extraído del código)

### `core.Usuario`
- `email`: `EmailField`, `unique=True`
- `username`: `CharField(max_length=150)`, `null=True`, `blank=True`
- `nombre`: `CharField(max_length=150)`
- `apellido`: `CharField(max_length=150)`
- `dni`: `CharField(max_length=20)`, `unique=True`
- `telefono`: `CharField(max_length=30)`, `unique=True`
- `localidad`: `ForeignKey` -> `geo.Localidad`, `on_delete=PROTECT`, `null=True`, `blank=True`

### `core.UsuarioEmpresa`
- `usuario`: `ForeignKey` -> `settings.AUTH_USER_MODEL`, `on_delete=CASCADE`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `rol`: `CharField(max_length=20)`, choices: `dueno`, `empleado`
- `activo`: `BooleanField(default=True)`
- `fecha_alta`: `DateField(auto_now_add=True)`
- Restricción: `UniqueConstraint(fields=['usuario', 'empresa'])`

### `geo.Pais`
- `nombre`: `CharField(max_length=150)`, `unique=True`
- `codigo`: `CharField(max_length=10)`, `null=True`, `blank=True`

### `geo.Provincia`
- `nombre`: `CharField(max_length=150)`
- `pais`: `ForeignKey` -> `geo.Pais`, `on_delete=PROTECT`
- Restricción: `UniqueConstraint(fields=['nombre', 'pais'])`

### `geo.Localidad`
- `nombre`: `CharField(max_length=150)`
- `provincia`: `ForeignKey` -> `geo.Provincia`, `on_delete=PROTECT`
- Restricción: `UniqueConstraint(fields=['nombre', 'provincia'])`

### `empresas.Rubro`
- `nombre`: `CharField(max_length=150)`

### `empresas.Empresa`
- `nombre`: `CharField(max_length=200)`
- `telefono`: `CharField(max_length=30)`, `unique=True`
- `calle`: `CharField(max_length=200)`
- `numero`: `CharField(max_length=20)`
- `activo`: `BooleanField(default=True)`
- `pais`: `ForeignKey` -> `geo.Pais`, `on_delete=PROTECT`
- `provincia`: `ForeignKey` -> `geo.Provincia`, `on_delete=PROTECT`
- `localidad`: `ForeignKey` -> `geo.Localidad`, `on_delete=PROTECT`
- `rubro`: `ForeignKey` -> `empresas.Rubro`, `on_delete=PROTECT`

### `suscripciones.Plan`
- `nombre`: `CharField(max_length=150)`
- `limite_simultaneo`: `PositiveIntegerField`, `null=True`, `blank=True`
- `precio_mensual`: `DecimalField(max_digits=10, decimal_places=2, default=0)`
- `precio_anual`: `DecimalField(max_digits=10, decimal_places=2, default=0)`

### `suscripciones.Suscripcion`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `plan`: `ForeignKey` -> `suscripciones.Plan`, `on_delete=PROTECT`
- `activa`: `BooleanField(default=True)`
- `periodicidad`: `CharField(max_length=20)`, choices: `mensual`, `anual`
- `fecha_inicio`: `DateField`
- `fecha_vencimiento`: `DateField`, `null=True`, `blank=True`
- Restricción: `UniqueConstraint(fields=['empresa'], condition=Q(activa=True))`

### `suscripciones.Pago`
- `suscripcion`: `ForeignKey` -> `suscripciones.Suscripcion`, `on_delete=CASCADE`
- `fecha_pago`: `DateField`
- `monto`: `DecimalField(max_digits=10, decimal_places=2)`
- `periodo`: `CharField(max_length=20)`, choices: `mensual`, `anual`

### `agenda.CapacidadEmpresa`
- `empresa`: `OneToOneField` -> `empresas.Empresa`, `on_delete=CASCADE`
- `nombre`: `CharField(max_length=150)`, `null=True`, `blank=True`
- `capacidad`: `PositiveIntegerField`

### `agenda.CapacidadPuesto`
- `capacidad`: `ForeignKey` -> `agenda.CapacidadEmpresa`, `on_delete=CASCADE`
- `orden`: `PositiveSmallIntegerField`
- `nombre`: `CharField(max_length=150)`, `null=True`, `blank=True`
- Restricción: `UniqueConstraint(fields=['capacidad', 'orden'])`

### `agenda.HorarioEmpresa`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `dia_semana`: `IntegerField`, choices: `0` a `6` (`Lunes` a `Domingo`)
- `hora_inicio`: `TimeField`
- `hora_fin`: `TimeField`

### `agenda.BloqueoEmpresa`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `fecha`: `DateField`
- `hora_inicio`: `TimeField`
- `hora_fin`: `TimeField`
- `motivo`: `CharField(max_length=255)`, `null=True`, `blank=True`

### `agenda.Turno`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `cliente`: `ForeignKey` -> `settings.AUTH_USER_MODEL`, `on_delete=PROTECT`
- `servicio_empresa`: `ForeignKey` -> `servicios.ServicioEmpresa`, `on_delete=PROTECT`
- `empleado`: `ForeignKey` -> `core.UsuarioEmpresa`, `on_delete=PROTECT`, `null=True`, `blank=True`
- `fecha`: `DateField`
- `hora_inicio`: `TimeField`
- `hora_fin`: `TimeField`
- `estado`: `CharField(max_length=20)`, choices: `pendiente`, `confirmado`, `cancelado`, `completado`
- `fecha_creacion`: `DateTimeField(auto_now_add=True)`
- `fecha_actualizacion`: `DateTimeField(auto_now=True)`

### `servicios.ServicioBase`
- `nombre`: `CharField(max_length=150)`
- `rubro`: `ForeignKey` -> `empresas.Rubro`, `on_delete=PROTECT`

### `servicios.ServicioEmpresa`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `servicio_base`: `ForeignKey` -> `servicios.ServicioBase`, `on_delete=PROTECT`
- `duracion`: `DurationField`
- `precio`: `DecimalField(max_digits=10, decimal_places=2)`
- `activo`: `BooleanField(default=True)`

### `comunicaciones.Conversacion`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `usuario`: `ForeignKey` -> `settings.AUTH_USER_MODEL`, `on_delete=CASCADE`
- `estado`: `CharField(max_length=50)`
- `activa`: `BooleanField(default=True)`
- `ultimo_mensaje`: `TextField`, `null=True`, `blank=True`
- `fecha_actualizacion`: `DateTimeField(auto_now=True)`

### `comunicaciones.Notificacion`
- `empresa`: `ForeignKey` -> `empresas.Empresa`, `on_delete=CASCADE`
- `usuario`: `ForeignKey` -> `settings.AUTH_USER_MODEL`, `on_delete=CASCADE`
- `canal`: `CharField(max_length=20)`, choices: `whatsapp`, `email`
- `tipo`: `CharField(max_length=30)`, choices: `confirmacion`, `recordatorio`, `cancelacion`
- `estado`: `CharField(max_length=20)`, choices: `pendiente`, `enviado`, `fallido`
- `fecha_envio`: `DateTimeField`
