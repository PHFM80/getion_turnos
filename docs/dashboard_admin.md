# Dashboard Admin

Este documento resume los flujos implementados en el panel admin.

**Modulo Empresa**
- Listado y busqueda: `/dashboard/admin/empresa/`
  - Filtro en vivo por nombre y estado (activa/inactiva).
  - Muestra vencimiento de suscripcion por empresa.
- Alta: `/dashboard/admin/empresas/nueva/`
  - Crea empresa y suscripcion inicial.
  - Plan obligatorio al crear.
  - Periodicidad obligatoria al crear (`mensual` o `anual`).
  - `fecha_inicio` de suscripcion = hoy.
  - `fecha_vencimiento` inicial = null.
- Edicion: `/dashboard/admin/empresa/<id>/`
  - Datos de empresa.
  - Card de suscripcion (con acceso a editar).
  - Card de pagos (registro + historial).
  - Card de usuarios (alta, editar, eliminar).

**Usuarios por empresa**
- Alta: `/dashboard/admin/empresa/<id>/usuarios/nuevo/`
  - Password inicial fija: `gestorturnos2026` solo para usuario nuevo.
  - Si el email ya existe, no crea duplicado: propone vincular usuario existente.
  - Muestra confirmacion previa (aceptar/cancelar) antes de vincular.
  - Regla por rol al vincular:
    - `dueno`: puede estar asociado a multiples empresas.
    - `empleado`: solo puede estar asociado a una empresa.
  - Si crea usuario nuevo, genera PDF descargable con credenciales.
  - Redireccion automatica de regreso a empresa.
- Edicion: `/dashboard/admin/empresa/<id>/usuarios/<usuario_id>/editar/`
  - Permite editar datos y resetear password.
  - Reset de password tambien genera PDF.
- Eliminacion:
  - Si el usuario pertenece a una sola empresa, se elimina el usuario.
  - Si pertenece a mas de una, se desvincula solo de la empresa actual.

**Vista global de usuarios**
- Ruta: `/dashboard/admin/usuarios/`
- Muestra cards con acceso rapido a editar usuario.
- Filtros:
  - texto (nombre/apellido/email/empresa),
  - empresa,
  - rol (`dueno`/`empleado`).
- Orden alfabetico: `A-Z` o `Z-A`.
- Presentacion: una card por usuario (sin repetir por multiples empresas).

**Suscripciones y pagos**
- Edicion de suscripcion: `/dashboard/admin/empresa/<id>/suscripcion/`
  - Campos editables: `plan`, `periodicidad`, `activa`.
- Registro de pagos:
  - `fecha_pago` se fija automaticamente al dia actual.
  - `monto` se calcula automaticamente desde el plan:
    - mensual -> `plan.precio_mensual`
    - anual -> `plan.precio_anual`
  - `periodo` se toma automaticamente de la `suscripcion.periodicidad`.
  - Actualiza vencimiento segun periodo cobrado:
    - mensual: +1 mes
    - anual: +12 meses
  - Reglas de periodo:
    - Si el ultimo pago fue anual, no permite mensual hasta estar a <= 7 dias de vencer.

**Contabilidad**
- Ruta: `/dashboard/admin/contabilidad/`
- Metricas:
  - Ingresos historicos, del mes, ultimos 30 dias.
  - Cantidad de pagos y ticket promedio.
  - Empresas al dia, vencidas y por vencer.
- Filtros:
  - anio, mes, rubro.
  - El estado financiero se calcula con fecha de corte coherente al filtro temporal.

**Complementos**
- Ruta base: `/dashboard/admin/complementos/`
- Altas operativas para:
  - Rubros
  - Paises
  - Provincias
  - Localidades
  - Planes
  - Servicios base

**Acceso y reglas de sesion**
- Usuarios admin (`is_staff` o `is_superuser`) acceden a dashboard admin.
- Usuarios no admin:
  - Si tienen una empresa, se usa esa empresa.
  - Si tienen varias, se muestra selector de empresa.
  - Si todas sus empresas estan inactivas, se bloquea acceso.
- La habilitacion tambien depende de suscripcion vigente/activa.

**Tareas programables**
- Comando: `python manage.py sync_suscripciones --quiet`
- Uso recomendado: 2 veces al dia por scheduler.
