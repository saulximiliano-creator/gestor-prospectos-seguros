# Gestor de Prospectos de Seguros (Python + SQL)

CRM de consola para dar seguimiento a prospectos de **seguros de auto y moto** que llegan por redes sociales: registro de clientes y vehículos, cotizaciones por tipo de cobertura, seguimientos programados y reportes del embudo de ventas.

Nació de mi trabajo como **asesor de seguros**, donde necesitaba saber a quién llamar cada día y qué red social me traía más ventas.

## Qué demuestra este proyecto

- **Diseño de base de datos relacional**: 4 tablas normalizadas con llaves foráneas, `CHECK`, índices y vistas (`sql/schema_mysql.sql`)
- **Consultas SQL**: `JOIN`, `GROUP BY`, agregaciones condicionales (`SUM(CASE …)`), subconsultas
- **Python** con separación por capas: acceso a datos (`db.py`), reglas de negocio (`servicio.py`) e interfaz (`main.py`)
- **Compatibilidad SQLite / MySQL** mediante una capa de datos que adapta los parámetros
- **Validación de datos** (teléfono, correo, rangos) con expresiones regulares
- **Pruebas unitarias** con `unittest` sobre una base en memoria

## Modelo de datos

```
prospecto 1───N vehiculo 1───N cotizacion
    │
    └────N seguimiento
```

| Tabla | Campos clave |
|---|---|
| `prospecto` | nombre, teléfono, correo, origen (Facebook, Instagram, TikTok…), etapa |
| `vehiculo` | tipo (Auto/Moto), marca, modelo, año |
| `cotizacion` | cobertura (RC, Limitada, Amplia, Premium), prima anual, aceptada |
| `seguimiento` | fecha programada, nota, hecho |

## Reglas de negocio

- Al registrar un prospecto se programa automáticamente un seguimiento para el día siguiente.
- Al cotizar, el prospecto pasa a etapa **Cotizado**; al aceptar, a **Cerrado**.
- Los prospectos cerrados o perdidos dejan de aparecer en seguimientos pendientes.

## Cómo ejecutarlo

```bash
python3 datos_demo.py          # (opcional) carga datos ficticios
python3 main.py                # menú interactivo
python3 -m unittest discover -s tests   # pruebas
```

Funciona con SQLite sin instalar nada. Para usar **MySQL**:

```bash
pip install -r requirements.txt
mysql -u root -p < sql/schema_mysql.sql
export DB_ENGINE=mysql DB_USER=root DB_PASSWORD=tu_password
python3 main.py
```

## Ejemplo de reportes

```
-- Embudo de ventas --
Nuevo       █ 1
Cotizado    ██ 2
Cerrado     ███ 3

-- Efectividad por red social --
origen     prospectos  cerrados  tasa_cierre_pct
Referido   1           1         100.0
Facebook   2           1         50.0
Instagram  2           1         50.0
TikTok     1           0         0.0
```

## Próximas mejoras

- [ ] Interfaz web con Flask
- [ ] Recordatorios automáticos por correo
- [ ] Gráficas del embudo con matplotlib

---
Autor: **Saúl Maximiliano García Ramírez**, estudiante de Ingeniería en Sistemas Computacionales (ESCOM-IPN). Los datos de ejemplo son ficticios.
