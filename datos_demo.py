"""Carga datos ficticios de ejemplo para probar los reportes."""
from prospectos.db import BaseDatos
from prospectos.servicio import GestorProspectos

DEMO = [
    ("Laura Méndez", "5512345678", "Instagram", ("Auto", "Nissan", "Versa", 2021), ("Amplia", 9800), True),
    ("Carlos Ruiz", "5523456789", "Facebook", ("Moto", "Italika", "FT150", 2023), ("Responsabilidad Civil", 1900), True),
    ("Ana Torres", "5534567890", "TikTok", ("Auto", "Chevrolet", "Aveo", 2019), ("Limitada", 7200), False),
    ("Jorge Pérez", "5545678901", "Facebook", None, None, False),
    ("Mariana Díaz", "5556789012", "Referido", ("Auto", "Mazda", "3", 2024), ("Premium", 16500), True),
    ("Luis Gómez", "5567890123", "Instagram", ("Moto", "Honda", "CB190R", 2022), ("Amplia", 4300), False),
]

if __name__ == "__main__":
    g = GestorProspectos(BaseDatos())
    for nombre, tel, origen, vehiculo, cot, acepta in DEMO:
        pid = g.agregar_prospecto(nombre, tel, "", origen)
        if vehiculo:
            vid = g.agregar_vehiculo(pid, *vehiculo)
            cid = g.cotizar(vid, *cot)
            if acepta:
                g.aceptar_cotizacion(cid)
    print(f"{len(DEMO)} prospectos de ejemplo cargados en prospectos.db")
