# Apps

**core**
- Define el usuario personalizado (`Usuario`) basado en email.
- Modela la relacion usuario-empresa con roles (`UsuarioEmpresa`).

**geo**
- Catalogo de `Pais`, `Provincia` y `Localidad`.

**empresas**
- `Empresa` con datos de contacto y ubicacion.
- `Rubro` para categorizar empresas.

**servicios**
- `ServicioBase` para catalogo general por rubro.
- `ServicioEmpresa` para servicios ofrecidos por cada empresa.

**agenda**
- `CapacidadEmpresa` para cupos por empresa.
- `HorarioEmpresa` para disponibilidad semanal.
- `BloqueoEmpresa` para excepciones.
- `Turno` con estado, cliente, servicio y empleado.

**suscripciones**
- `Plan` con limite de turnos simultaneos y precios mensual/anual.
- `Suscripcion` por empresa con periodicidad mensual/anual.
- `Pago` historico (fecha actual, monto y periodo aplicado).

**comunicaciones**
- `Conversacion` empresa-usuario.
- `Notificacion` por canal y tipo (confirmacion, recordatorio, cancelacion).
