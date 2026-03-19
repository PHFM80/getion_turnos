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
- `Plan` y `Suscripcion` por empresa.
- `Pago` con periodo mensual o anual.

**comunicaciones**
- `Conversacion` empresa-usuario.
- `Notificacion` por canal y tipo (confirmacion, recordatorio, cancelacion).
