"""Búsqueda en la Lista de Costa Rica del CAFTA-DR y reglas especiales de sus Notas Generales."""
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

from catalogo import CAPITULOS, SINONIMOS

DATA = Path(__file__).parent / "data" / "cafta_cr.json"


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def formato_codigo(c):
    c = "".join(ch for ch in str(c) if ch.isdigit())
    return f"{c[0:4]}.{c[4:6]}.{c[6:8]}.{c[8:10]}" if len(c) >= 10 else c


@lru_cache(maxsize=1)
def lista():
    filas = []
    for codigo, desc, base, cat in json.load(open(DATA, encoding="utf-8")):
        cap = int(codigo[:2])
        filas.append({
            "codigo": codigo,
            "descripcion": desc.lstrip("- ").strip() or "Sin descripción en la lista",
            "base": base,
            "categoria": cat,
            "capitulo": cap,
            "capitulo_nombre": CAPITULOS.get(cap, ""),
            "_busqueda": normalizar(f"{desc} {CAPITULOS.get(cap, '')}"),
        })
    return filas


def buscar(consulta, limite=60):
    q = normalizar(consulta).strip()
    if not q:
        return []
    filas = lista()
    digitos = "".join(ch for ch in q if ch.isdigit())
    if digitos and len(digitos) >= 2 and not any(ch.isalpha() for ch in q):
        return [f for f in filas if f["codigo"].startswith(digitos)][:limite]

    prefijos = []
    for termino, codigos in SINONIMOS.items():
        if termino in q:
            prefijos += codigos
    por_sinonimo = [f for f in filas if any(f["codigo"].startswith(p) for p in prefijos)]

    palabras = [p for p in q.split() if len(p) >= 3]
    por_texto = []
    if palabras:
        por_texto = [f for f in filas if all(p in f["_busqueda"] for p in palabras)
                     and f not in por_sinonimo]
    return (por_sinonimo + por_texto)[:limite]


def subpartida(codigo):
    """Líneas hermanas de la misma subpartida, para dar contexto a descripciones como 'Otros'."""
    return [f for f in lista() if f["codigo"][:6] == codigo[:6]]


def obtener(codigo):
    c = "".join(ch for ch in str(codigo) if ch.isdigit())[:10]
    for f in lista():
        if f["codigo"] == c:
            return f
    candidatos = [f for f in lista() if f["codigo"].startswith(c[:6])] if len(c) >= 6 else []
    return candidatos[0] if len(candidatos) == 1 else None


# Notas Generales de la Lista de Costa Rica (Anexo 3.3)
_SOLO_EEUU = ("1701", "090111", "090112", "090121", "090122")
_EXCLUIDOS_RD = ("070310", "071331", "071332", "071333", "100610", "100620", "100630", "100640",
                 "2203", "2207", "2208", "240120", "240220", "240310")
_CONTINGENTES = {
    ("020311", "020312", "020319", "020321", "020322", "020329"): "carne de cerdo",
    ("02071399", "02071499"): "muslos y piernas de pollo",
    ("040210", "040221", "040229"): "leche en polvo",
    ("040510", "040520"): "mantequilla",
    ("040610", "04062090", "040630", "04069010", "04069020", "04069090"): "queso",
    ("210500",): "helados",
    ("04029990", "22029090"): "otros productos lácteos",
    ("10061090",): "arroz en granza",
    ("100620", "1006301", "100630", "100640"): "arroz pilado",
    ("070190",): "papa fresca",
    ("0703101",): "cebolla fresca",
    ("200410",): "papa prefrita congelada",
}


def notas_cafta(codigo, pais):
    notas = []
    if codigo.startswith(_SOLO_EEUU):
        txt = "Los compromisos arancelarios aplican únicamente a mercancías originarias de Estados Unidos (Nota General 6)."
        notas.append(("bloquea" if pais == "República Dominicana" else "info", txt))
    if codigo.startswith(_EXCLUIDOS_RD) and pais == "República Dominicana":
        notas.append(("bloquea", "La preferencia no aplica a esta mercancía cuando se importa directamente desde República Dominicana (Nota General 7)."))
    for prefijos, producto in _CONTINGENTES.items():
        if codigo.startswith(prefijos):
            notas.append(("info", f"Sujeto a contingente arancelario de {producto}: la tasa preferencial aplica dentro de la cuota asignada por COMEX (Apéndices I y II)."))
    return notas
