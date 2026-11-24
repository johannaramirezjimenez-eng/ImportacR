"""Expedientes de demostración y creación de expedientes nuevos."""
import copy
import uuid

from catalogo import DOCUMENTOS, PAISES, PUERTOS, TIPOS


def _base(**kw):
    exp = {
        "id": uuid.uuid4().hex[:8], "demo": False, "tipo": "Otra mercancía",
        "incoterm": "FOB", "otros_cargos": 0.0, "kilos": 0.0, "alcohol": None,
        "credito_iva": False, "verificacion": {"fecha": None, "responsable": ""},
        "referencia_tarifas": None, "checks": {}, "unidades": 1, "margen": 30.0,
        "honorarios": 150000.0, "almacenaje": 50000.0, "transporte_local": 50000.0,
        "tasas": {"dai": 0.0, "sc": 0.0, "l6946": 1.0, "inder": 0.0, "ifam": 0.0, "iva": 13.0, "esp": 0.0, "pref": 0.0},
    }
    exp.update(kw)
    exp["tratado"] = PAISES.get(exp["origen"])
    exp["transporte"] = PUERTOS[exp["puerto"]][0]
    exp.setdefault("dias", list(PUERTOS[exp["puerto"]][1]))
    if "permisos" not in exp:
        exp["permisos"] = list(TIPOS[exp["tipo"]]["permisos"])
        if exp["tratado"]:
            exp["permisos"].append(("Certificado o declaración de origen", f"Exportador en {exp['origen']}"))
    return exp


def demostraciones():
    return [
        _base(
            demo=True, nombre="Whisky escocés", tipo="Bebida alcohólica",
            descripcion="Whisky 750 ml, 40 % vol., 100 cajas de 12 botellas",
            inciso="2208.30.90.00", origen="Reino Unido", puerto="Moín (Limón)",
            fob=2750.0, flete=200.0, seguro=50.0, tc=602.0, kilos=1300.0, usa_pref=False,
            tasas={"dai": 14.0, "sc": 10.0, "l6946": 1.0, "inder": 8.0, "ifam": 10.0, "iva": 13.0, "esp": 4.80, "pref": 15.0},
            alcohol={"cajas": 100, "por_caja": 12, "ml": 750, "grado": 40.0},
            referencia_tarifas="Instructivo de cálculo de la obligación tributaria, DGA (2023), sección M",
            dias=[5, 7, 18, 1, 2, 3, 1, 1, 2], unidades=1200, honorarios=180000.0,
            almacenaje=90000.0, transporte_local=60000.0, margen=35.0,
        ),
        _base(
            demo=True, nombre="Sérum facial coreano", tipo="Cosmético o producto de higiene",
            descripcion="Sérum facial hidratante de 50 ml, 2 000 unidades",
            inciso="3304.99.00.00", origen="Corea del Sur", puerto="Juan Santamaría (aéreo)",
            fob=9000.0, flete=1100.0, seguro=120.0, tc=510.0, kilos=260.0, usa_pref=True,
            tasas={"dai": 14.0, "sc": 0.0, "l6946": 1.0, "inder": 0.0, "ifam": 0.0, "iva": 13.0, "esp": 0.0, "pref": 0.0},
            dias=[4, 10, 4, 1, 1, 4, 1, 1, 1], unidades=2000, honorarios=150000.0,
            almacenaje=40000.0, transporte_local=35000.0, margen=60.0,
        ),
        _base(
            demo=True, nombre="Envasadora industrial", tipo="Maquinaria o equipo industrial",
            descripcion="Máquina envasadora automática, 1 unidad",
            inciso="8422.30.10.00.90", origen="China", puerto="Caldera",
            fob=38000.0, flete=3200.0, seguro=380.0, tc=510.0, kilos=2400.0, usa_pref=True,
            dias=[7, 30, 32, 1, 2, 1, 1, 1, 3], unidades=1, honorarios=220000.0,
            almacenaje=120000.0, transporte_local=180000.0, margen=0.0,
        ),
    ]


def nuevo(nombre, tipo, origen, inciso, puerto, unidades):
    alcohol = {"cajas": 1, "por_caja": 12, "ml": 750, "grado": 40.0} if TIPOS[tipo].get("alcohol") else None
    exp = _base(nombre=nombre, tipo=tipo, descripcion=f"{tipo} originario de {origen}", inciso=inciso or "Por clasificar",
                origen=origen, puerto=puerto, fob=0.0, flete=0.0, seguro=0.0, tc=510.0,
                usa_pref=bool(PAISES.get(origen)), alcohol=alcohol, unidades=max(1, int(unidades)))
    if alcohol:
        exp["tasas"]["esp"] = 4.80
    return exp


def documentos_de(exp):
    return [(f"p{i}", n, d) for i, (n, d) in enumerate(exp["permisos"])] + \
           [(f"d{i}", n, d) for i, (n, d) in enumerate(DOCUMENTOS)]


def duplicar(exp):
    return copy.deepcopy(exp)
