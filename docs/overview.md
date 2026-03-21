# Overview

Gestion Turnos es una aplicacion Django para administrar empresas, usuarios, servicios, suscripciones, pagos y turnos.

**Capacidades actuales**
- Home publica con modo claro/oscuro.
- Login con validaciones y visualizacion/ocultacion de password.
- Vista publica de empresas/servicios y solicitud de turno (mock, sin persistencia de turnos).
- Dashboard de usuario con selector de empresa cuando un usuario pertenece a mas de una.
- Dashboard admin con modulos de empresa, complementos y contabilidad.
- Alta/edicion de empresa con validaciones de geografia dependiente (pais, provincia, localidad).
- Alta/edicion/eliminacion de usuarios por empresa y reset de password con PDF de credenciales.
- Gestion de suscripcion (plan + periodicidad) y registro de pagos automaticos con reglas de vencimiento.
- Contabilidad con filtros por anio/mes/rubro y metricas financieras.
- Sincronizacion de suscripciones vencidas via comando de management.

**Entidades principales**
- `core.Usuario` - Usuario autenticado.
- `core.UsuarioEmpresa` - Relacion usuario-empresa con rol.
- `empresas.Empresa` y `empresas.Rubro` - Empresa y categoria.
- `geo.Pais`, `geo.Provincia`, `geo.Localidad` - Datos de ubicacion.
- `servicios.ServicioBase` y `servicios.ServicioEmpresa` - Servicios base y por empresa.
- `suscripciones.Plan`, `suscripciones.Suscripcion`, `suscripciones.Pago` - Planes, suscripciones y pagos.

**Rutas principales**
- Publicas:
  - `/`
  - `/servicios/`
  - `/servicios/turno/<slug>/`
  - `/login/`, `/logout/`
- Dashboard:
  - `/dashboard/`
  - `/dashboard/empresa/<empresa_id>/` (selector de empresa para usuarios multiempresa)
- Admin:
  - `/dashboard/admin/`
  - `/dashboard/admin/empresa/`
  - `/dashboard/admin/complementos/`
  - `/dashboard/admin/contabilidad/`
