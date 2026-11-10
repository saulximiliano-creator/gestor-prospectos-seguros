"""Gestor de prospectos de seguros de auto y moto — interfaz de consola."""
import sys

from prospectos.db import BaseDatos, COBERTURAS, ETAPAS, ORIGENES
from prospectos.servicio import ErrorValidacion, GestorProspectos


def tabla(filas, columnas=None):
    if not filas:
        print("(sin resultados)")
        return
    columnas = columnas or list(filas[0].keys())
    anchos = {c: max(len(str(c)), *(len(str(f[c])) for f in filas)) for c in columnas}
    print("  ".join(str(c).ljust(anchos[c]) for c in columnas))
    print("  ".join("-" * anchos[c] for c in columnas))
    for f in filas:
        print("  ".join(str(f[c]).ljust(anchos[c]) for c in columnas))


def elegir(msg, opciones):
    for i, o in enumerate(opciones, 1):
        print(f"  {i}. {o}")
    while True:
        r = input(msg)
        if r.isdigit() and 1 <= int(r) <= len(opciones):
            return opciones[int(r) - 1]
        print("Opción inválida.")


MENU = """
===== GESTOR DE PROSPECTOS DE SEGUROS =====
 1. Nuevo prospecto          6. Seguimientos pendientes
 2. Listar / buscar          7. Marcar seguimiento hecho
 3. Agregar vehículo         8. Programar seguimiento
 4. Registrar cotización     9. Reportes
 5. Cambiar etapa           10. Exportar a CSV
 0. Salir
"""


def main():
    db = BaseDatos()
    g = GestorProspectos(db)
    while True:
        print(MENU)
        op = input("Opción: ").strip()
        try:
            if op == "1":
                pid = g.agregar_prospecto(
                    input("Nombre: "), input("Teléfono (10 dígitos): "),
                    input("Correo: "), elegir("Origen: ", ORIGENES))
                print(f"Prospecto #{pid} creado con seguimiento para mañana.")
            elif op == "2":
                texto = input("Buscar (vacío = todos): ").strip()
                tabla(g.buscar(texto) if texto else g.listar(),
                      ["id", "nombre", "telefono", "origen", "etapa", "fecha_alta"])
            elif op == "3":
                vid = g.agregar_vehiculo(int(input("ID prospecto: ")), elegir("Tipo: ", ("Auto", "Moto")),
                                         input("Marca: "), input("Modelo: "), int(input("Año: ")))
                print(f"Vehículo #{vid} registrado.")
            elif op == "4":
                cid = g.cotizar(int(input("ID vehículo: ")), elegir("Cobertura: ", COBERTURAS),
                                float(input("Prima anual $: ")))
                print(f"Cotización #{cid} registrada.")
                if input("¿El cliente la aceptó? (s/n): ").lower() == "s":
                    g.aceptar_cotizacion(cid)
                    print("¡Venta cerrada!")
            elif op == "5":
                g.cambiar_etapa(int(input("ID prospecto: ")), elegir("Nueva etapa: ", ETAPAS))
                print("Etapa actualizada.")
            elif op == "6":
                tabla(g.pendientes())
            elif op == "7":
                g.marcar_hecho(int(input("ID seguimiento: ")))
                print("Listo.")
            elif op == "8":
                g.programar_seguimiento(int(input("ID prospecto: ")), input("Fecha (AAAA-MM-DD): "),
                                        input("Nota: "))
                print("Seguimiento programado.")
            elif op == "9":
                print("\n-- Embudo de ventas --")
                for etapa, n in g.embudo().items():
                    print(f"{etapa:<11} {'█' * n} {n}")
                print("\n-- Efectividad por red social --")
                tabla(g.efectividad_por_origen())
                print("\n-- Prima promedio por cobertura --")
                tabla(g.prima_por_cobertura())
            elif op == "10":
                n = g.exportar_csv("prospectos.csv")
                print(f"{n} prospectos exportados a prospectos.csv")
            elif op == "0":
                db.cerrar()
                sys.exit(0)
            else:
                print("Opción no válida.")
        except ErrorValidacion as e:
            print(f"Error: {e}")
        except ValueError:
            print("Error: dato numérico inválido.")


if __name__ == "__main__":
    main()
