# Datos Base

Existe un comando para cargar informacion inicial necesaria para pruebas y configuracion.

**Comando**
```powershell
python manage.py seed_initial_data
```

**Que carga**
- Pais: Argentina.
- Provincias: Mendoza.
- Localidades de Mendoza (Capital, Godoy Cruz, Guaymallen, Maipu, Lujan de Cuyo, Las Heras, San Martin, Rivadavia, Junin, Tunuyan, Tupungato, San Carlos, San Rafael, General Alvear, Malargue).
- Rubros: Peluqueria, Barberia, Peluqueria Canina.
- Servicios base asociados a cada rubro.

El comando es idempotente: si los registros ya existen, no los duplica.
