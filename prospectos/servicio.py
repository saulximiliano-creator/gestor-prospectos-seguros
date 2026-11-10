"""Reglas de negocio del gestor de prospectos."""
import csv
import re
from datetime import date, timedelta

from .db import BaseDatos, COBERTURAS, ETAPAS, ORIGENES

RE_TELEFONO = re.compile(r"^\d{10}$")
RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


class ErrorValidacion(ValueError):
    pass


class GestorProspectos:
    def __init__(self, db: BaseDatos):
        self.db = db

    # ---------- Prospectos ----------
    def agregar_prospecto(self, nombre, telefono="", correo="", origen="Otro"):
        nombre = nombre.strip()
        if len(nombre) < 3:
            raise ErrorValidacion("El nombre debe tener al menos 3 caracteres.")
        if telefono and not RE_TELEFONO.match(telefono):
            raise ErrorValidacion("El teléfono debe tener 10 dígitos.")
        if correo and not RE_CORREO.match(correo):
            raise ErrorValidacion("Correo inválido.")
        if origen not in ORIGENES:
            raise ErrorValidacion(f"Origen debe ser uno de: {', '.join(ORIGENES)}")
        pid = self.db.ejecutar(
            "INSERT INTO prospecto (nombre, telefono, correo, origen) VALUES (?, ?, ?, ?)",
            (nombre, telefono, correo, origen),
        )
        # Regla: todo prospecto nuevo recibe un seguimiento automático al día siguiente
        self.programar_seguimiento(pid, date.today() + timedelta(days=1), "Primer contacto")
        return pid

    def cambiar_etapa(self, prospecto_id, etapa):
        if etapa not in ETAPAS:
            raise ErrorValidacion(f"Etapa debe ser una de: {', '.join(ETAPAS)}")
        self.db.ejecutar("UPDATE prospecto SET etapa = ? WHERE id = ?", (etapa, prospecto_id))

    def buscar(self, texto):
        patron = f"%{texto}%"
        return self.db.consultar(
            "SELECT * FROM prospecto WHERE nombre LIKE ? OR telefono LIKE ? ORDER BY nombre",
            (patron, patron),
        )

    def listar(self, etapa=None):
        if etapa:
            return self.db.consultar("SELECT * FROM prospecto WHERE etapa = ? ORDER BY id", (etapa,))
        return self.db.consultar("SELECT * FROM prospecto ORDER BY id")

    # ---------- Vehículos y cotizaciones ----------
    def agregar_vehiculo(self, prospecto_id, tipo, marca, modelo, anio):
        if tipo not in ("Auto", "Moto"):
            raise ErrorValidacion("Tipo debe ser Auto o Moto.")
        if not 1980 <= int(anio) <= date.today().year + 1:
            raise ErrorValidacion("Año de vehículo fuera de rango.")
        return self.db.ejecutar(
            "INSERT INTO vehiculo (prospecto_id, tipo, marca, modelo, anio) VALUES (?, ?, ?, ?, ?)",
            (prospecto_id, tipo, marca, modelo, int(anio)),
        )

    def cotizar(self, vehiculo_id, cobertura, prima_anual):
        if cobertura not in COBERTURAS:
            raise ErrorValidacion(f"Cobertura debe ser una de: {', '.join(COBERTURAS)}")
        if float(prima_anual) <= 0:
            raise ErrorValidacion("La prima debe ser mayor a 0.")
        cid = self.db.ejecutar(
            "INSERT INTO cotizacion (vehiculo_id, cobertura, prima_anual) VALUES (?, ?, ?)",
            (vehiculo_id, cobertura, float(prima_anual)),
        )
        # Regla: al cotizar, el prospecto avanza a 'Cotizado' si estaba en una etapa anterior
        self.db.ejecutar(
            """UPDATE prospecto SET etapa = 'Cotizado'
               WHERE id = (SELECT prospecto_id FROM vehiculo WHERE id = ?)
                 AND etapa IN ('Nuevo', 'Contactado')""",
            (vehiculo_id,),
        )
        return cid

    def aceptar_cotizacion(self, cotizacion_id):
        self.db.ejecutar("UPDATE cotizacion SET aceptada = 1 WHERE id = ?", (cotizacion_id,))
        self.db.ejecutar(
            """UPDATE prospecto SET etapa = 'Cerrado' WHERE id = (
                   SELECT v.prospecto_id FROM cotizacion c JOIN vehiculo v ON v.id = c.vehiculo_id
                   WHERE c.id = ?)""",
            (cotizacion_id,),
        )

    # ---------- Seguimientos ----------
    def programar_seguimiento(self, prospecto_id, fecha, nota=""):
        return self.db.ejecutar(
            "INSERT INTO seguimiento (prospecto_id, fecha_programada, nota) VALUES (?, ?, ?)",
            (prospecto_id, str(fecha), nota),
        )

    def pendientes(self, hasta=None):
        hasta = str(hasta or date.today())
        return self.db.consultar(
            """SELECT s.id, s.fecha_programada, s.nota, p.nombre, p.telefono, p.etapa
               FROM seguimiento s JOIN prospecto p ON p.id = s.prospecto_id
               WHERE s.hecho = 0 AND s.fecha_programada <= ?
                 AND p.etapa NOT IN ('Cerrado', 'Perdido')
               ORDER BY s.fecha_programada""",
            (hasta,),
        )

    def marcar_hecho(self, seguimiento_id):
        self.db.ejecutar("UPDATE seguimiento SET hecho = 1 WHERE id = ?", (seguimiento_id,))

    # ---------- Reportes ----------
    def embudo(self):
        filas = self.db.consultar("SELECT etapa, COUNT(*) AS total FROM prospecto GROUP BY etapa")
        conteo = {f["etapa"]: f["total"] for f in filas}
        return {e: conteo.get(e, 0) for e in ETAPAS}

    def efectividad_por_origen(self):
        return self.db.consultar(
            """SELECT origen,
                      COUNT(*) AS prospectos,
                      SUM(CASE WHEN etapa = 'Cerrado' THEN 1 ELSE 0 END) AS cerrados,
                      ROUND(100.0 * SUM(CASE WHEN etapa = 'Cerrado' THEN 1 ELSE 0 END) / COUNT(*), 1)
                          AS tasa_cierre_pct
               FROM prospecto GROUP BY origen ORDER BY tasa_cierre_pct DESC, prospectos DESC"""
        )

    def prima_por_cobertura(self):
        return self.db.consultar(
            """SELECT cobertura, COUNT(*) AS cotizaciones,
                      ROUND(AVG(prima_anual), 2) AS prima_promedio,
                      SUM(CASE WHEN aceptada = 1 THEN 1 ELSE 0 END) AS aceptadas
               FROM cotizacion GROUP BY cobertura ORDER BY prima_promedio"""
        )

    def exportar_csv(self, ruta):
        filas = self.listar()
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            if not filas:
                return 0
            w = csv.DictWriter(f, fieldnames=filas[0].keys())
            w.writeheader()
            w.writerows(filas)
        return len(filas)
