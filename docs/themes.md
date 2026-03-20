# Themes

Este documento describe el sistema de modo claro/oscuro y como extenderlo.

**Archivos**
- `static/css/themes/theme-light.css`
  - Define las variables CSS para el modo claro.
- `static/css/themes/theme-dark.css`
  - Define las variables CSS para el modo oscuro.
- `static/css/base.css`
  - Consume las variables para fondos, texto, botones y layouts.
- `static/js/base.js`
  - Aplica y persiste el tema en `localStorage`.

**Como funciona**
1. `templates/base.html` setea `data-theme` en `<html>` al cargar, priorizando `localStorage`.
2. Los archivos de theme declaran variables bajo `[data-theme="light"]` y `[data-theme="dark"]`.
3. El boton de toggle cambia el atributo sin recargar la pagina.

**Persistencia**
- La clave es `gt-theme` en `localStorage`.
- El modo se mantiene entre vistas (home, dashboard, formularios) sin perder estado de inputs.

**Agregar un nuevo theme**
1. Crear un archivo en `static/css/themes/` con las variables necesarias.
2. Cargarlo en `templates/base.html` antes de `static/css/base.css`.
3. Ajustar `static/js/base.js` si se desea un selector con mas de dos opciones.
