# Setup

**Requisitos**
- Python compatible con `Django==6.0.3`.
- Base de datos: SQLite en desarrollo o Postgres en produccion.

**Variables de entorno**
Se cargan desde `.env` en la raiz del proyecto.
- `ENVIRONMENT` = `development` o `production`.
- `DEBUG` = `1` o `0`.
- `SECRET_KEY` = clave secreta de Django.
- `ALLOWED_HOSTS` = lista separada por comas.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` (solo cuando `ENVIRONMENT=production`).

**Flujo recomendado en desarrollo**
1. Crear entorno virtual e instalar dependencias.
2. Revisar `.env` y ajustar valores.
3. Ejecutar migraciones.
4. Cargar datos base.
5. Crear superusuario.
6. Iniciar servidor.

Comandos:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
python manage.py runserver
```

**Notas de base de datos**
- En desarrollo se usa SQLite en `db.sqlite3`.
- En produccion se valida que existan variables de Postgres antes de iniciar.
