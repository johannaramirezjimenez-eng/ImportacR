"""
Validación del motor de cálculo contra los ejemplos oficiales del
Instructivo de cálculo de la obligación tributaria (DGA, 2023)
y contra las reglas de desgravación del Anexo 3.3 del CAFTA-DR.

Ejecutar con:  python validacion.py
"""
from motor import calcular, desgravacion_cafta

WHISKY_SECCION_M = {
    "fob": 3000.0, "flete": 0.0, "seguro": 0.0, "tc": 602.0, "kilos": 0, "puerto": "Moín (Limón)",
    "otros_cargos": 0, "usa_pref": False,
    "tasas": {"dai": 14, "sc": 10, "l6946": 1, "inder": 8, "ifam": 10, "iva": 13, "esp": 4.80, "pref": 0},
    "alcohol": {"cajas": 100, "por_caja": 12, "ml": 750, "grado": 40},
}
RON_CHILE_SECCION_N = {
    **WHISKY_SECCION_M, "usa_pref": True,
    "tasas": {"dai": 14, "sc": 10, "l6946": 1, "inder": 8, "ifam": 10, "iva": 13, "esp": 4.80, "pref": 0},
    "alcohol": {"cajas": 100, "por_caja": 12, "ml": 760, "grado": 40},
}

pruebas = [
    ("Whisky, sección M: IVA", calcular(WHISKY_SECCION_M)["iva"], 577193.16),
    ("Whisky, sección M: INDER", dict((k, v) for k, *_, v in calcular(WHISKY_SECCION_M)["lineas"])["inder"], 182622.72),
    ("Whisky, sección M: IFAM", dict((k, v) for k, *_, v in calcular(WHISKY_SECCION_M)["lineas"])["ifam"], 246540.67),
    ("Ron Chile con TLC, sección N: IVA", calcular(RON_CHILE_SECCION_N)["iva"], 534445.70),
    ("Ron Chile con TLC, sección N: total", calcular(RON_CHILE_SECCION_N)["obligacion"], 2839566.50),
    ("CAFTA-DR categoría C, año 5 (2010), base 15 %", desgravacion_cafta("C", 15, 2010)["tasa"], 7.5),
    ("CAFTA-DR categoría E, año 8 (2013), base 15 %", desgravacion_cafta("E", 15, 2013)["tasa"], 12.5),
    ("CAFTA-DR categoría A en 2026", desgravacion_cafta("A", 15, 2026)["tasa"], 0.0),
]

if __name__ == "__main__":
    fallas = 0
    for nombre, obtenido, esperado in pruebas:
        ok = abs(obtenido - esperado) < 0.005
        fallas += not ok
        print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido:,.2f} · esperado {esperado:,.2f}")
    print("\nTodas las pruebas pasaron." if not fallas else f"\n{fallas} prueba(s) fallaron.")
