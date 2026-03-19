# Overview

Gestion Turnos es un backend en Django orientado a empresas que ofrecen servicios y gestionan turnos con clientes. Incluye datos geograficos, catalogo de servicios, agenda, suscripciones y notificaciones.

**Capacidades actuales**
- Alta de empresas y rubros.
- Catalogo de servicios base y servicios ofrecidos por cada empresa.
- Agenda de turnos con estados y horarios.
- Suscripciones y pagos por empresa.
- Comunicaciones y notificaciones (email o WhatsApp).

**Entidades principales**
- `core.Usuario` - Usuario autenticado (cliente o empleado).
- `core.UsuarioEmpresa` - Relacion entre usuario y empresa con rol.
- `empresas.Empresa` y `empresas.Rubro` - Empresa y su categoria.
- `servicios.ServicioBase` y `servicios.ServicioEmpresa` - Catalogo base y oferta concreta.
- `agenda.Turno` - Turno con estado, fecha y servicio.
- `suscripciones.Suscripcion` y `suscripciones.Pago` - Planes y pagos.
- `comunicaciones.Conversacion` y `comunicaciones.Notificacion` - Mensajeria y alertas.
- `geo.Pais`, `geo.Provincia`, `geo.Localidad` - Datos de ubicacion.

**Rutas disponibles**
- `admin/` (Django Admin).

El enrutamiento publico aun no esta configurado en `config/urls.py`.
