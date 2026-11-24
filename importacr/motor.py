"""
Motor de cálculo de ImportaCR.

1. Obligación tributaria aduanera de importación, según el
   "Instructivo cálculo para la obligación tributaria para la importación
   de mercancías" (Dirección General de Aduanas, MH-DGA-PRO09-INS-004, 2023).
2. Desgravación arancelaria del CAFTA-DR para la Lista de Costa Rica
   (Anexo 3.3, párrafo 1, y Notas Generales de Costa Rica, párrafo 3).
"""
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def r2(x):
    """Redondea a dos decimales (medio hacia arriba), como los ejemplos del instructivo."""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def colones(x):
    """Formato monetario costarricense: ¢1 234 567,89"""
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"¢{s}"


def pct(x, dec=2):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return f"{s} %"


# --------------------------------------------------------------------------
# 1. Obligación tributaria
# --------------------------------------------------------------------------

def calcular(exp, preferencial=None, tipo_cambio=None):
    """
    Calcula la obligación tributaria de un expediente.

    exp: diccionario con fob, flete, seguro, tc, tasas, usa_pref, alcohol,
         puerto, kilos y otros_cargos.
    preferencial / tipo_cambio: permiten simular escenarios sin cambiar el expediente.
    """
    t = exp["tasas"]
    usa_pref = exp["usa_pref"] if preferencial is None else preferencial
    tc = exp["tc"] if tipo_cambio is None else tipo_cambio

    va_usd = exp["fob"] + exp["flete"] + exp["seguro"]
    va = r2(va_usd * tc)
    lineas = []

    dai = l6946 = pref = 0.0
    if usa_pref:
        # Trato preferencial: sustituye el DAI y la Ley 6946 por la tasa del tratado.
        pref = r2(va * t["pref"] / 100)
        lineas.append(("pref", "Trato preferencial (sustituye DAI y Ley 6946)",
                       f"(VA × TC) × {pct(t['pref'])}", pref))
    else:
        dai = r2(va * t["dai"] / 100)
        lineas.append(("dai", "Derechos Arancelarios a la Importación (DAI)",
                       f"(VA × TC) × {pct(t['dai'])}", dai))

    sc = r2((va + dai + pref) * t["sc"] / 100)
    if t["sc"]:
        lineas.append(("sc", "Impuesto selectivo de consumo",
                       f"(VA × TC + DAI) × {pct(t['sc'])}", sc))

    if not usa_pref:
        l6946 = r2(va * t["l6946"] / 100)
        lineas.append(("l6946", "Ley 6946",
                       f"(VA × TC) × {pct(t['l6946'])}", l6946))

    inder = r2((va + dai + pref + sc + l6946) * t["inder"] / 100)
    if t["inder"]:
        lineas.append(("inder", "INDER ad valorem",
                       f"(VA × TC + DAI + SC + Ley 6946) × {pct(t['inder'])}", inder))

    ifam = r2((va + dai + pref + sc + l6946 + inder) * t["ifam"] / 100)
    if t["ifam"]:
        lineas.append(("ifam", "IFAM ad valorem",
                       f"(VA × TC + DAI + SC + Ley 6946 + INDER) × {pct(t['ifam'])}", ifam))

    especifico = 0.0
    alc = exp.get("alcohol")
    if alc and t["esp"]:
        ml_abs = alc["cajas"] * alc["por_caja"] * alc["ml"] * alc["grado"] / 100
        especifico = r2(ml_abs * t["esp"])
        ml_txt = f"{ml_abs:,.0f}".replace(",", " ")
        lineas.append(("esp", "Impuesto específico sobre bebidas alcohólicas",
                       f"{ml_txt} ml de alcohol absoluto × {colones(t['esp'])}", especifico))

    caldera = 0.0
    if exp["puerto"] == "Caldera" and exp["kilos"]:
        ton = exp["kilos"] / 1000
        caldera = (r2(ton * 0.40 * tc) + r2(ton * 0.20 * tc) + r2(ton * 1) + r2(ton * 2))
        caldera = r2(caldera)
        lineas.append(("caldera", "Gravamen portuario de Caldera (Leyes 8461, 6975 y 4429)",
                       f"{ton:.3f} t × (US$0,40 + US$0,20) × TC + ¢3,00 × t", caldera))

    otros = exp.get("otros_cargos", 0) or 0
    if otros:
        lineas.append(("otros", "Otros cargos de la declaración", "Timbres y cargos declarados", otros))

    base_iva = r2(va + dai + pref + sc + l6946 + inder + ifam + especifico + caldera + otros)
    iva = r2(base_iva * t["iva"] / 100)
    lineas.append(("iva", "Impuesto al Valor Agregado (IVA)",
                   f"(VA × TC + tributos y cargos) × {pct(t['iva'])}", iva))

    obligacion = r2(sum(v for k, _, _, v in lineas if k != "otros"))
    return {
        "va_usd": va_usd, "va": va, "tc": tc, "lineas": lineas,
        "base_iva": base_iva, "iva": iva, "obligacion": obligacion,
        "otros": otros, "total": r2(obligacion + otros),
    }


# --------------------------------------------------------------------------
# 2. Desgravación arancelaria CAFTA-DR (Lista de Costa Rica)
# --------------------------------------------------------------------------

