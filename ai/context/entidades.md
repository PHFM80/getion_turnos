# Entidades del Sistema

## Core

### Usuario
- email
- nombre
- apellido
- telefono
- localidad

### UsuarioEmpresa
- usuario
- empresa
- rol
- activo

### Cliente
- nombre
- telefono
- email
- empresa

---

## Geografía

### Pais
- nombre
- codigo

### Provincia
- nombre
- pais

### Localidad
- nombre
- provincia

---

## Empresas

### Rubro
- nombre

### Empresa
- nombre
- telefono
- direccion
- localidad
- rubro
- activo

---

## Suscripciones

### Plan
- nombre
- limite_simultaneo
- precio_mensual
- precio_anual

### Suscripcion
- empresa
- plan
- activa
- periodicidad
- fecha_inicio
- fecha_vencimiento

### Pago
- suscripcion
- fecha_pago
- monto
- periodo

---

## Servicios

### ServicioBase
- nombre
- rubro

### ServicioEmpresa
- empresa
- servicio_base
- duracion
- precio
- activo

---

## Agenda

### CapacidadEmpresa
- empresa
- capacidad
- nombre

### CapacidadPuesto
- capacidad_empresa
- nombre
- orden

### HorarioEmpresa
- empresa
- dia_semana
- hora_inicio
- hora_fin

### BloqueoEmpresa
- empresa
- fecha
- hora_inicio
- hora_fin
- motivo

### Turno
- empresa
- cliente
- servicio_empresa
- empleado
- fecha
- hora_inicio
- hora_fin
- estado

---

## Comunicaciones

### Conversacion
- empresa
- cliente
- estado
- activa
- ultimo_mensaje

### Notificacion
- empresa
- cliente
- canal
- tipo
- estado
- fecha_envio