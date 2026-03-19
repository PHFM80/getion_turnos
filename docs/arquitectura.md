# Arquitectura

Este documento resume la arquitectura actual basada en lo que existe en el codigo.

**Estructura de apps**
- `core`: usuario personalizado y relacion usuario-empresa con roles.
- `geo`: pais, provincia y localidad.
- `empresas`: empresa y rubro.
- `servicios`: catalogo base y servicios por empresa.
- `agenda`: capacidad, horarios, bloqueos y turnos.
- `suscripciones`: planes, suscripciones y pagos.
- `comunicaciones`: conversaciones y notificaciones.

**Relaciones clave (modelo)**
- Un `Usuario` puede pertenecer a varias `Empresa` mediante `UsuarioEmpresa`.
- Una `Empresa` pertenece a un `Rubro` y a una ubicacion (`Pais`, `Provincia`, `Localidad`).
- Una `Empresa` ofrece muchos `ServicioEmpresa`, basados en `ServicioBase`.
- Una `Empresa` tiene `Turno` que referencian cliente, servicio y opcionalmente empleado.
- Una `Empresa` puede tener una `Suscripcion` activa y muchos `Pago`.
- Las `Notificacion` y `Conversacion` vinculan empresa y usuario.

**Flujos existentes**
- Alta de datos base con `seed_initial_data` (geo, rubros y servicios).

**Pendiente (cuando exista)**
- Endpoints publicos y flujo de turnos por API.
- Integraciones reales de notificaciones.
- Diagrama de despliegue.