# Año uno: año de entrada en vigor del Tratado según el Art. 22.5.1 (Anexo 3.3,
# párrafos 4 y 5). Costa Rica aplica sus tasas como si el Tratado hubiera
# entrado en vigor en esa fecha, aunque para el país rigiera desde 2009.
CAFTA_ANIO_UNO = 2006


def _reduccion_acumulada(cat, n):
    """Porcentaje acumulado de reducción de la tasa base en el año n del Tratado."""
    if n < 1:
        return 0.0
    if cat in ("A", "G"):
        return 100.0
    if cat == "B":                              # 5 etapas anuales iguales
        return min(100.0, n * 20.0)
    if cat == "C":                              # 10 etapas anuales iguales
        return min(100.0, n * 10.0)
    if cat == "D":                              # 15 etapas anuales iguales
        return min(100.0, n * 100 / 15)
    if cat == "E":                              # base años 1-6; 8,25 % (7-10); 13,4 % (11-14); libre año 15
        if n <= 6: return 0.0
        if n <= 10: return 8.25 * (n - 6)
        if n <= 14: return 33.0 + 13.4 * (n - 10)
        return 100.0
    if cat == "F":                              # base años 1-10; 10 etapas; libre año 20
        if n <= 10: return 0.0
        return min(100.0, 10.0 * (n - 10))
    if cat == "M":                              # 2 %, 2 %, 8 % (3-6), 16 % (7-9), libre año 10
        tabla = {1: 2, 2: 4, 3: 12, 4: 20, 5: 28, 6: 36, 7: 52, 8: 68, 9: 84}
        return float(tabla.get(n, 100))
    if cat == "N":                              # 12 etapas anuales iguales
        return min(100.0, n * 100 / 12)
    if cat == "R":                              # base años 1-6; 9 etapas; libre año 15
        if n <= 6: return 0.0
        return min(100.0, (n - 6) * 100 / 9)
    if cat == "S":                              # base 1-5; 8 % (6-10); 12 % (11-14); libre 15
        if n <= 5: return 0.0
        if n <= 10: return 8.0 * (n - 5)
        if n <= 14: return 40.0 + 12.0 * (n - 10)
        return 100.0
    if cat == "T":                              # base 1-4; 8 % (5-9); 10 % (10-14); libre 15
        if n <= 4: return 0.0
        if n <= 9: return 8.0 * (n - 4)
        if n <= 14: return 40.0 + 10.0 * (n - 9)
        return 100.0
    if cat == "U":                              # base 1-10; 13,4 % y 13,3 % (11-13); 15 % (14-16); libre 17
        tabla = {11: 13.4, 12: 26.7, 13: 40.0, 14: 55.0, 15: 70.0, 16: 85.0}
        if n <= 10: return 0.0
        return tabla.get(n, 100.0)
    if cat == "V":                              # base 1-10; 8 % (11-15); 12 % (16-19); libre 20
        if n <= 10: return 0.0
        if n <= 15: return 8.0 * (n - 10)
        if n <= 19: return 40.0 + 12.0 * (n - 15)
        return 100.0
    return None                                 # H u otra: sin preferencia


LIBRE_DESDE = {"A": 1, "B": 5, "C": 10, "D": 15, "E": 15, "F": 20, "M": 10,
               "N": 12, "R": 15, "S": 15, "T": 15, "U": 17, "V": 20, "G": 1}


def desgravacion_cafta(categoria, tasa_base, anio, anio_uno=CAFTA_ANIO_UNO):
    """
    Tasa preferencial CAFTA-DR para un año calendario.
    Las tasas de transición se redondean hacia abajo al décimo de punto
    porcentual (Anexo 3.3, párrafo 3).
    """
    cat = (categoria or "").strip()[:1].upper()
    n = anio - anio_uno + 1
    red = _reduccion_acumulada(cat, n)
    if red is None:
        return {"aplica": False, "categoria": cat, "anio_tratado": n,
                "detalle": "Sin preferencia arancelaria: se aplica el arancel de nación más favorecida."}
    tasa = tasa_base * (1 - red / 100)
    tasa = float(Decimal(str(tasa)).quantize(Decimal("0.1"), rounding=ROUND_FLOOR))
    libre = LIBRE_DESDE.get(cat)
    return {
        "aplica": True, "categoria": cat, "anio_tratado": n, "reduccion": round(red, 2),
        "tasa": max(0.0, tasa),
        "libre_desde": anio_uno + libre - 1 if libre else None,
    }


# --------------------------------------------------------------------------
# 3. Costo puesto en bodega
# --------------------------------------------------------------------------

def costo_bodega(exp, liq):
    tributos = liq["obligacion"] - (liq["iva"] if exp.get("credito_iva") else 0)
    locales = exp["honorarios"] + exp["almacenaje"] + exp["transporte_local"]
    total = liq["va"] + tributos + liq["otros"] + locales
    unidades = max(1, exp["unidades"])
    unitario = total / unidades
    return {
        "mercancia": liq["va"], "tributos": tributos, "otros": liq["otros"],
        "locales": locales, "total": total, "unitario": unitario,
        "precio": unitario * (1 + exp["margen"] / 100),
        "peso_tributos": tributos / total * 100 if total else 0,
    }
