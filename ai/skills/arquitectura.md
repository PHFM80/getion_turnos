# Arquitectura del sistema

## Organización general
- El proyecto está organizado en apps Django separadas por dominio.
- Cada app debe mantener responsabilidades claras y acotadas.
- No mezclar lógica de diferentes dominios en una misma app.

## Estructura por responsabilidad

### Models
- Definen la estructura de datos.
- No deben contener lógica de negocio compleja.

### Views / Controllers
- Manejan la entrada y salida (request/response).
- No deben contener lógica de negocio.
- Solo orquestan llamadas a servicios.

### Services
- Contienen la lógica de negocio.
- Centralizan reglas del sistema.
- Deben ser reutilizables y claros.

### Integraciones
- Toda integración externa debe estar aislada.
- No mezclar lógica de integración con lógica de negocio.

## Organización del código
- Cada funcionalidad debe ubicarse en el archivo correspondiente.
- Evitar archivos grandes con múltiples responsabilidades.
- Dividir código cuando crezca en complejidad.

## Escalabilidad
- El sistema debe poder crecer sin necesidad de reestructuración completa.
- Agregar nuevas funcionalidades sin romper las existentes.

## Consistencia
- Mantener nombres claros y coherentes en todo el proyecto.
- Seguir los mismos patrones en todas las apps.

## Modificaciones
- Antes de agregar código, revisar si ya existe algo similar.
- Evitar refactorizaciones innecesarias.
- Mantener compatibilidad con el código existente.