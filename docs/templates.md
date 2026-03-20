# Templates

Este documento describe las vistas HTML creadas y el orden correcto de carga de assets.

**Estructura y herencia**
```
base.html
├── index.html
│   └── login.html
└── dashboard/base.html
    └── dashboard/index.html
```

- `templates/base.html`
  - Base global.
  - Incluye Bootstrap, tipografia y `static/css/base.css`.
  - Define bloques `extra_css`, `content`, `extra_js`.
- `templates/index.html`
  - Hereda de `base.html`.
  - Carga `static/css/index.css` y `static/js/index.js`.
- `templates/login.html`
  - Hereda de `index.html`.
  - Reutiliza el layout del home.
- `templates/dashboard/base.html`
  - Hereda de `base.html`.
  - Carga `static/css/dashboard.css` y `static/js/dashboard.js`.
  - Define bloque `dashboard_content` para vistas internas.
- `templates/dashboard/index.html`
  - Hereda de `dashboard/base.html`.

**Regla de `load static`**
- Todos los templates que usen `{% static %}` deben declarar `{% load static %}` al inicio.

**Orden de assets**
1. Bootstrap CSS.
2. `static/css/base.css`.
3. CSS especifico (`index.css`, `dashboard.css`).
4. Bootstrap JS (bundle).
5. `static/js/base.js`.
6. JS especifico (`index.js`, `dashboard.js`).

**Rutas relacionadas**
- `/` -> `index.html`
- `/login/` -> `login.html`
- `/dashboard/` -> `dashboard/index.html`
- `/logout/` -> POST de cierre de sesion
