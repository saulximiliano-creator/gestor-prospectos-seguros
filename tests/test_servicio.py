import unittest
from datetime import date, timedelta

from prospectos.db import BaseDatos
from prospectos.servicio import ErrorValidacion, GestorProspectos


class TestGestor(unittest.TestCase):
    def setUp(self):
        self.db = BaseDatos(":memory:")
        self.g = GestorProspectos(self.db)

    def tearDown(self):
        self.db.cerrar()

    def test_alta_crea_seguimiento_automatico(self):
        pid = self.g.agregar_prospecto("Laura Méndez", "5512345678", "", "Instagram")
        manana = date.today() + timedelta(days=1)
        pend = self.g.pendientes(hasta=manana)
        self.assertEqual(len(pend), 1)
        self.assertEqual(pend[0]["nombre"], "Laura Méndez")
        self.assertEqual(self.g.listar()[0]["id"], pid)

    def test_validaciones(self):
        with self.assertRaises(ErrorValidacion):
            self.g.agregar_prospecto("Al")
        with self.assertRaises(ErrorValidacion):
            self.g.agregar_prospecto("Carlos", telefono="123")
        with self.assertRaises(ErrorValidacion):
            self.g.agregar_prospecto("Carlos", correo="no-es-correo")
        with self.assertRaises(ErrorValidacion):
            self.g.agregar_prospecto("Carlos", origen="Twitter")

    def test_flujo_cotizar_y_cerrar(self):
        pid = self.g.agregar_prospecto("Ana Torres", origen="TikTok")
        vid = self.g.agregar_vehiculo(pid, "Moto", "Italika", "FT150", 2023)
        cid = self.g.cotizar(vid, "Amplia", 3500)
        self.assertEqual(self.g.listar()[0]["etapa"], "Cotizado")
        self.g.aceptar_cotizacion(cid)
        self.assertEqual(self.g.listar()[0]["etapa"], "Cerrado")
        # un prospecto cerrado ya no aparece en pendientes
        self.assertEqual(self.g.pendientes(hasta=date.today() + timedelta(days=5)), [])

    def test_reportes(self):
        for i, origen in enumerate(["Facebook", "Facebook", "Instagram"]):
            pid = self.g.agregar_prospecto(f"Cliente {i}", origen=origen)
            if i == 0:
                self.g.cambiar_etapa(pid, "Cerrado")
        embudo = self.g.embudo()
        self.assertEqual(embudo["Nuevo"], 2)
        self.assertEqual(embudo["Cerrado"], 1)
        fb = next(r for r in self.g.efectividad_por_origen() if r["origen"] == "Facebook")
        self.assertEqual(fb["tasa_cierre_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
