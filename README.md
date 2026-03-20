# Gestion Turnos

Proyecto Django para gestionar turnos de empresas con servicios, agenda, suscripciones y comunicaciones con clientes.

**Guia rapida**
1. Crear y activar un entorno virtual.
2. Instalar dependencias.
3. Configurar variables de entorno.
4. Aplicar migraciones y cargar datos base.
5. Levantar el servidor.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
python manage.py runserver
```

**Documentacion**
- `docs/overview.md` - Panorama funcional y entidades principales.
- `docs/setup.md` - Configuracion local y variables de entorno.
- `docs/apps.md` - Detalle por aplicacion y modelos clave.
- `docs/seed.md` - Datos base y comando de carga.
- `docs/arquitectura.md` - Arquitectura actual y relaciones entre apps.
- `docs/templates.md` - Vistas, herencia y orden de assets.
