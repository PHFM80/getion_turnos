# Templates

Este documento describe las vistas HTML y el orden de carga de assets.

**Estructura y herencia**
```
base.html
├── index.html
│   └── login.html
├── servicios.html
│   └── servicios_turno.html
└── dashboard/base.html
    ├── dashboard/index.html
    ├── dashboard/seleccionar_empresa.html
    └── dashboard/admin/*
```

- `templates/base.html`
  - Base global.
  - Carga Bootstrap, tipografia, themes y `static/css/base.css`.
  - Incluye boton de modo claro/oscuro.
- `templates/index.html`
  - Home publica.
  - Carga `static/css/index.css` y `static/js/index.js`.
- `templates/login.html`
  - Login con mensajes de error y toggle de password.
- `templates/servicios.html`
  - Listado publico de empresas con filtro por rubro.
- `templates/servicios_turno.html`
  - Seleccion de horario y formulario de solicitud de turno (mock).
- `templates/dashboard/base.html`
  - Layout del dashboard.
  - Sidebar con estado activo dinamico segun ruta.
  - Carga `static/css/dashboard.css` y `static/js/dashboard.js`.
- `templates/dashboard/seleccionar_empresa.html`
  - Selector para usuarios con mas de una empresa.
- `templates/dashboard/admin/empresa*.html`
  - CRUD operativo de empresa, usuarios, suscripcion y pagos.
- `templates/dashboard/admin/complemento*.html`
  - Carga de catalogos base (rubros, geo, planes, servicios base).
- `templates/dashboard/admin/contabilidad.html`
  - Metricas financieras y filtros por anio/mes/rubro.

**Orden de assets**
1. Bootstrap CSS.
2. `static/css/themes/theme-light.css`.
3. `static/css/themes/theme-dark.css`.
4. `static/css/base.css`.
5. CSS especifico (`index.css`, `dashboard.css`).
6. Bootstrap JS (bundle).
7. `static/js/base.js`.
8. JS especifico (`index.js`, `dashboard.js`).

**Comportamientos relevantes de frontend**
- Theme persistente via `localStorage` (`gt-theme`).
- Filtros dinamicos en:
  - Complementos (provincias/localidades/servicios base).
  - Empresas (busqueda y estado).
  - Servicios publicos (rubro).
- Dependencias geograficas en formularios de empresa:
  - Pais -> Provincia -> Localidad.
- Tooltips en contabilidad para aclarar reglas de corte temporal.

**Rutas relacionadas**
- Publico: `/`, `/servicios/`, `/servicios/turno/<slug>/`, `/login/`.
- Dashboard usuario: `/dashboard/`, `/dashboard/empresa/<id>/`.
- Dashboard admin: `/dashboard/admin/`, `/dashboard/admin/empresa/`, `/dashboard/admin/complementos/`, `/dashboard/admin/contabilidad/`.
