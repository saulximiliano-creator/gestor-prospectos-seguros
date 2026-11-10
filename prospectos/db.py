"""Capa de acceso a datos.

Por defecto usa SQLite (no requiere instalar nada). Para usar MySQL:
    export DB_ENGINE=mysql DB_HOST=localhost DB_USER=root DB_PASSWORD=... DB_NAME=prospectos_seguros
y ejecutar antes sql/schema_mysql.sql.
"""
import os
import sqlite3
from pathlib import Path

ETAPAS = ("Nuevo", "Contactado", "Cotizado", "Cerrado", "Perdido")
ORIGENES = ("Facebook", "Instagram", "TikTok", "WhatsApp", "Referido", "Otro")
COBERTURAS = ("Responsabilidad Civil", "Limitada", "Amplia", "Premium")

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS prospecto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    correo TEXT,
    origen TEXT NOT NULL DEFAULT 'Otro',
    etapa TEXT NOT NULL DEFAULT 'Nuevo',
    fecha_alta TEXT NOT NULL DEFAULT (date('now'))
);
CREATE TABLE IF NOT EXISTS vehiculo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospecto_id INTEGER NOT NULL REFERENCES prospecto(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('Auto','Moto')),
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    anio INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cotizacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_id INTEGER NOT NULL REFERENCES vehiculo(id) ON DELETE CASCADE,
    cobertura TEXT NOT NULL,
    prima_anual REAL NOT NULL CHECK (prima_anual > 0),
    fecha TEXT NOT NULL DEFAULT (date('now')),
    aceptada INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS seguimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospecto_id INTEGER NOT NULL REFERENCES prospecto(id) ON DELETE CASCADE,
    fecha_programada TEXT NOT NULL,
    nota TEXT,
    hecho INTEGER NOT NULL DEFAULT 0
);
"""


class BaseDatos:
    def __init__(self, ruta_sqlite="prospectos.db"):
        self.engine = os.getenv("DB_ENGINE", "sqlite").lower()
        if self.engine == "mysql":
            import mysql.connector  # pip install mysql-connector-python
            self.con = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "prospectos_seguros"),
            )
            self.ph = "%s"
        else:
            self.con = sqlite3.connect(ruta_sqlite)
            self.con.execute("PRAGMA foreign_keys = ON")
            self.con.executescript(SCHEMA_SQLITE)
            self.ph = "?"

    def _sql(self, consulta):
        """Adapta los marcadores de parámetros (? en SQLite, %s en MySQL)."""
        return consulta.replace("?", self.ph)

    def ejecutar(self, consulta, params=()):
        cur = self.con.cursor()
        cur.execute(self._sql(consulta), params)
        self.con.commit()
        return cur.lastrowid

    def consultar(self, consulta, params=()):
        cur = self.con.cursor()
        cur.execute(self._sql(consulta), params)
        columnas = [c[0] for c in cur.description]
        return [dict(zip(columnas, fila)) for fila in cur.fetchall()]

    def cerrar(self):
        self.con.close()
