"""
ImportaCR · Sistema de gestión de importaciones para Costa Rica
Ejecutar con:  streamlit run app.py
"""
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import arancel
from casos import demostraciones, documentos_de, nuevo
from catalogo import (ETAPAS, FUENTES, NORMATIVA, PAISES, PUERTOS, RIESGOS,
                      TICA_URL, TIPOS)
from motor import calcular, colones, costo_bodega, desgravacion_cafta, pct

st.set_page_config(page_title="ImportaCR", layout="wide", initial_sidebar_state="expanded")

AZUL, MARINO, NARANJA, VERDE, GRIS = "#1f7fb5", "#10223a", "#ff7a1a", "#0a7d4f", "#9fb0c4"

st.markdown("""
<style>
.block-container{padding-top:1.6rem;max-width:1240px}
h1,h2,h3{letter-spacing:-.01em}
.cab{border-bottom:2px solid #10223a;padding-bottom:.6rem;margin-bottom:.4rem}
.cab h1{font-size:2.1rem;margin:0;line-height:1.15}
.cab p{margin:.2rem 0 .5rem;color:#4a5b70}
.chip{display:inline-block;font-size:.8rem;font-weight:600;padding:2px 10px;border-radius:999px;margin:0 6px 6px 0;background:#e6f2fa;color:#10223a;white-space:nowrap}
.chip.ok{background:#d5f2e3;color:#0a5a38}.chip.alerta{background:#ffe6d0;color:#8a3a00}.chip.demo{background:#10223a;color:#fff}
.fuente{font-size:.8rem;color:#5a6b80;margin:-.3rem 0 .8rem}
.total{font-size:2.3rem;font-weight:700;color:#ff7a1a;line-height:1.1;white-space:nowrap}
.etq{font-size:.85rem;color:#5a6b80}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.6rem;margin:.4rem 0 1rem}
.kpi{background:#f1f6fb;border-radius:8px;padding:.6rem .8rem}
.kpi .v{font-size:1.35rem;font-weight:700;color:#10223a;white-space:nowrap}
.kpi .v.ok{color:#0a7d4f}.kpi .v.mal{color:#a24a00}
.kpi .s{font-size:.78rem;color:#5a6b80}
table.t{width:100%;border-collapse:collapse;font-size:.9rem;margin:.2rem 0 .6rem}
table.t th{text-align:left;font-size:.78rem;color:#5a6b80;font-weight:600;border-bottom:1px solid #d8e3ee;padding:6px 8px}
table.t td{border-bottom:1px solid #e6edf3;padding:7px 8px;vertical-align:top}
table.t td.n,table.t th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
table.t td small{display:block;color:#5a6b80;font-size:.78rem}
table.t tr.sum td{font-weight:700;border-top:2px solid #10223a}
.nivel{display:inline-block;min-width:1.8rem;text-align:center;font-weight:700;border-radius:6px;padding:1px 6px;color:#10223a}
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ estado
if "expedientes" not in st.session_state:
    st.session_state.expedientes = demostraciones()
    st.session_state.activo = st.session_state.expedientes[0]["id"]

exps = st.session_state.expedientes


def activo():
    return next(e for e in exps if e["id"] == st.session_state.activo)


def campo(exp, clave, etiqueta, ruta=None, **kw):
    """Campo numérico ligado al expediente."""
    destino = exp if ruta is None else exp[ruta]
    k = f"{exp['id']}.{ruta or ''}.{clave}"
    destino[clave] = st.number_input(etiqueta, value=float(destino[clave]), key=k, **kw)
    return destino[clave]


def estado_tarifas(exp):
    v = exp["verificacion"]
    if v["fecha"]:
        quien = f" por {v['responsable']}" if v["responsable"] else ""
        return "ok", f"Verificado en el TICA el {v['fecha'].strftime('%d/%m/%Y')}{quien}"
    if exp["referencia_tarifas"]:
        return "ok", "Tarifas de referencia oficial"
    return "alerta", "Tarifas sin verificar"


def kpis(items):
    """items: (etiqueta, valor, nota, clase)"""
    html = "".join(f'<div class="kpi"><div class="s">{e}</div><div class="v {c}">{v}</div>'
                   f'{f"<div class=s>{n}</div>" if n else ""}</div>' for e, v, n, c in items)
    st.markdown(f'<div class="kpis">{html}</div>', unsafe_allow_html=True)


def tabla(cabecera, filas, numericas=(), suma=False):
    th = "".join(f'<th class="{"n" if i in numericas else ""}">{h}</th>' for i, h in enumerate(cabecera))
    trs = []
    for j, fila in enumerate(filas):
        cls = ' class="sum"' if suma and j == len(filas) - 1 else ""
        tds = "".join(f'<td class="{"n" if i in numericas else ""}">{v}</td>' for i, v in enumerate(fila))
        trs.append(f"<tr{cls}>{tds}</tr>")
    st.markdown(f'<table class="t"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>',
                unsafe_allow_html=True)


CORTO = {"pref": "Preferencial", "dai": "DAI", "sc": "Selectivo", "l6946": "Ley 6946", "inder": "INDER",
         "ifam": "IFAM", "esp": "Específico", "caldera": "Caldera", "otros": "Otros", "iva": "IVA"}


# ------------------------------------------------------------------ nuevo expediente
@st.dialog("Nuevo expediente de importación", width="large")
def dialogo_nuevo(inciso_inicial=""):
    with st.form("nuevo"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del producto", placeholder="Café tostado colombiano")
        tipo = c2.selectbox("Tipo de mercancía", list(TIPOS))
        origen = c1.selectbox("País de origen", list(PAISES))
        inciso = c2.text_input("Inciso arancelario", value=inciso_inicial,
                               help="Si no lo conoce, búsquelo en la pestaña Clasificación arancelaria.")
        puerto = c1.selectbox("Aduana de ingreso", list(PUERTOS))
        unidades = c2.number_input("Unidades a importar", min_value=1, value=1)
        enviado = st.form_submit_button("Crear expediente", type="primary")
    tratado = PAISES.get(origen)
    st.caption(f"Tratado aplicable: {tratado}." if tratado else f"{origen} no tiene tratado comercial vigente con Costa Rica: se aplica el DAI general.")
    if TIPOS[tipo].get("nota"):
        st.caption(TIPOS[tipo]["nota"])
    if enviado:
        exp = nuevo(nombre.strip() or "Expediente sin nombre", tipo, origen, inciso.strip(), puerto, unidades)
        fila = arancel.obtener(exp["inciso"])
        if fila and tratado == "CAFTA-DR":
            d = desgravacion_cafta(fila["categoria"], fila["base"], date.today().year)
            bloqueo = any(t == "bloquea" for t, _ in arancel.notas_cafta(fila["codigo"], origen))
            if d["aplica"] and not bloqueo:
                exp["tasas"]["pref"] = d["tasa"]
        exps.append(exp)
        st.session_state.activo = exp["id"]
        st.rerun()


# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    st.markdown("## ImportaCR")
    st.caption("Sistema de gestión de importaciones · Costa Rica")
    ids = [e["id"] for e in exps]
    st.session_state.activo = st.selectbox(
        "Expediente", ids, index=ids.index(st.session_state.activo),
        format_func=lambda i: next(e["nombre"] for e in exps if e["id"] == i))
    if st.button("Nuevo expediente", type="primary", use_container_width=True):
        dialogo_nuevo()
    exp = activo()
    st.divider()
    st.markdown("**Verificación de tarifas**")
    fecha = st.date_input("Fecha de verificación en el TICA", value=exp["verificacion"]["fecha"],
                          key=f"{exp['id']}.vf", format="DD/MM/YYYY")
    resp = st.text_input("Responsable", value=exp["verificacion"]["responsable"], key=f"{exp['id']}.vr")
    exp["verificacion"] = {"fecha": fecha, "responsable": resp}
    st.link_button("Abrir el arancel integrado (TICA)", TICA_URL, use_container_width=True)
    if not exp["demo"] and st.button("Eliminar expediente", use_container_width=True):
        exps.remove(exp)
        st.session_state.activo = exps[0]["id"]
        st.rerun()
    st.divider()
    st.caption("Prototipo desarrollado como propuesta de investigación del curso Procesos de Importaciones, "
               "Universidad San Marcos. No sustituye la declaración aduanera del agente aduanero.")

# ------------------------------------------------------------------ cabecera
exp = activo()
liq = calcular(exp)
nivel, texto_estado = estado_tarifas(exp)
chips = [f"Inciso {exp['inciso']}", f"Origen: {exp['origen']}",
         exp["tratado"] or "Sin tratado comercial", f"{exp['transporte']} · {exp['puerto']}"]
html_chips = "".join(f'<span class="chip">{c}</span>' for c in chips)
html_chips += f'<span class="chip {nivel}">{texto_estado}</span>'
if exp["demo"]:
    html_chips = '<span class="chip demo">Expediente de demostración</span>' + html_chips
st.markdown(f'<div class="cab"><h1>{exp["nombre"]}</h1><p>{exp["descripcion"]}</p>{html_chips}</div>',
            unsafe_allow_html=True)

tabs = st.tabs(["Liquidación", "Clasificación", "Logística", "Permisos", "Riesgos", "Costos",
                "Colaboración", "Fuentes"])

# ================================================================== 1. Liquidación
with tabs[0]:
    izq, der = st.columns([1, 1.25], gap="large")
    with izq:
        st.subheader("Valor aduanero")
        campo(exp, "fob", "Valor FOB (US$)", min_value=0.0, step=100.0)
        campo(exp, "flete", "Flete internacional (US$)", min_value=0.0, step=50.0)
        campo(exp, "seguro", "Seguro (US$)", min_value=0.0, step=10.0)
        campo(exp, "tc", "Tipo de cambio de venta (¢ por US$)", min_value=0.0, step=1.0,
              help="Tipo de cambio del BCCR a la fecha de aceptación del DUA.")

        st.subheader("Tarifas del inciso")
        c1, c2, c3 = st.columns(3)
        with c1:
            campo(exp, "dai", "DAI (%)", ruta="tasas", min_value=0.0, step=1.0)
            campo(exp, "inder", "INDER (%)", ruta="tasas", min_value=0.0, step=1.0)
        with c2:
            campo(exp, "sc", "Selectivo (%)", ruta="tasas", min_value=0.0, step=1.0)
            campo(exp, "ifam", "IFAM (%)", ruta="tasas", min_value=0.0, step=1.0)
        with c3:
            campo(exp, "l6946", "Ley 6946 (%)", ruta="tasas", min_value=0.0, step=1.0)
            campo(exp, "iva", "IVA (%)", ruta="tasas", min_value=0.0, step=1.0)
        if exp["referencia_tarifas"] and not exp["verificacion"]["fecha"]:
            st.markdown(f'<p class="fuente">Fuente: {exp["referencia_tarifas"]}.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="fuente">Fuente: arancel integrado del TICA · {texto_estado.lower()}.</p>',
                        unsafe_allow_html=True)

        if exp["tratado"]:
            exp["usa_pref"] = st.toggle(f"Aplicar trato preferencial ({exp['tratado']})", value=exp["usa_pref"],
                                        key=f"{exp['id']}.pref_on")
            campo(exp, "pref", "Tasa preferencial (%) · sustituye DAI y Ley 6946", ruta="tasas", min_value=0.0, step=0.5)
            fila = arancel.obtener(exp["inciso"])
            if exp["tratado"] == "CAFTA-DR" and fila:
                d = desgravacion_cafta(fila["categoria"], fila["base"], date.today().year)
                st.markdown(f'<p class="fuente">Fuente: Lista de Costa Rica, Anexo 3.3 del CAFTA-DR · categoría '
                            f'{d["categoria"]}, tasa {date.today().year}: {pct(d.get("tasa", 0), 1)}.</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="fuente">Fuente: lista de desgravación del tratado y arancel integrado del TICA.</p>',
                            unsafe_allow_html=True)
        else:
            exp["usa_pref"] = False

        if exp["alcohol"]:
            st.subheader("Impuesto específico")
            c1, c2 = st.columns(2)
            with c1:
                campo(exp, "cajas", "Cajas", ruta="alcohol", min_value=0.0, step=1.0)
                campo(exp, "ml", "Mililitros por unidad", ruta="alcohol", min_value=0.0, step=50.0)
            with c2:
                campo(exp, "por_caja", "Unidades por caja", ruta="alcohol", min_value=0.0, step=1.0)
                campo(exp, "grado", "Grado alcohólico (% vol.)", ruta="alcohol", min_value=0.0, step=1.0)
            campo(exp, "esp", "Tarifa (¢ por ml de alcohol absoluto)", ruta="tasas", min_value=0.0, step=0.1)

        st.subheader("Ingreso al país")
        c1, c2 = st.columns(2)
        puertos = list(PUERTOS)
        exp["puerto"] = c1.selectbox("Aduana de ingreso", puertos, index=puertos.index(exp["puerto"]),
                                     key=f"{exp['id']}.puerto")
        exp["transporte"] = PUERTOS[exp["puerto"]][0]
        with c2:
            campo(exp, "kilos", "Peso bruto (kg)", min_value=0.0, step=10.0)
        campo(exp, "otros_cargos", "Otros cargos de la declaración (¢)", min_value=0.0, step=100.0)

    liq = calcular(exp)
    with der:
        if liq["va"] <= 0:
            st.info("Ingrese el valor FOB, el flete, el seguro y el tipo de cambio para generar la liquidación.")
        else:
            st.markdown('<div class="etq">Obligación tributaria estimada</div>'
                        f'<div class="total">{colones(liq["obligacion"])}</div>'
                        f'<div class="etq">Equivale al {pct(liq["obligacion"] / liq["va"] * 100, 1)} del valor aduanero '
                        f'(US${liq["va_usd"]:,.2f} × {colones(liq["tc"])}).</div>', unsafe_allow_html=True)

            # Cascada: cada tributo se apila sobre el valor aduanero hasta llegar al total.
            nombres = ["Valor aduanero"] + [CORTO[k] for k, *_ in liq["lineas"]] + ["Total"]
            alturas, bases, colores, acumulado = [liq["va"]], [0], [GRIS], liq["va"]
            for *_, v in liq["lineas"]:
                alturas.append(v); bases.append(acumulado); colores.append(AZUL); acumulado += v
            alturas.append(acumulado); bases.append(0); colores.append(NARANJA)
            fig = go.Figure(go.Bar(x=nombres, y=alturas, base=bases, marker_color=colores,
                                   hovertemplate="%{x}: ¢%{y:,.2f}<extra></extra>"))
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, bargap=0.25,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              yaxis=dict(tickformat=",.0f", gridcolor="#e6edf3"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            filas = [(f"Valor aduanero en colones<small>US${liq['va_usd']:,.2f} × {colones(liq['tc'])}</small>", colones(liq["va"]))]
            filas += [(f"{n}<small>{f}</small>", colones(v)) for _, n, f, v in liq["lineas"]]
            filas += [("Total de tributos", colones(liq["obligacion"]))]
            tabla(["Concepto y base de cálculo", "Monto"], filas, numericas=(1,), suma=True)
            csv = pd.DataFrame([("Valor aduanero en colones", liq["va"])] + [(n, v) for _, n, _, v in liq["lineas"]] +
                               [("Total de tributos", liq["obligacion"])], columns=["Concepto", "Monto (CRC)"])
            st.caption(f"Base imponible del IVA: {colones(liq['base_iva'])}. Procedimiento del Instructivo de cálculo de la "
                       "obligación tributaria de la Dirección General de Aduanas (2023).")

            if exp["tratado"]:
                sin = calcular(exp, preferencial=False)["obligacion"]
                con = calcular(exp, preferencial=True)["obligacion"]
                st.markdown("##### Efecto del tratado comercial")
                kpis([("Sin trato preferencial", colones(sin), None, ""), ("Con trato preferencial", colones(con), None, ""),
                      ("Ahorro", colones(max(0, sin - con)), None, "ok" if sin > con else "")])
                if sin - con <= 0:
                    st.caption("Con la tasa preferencial registrada el tratado no reduce la carga tributaria.")
                st.caption("El trato preferencial exige una prueba de origen válida conforme a las reglas de origen del tratado.")

            st.download_button("Descargar liquidación (CSV)", csv.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"liquidacion_{exp['nombre'].replace(' ', '_')}.csv", mime="text/csv")

# ================================================================== 2. Clasificación
with tabs[1]:
    st.subheader("Buscador arancelario")
    st.caption("Busque por palabra, nombre comercial o código. Los resultados provienen de la Lista de Costa Rica del "
               "CAFTA-DR (Anexo 3.3); las tarifas vigentes se confirman en el arancel integrado del TICA.")
    consulta = st.text_input("Producto o código", placeholder="Ej.: whisky, maquillaje, 8422, café",
                             label_visibility="collapsed")
    resultados = arancel.buscar(consulta) if consulta else []
    if consulta and not resultados:
        st.warning("No se encontraron líneas. Pruebe con otra palabra o con los primeros dígitos del código.")
    if resultados:
        df = pd.DataFrame([{"Código SAC": arancel.formato_codigo(f["codigo"]), "Descripción": f["descripcion"],
                            "Capítulo": f'{f["capitulo"]:02d} · {f["capitulo_nombre"]}',
                            "Tasa base (%)": f["base"], "Categoría CAFTA-DR": f["categoria"]} for f in resultados])
        sel = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun",
                           selection_mode="single-row", height=min(420, 38 + 35 * len(df)))
        st.caption(f"{len(resultados)} resultados. Seleccione una fila para ver el detalle.")
        filas_sel = sel.selection.rows if sel and sel.selection else []
        if filas_sel:
            f = resultados[filas_sel[0]]
            st.markdown(f"#### {arancel.formato_codigo(f['codigo'])}")
            st.write(f["descripcion"])
            hermanas = [h for h in arancel.subpartida(f["codigo"]) if h["codigo"] != f["codigo"]]
            if hermanas:
                st.caption("Otras líneas de la misma subpartida: " +
                           " · ".join(f'{arancel.formato_codigo(h["codigo"])} {h["descripcion"]}' for h in hermanas[:6]))
            c1, c2 = st.columns([1.2, 1])
            with c1:
                anio = st.number_input("Año de importación", min_value=2006, max_value=2040,
                                       value=date.today().year, step=1)
                d = desgravacion_cafta(f["categoria"], f["base"], int(anio))
                if d["aplica"]:
                    kpis([(f"Tasa preferencial CAFTA-DR en {int(anio)}", pct(d["tasa"], 1), "Anexo 3.3, categoría " + d["categoria"], "")])
                    st.caption(f"Tasa base {pct(f['base'], 0)} · categoría {d['categoria']} · año {d['anio_tratado']} del Tratado · "
                               f"libre de arancel desde {d['libre_desde']}.")
                else:
                    st.info(d["detalle"])
                if len(f["categoria"]) > 1:
                    st.caption(f"Nota de la lista: {f['categoria']}.")
                for nivel_nota, nota in arancel.notas_cafta(f["codigo"], exp["origen"]):
                    (st.warning if nivel_nota == "bloquea" else st.info)(nota)
            with c2:
                st.code(f["codigo"], language=None)
                st.link_button("Verificar en el TICA", TICA_URL, use_container_width=True)
                if st.button("Crear expediente con este código", type="primary", use_container_width=True):
                    dialogo_nuevo(arancel.formato_codigo(f["codigo"]))
            st.caption("La tasa base corresponde al arancel de nación más favorecida vigente al 1 de enero de 2003; "
                       "no equivale al DAI actual.")

    st.divider()
    st.subheader("Ficha normativa del expediente")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Mercancía:** {exp['descripcion']}  \n**Inciso:** {exp['inciso']}  \n"
                    f"**Origen:** {exp['origen']}  \n**Tratado:** {exp['tratado'] or 'Sin tratado comercial'}  \n"
                    f"**Incoterm:** {exp['incoterm']}")
    with c2:
        t = exp["tasas"]
        vigentes = [("DAI", t["dai"]), ("Selectivo de consumo", t["sc"]), ("Ley 6946", t["l6946"]),
                    ("INDER", t["inder"]), ("IFAM", t["ifam"]), ("IVA", t["iva"])]
        st.markdown("**Tarifas aplicadas:** " + ", ".join(f"{n} {pct(v, 2)}" for n, v in vigentes if v) +
                    (f", específico {colones(t['esp'])} por ml" if exp["alcohol"] else ""))
        st.markdown(f'<span class="chip {nivel}">{texto_estado}</span>', unsafe_allow_html=True)
    st.markdown("**Obligaciones del importador:** autodeterminación de los tributos, declaración correcta del valor "
                "aduanero, transmisión del DUA por medio de un agente aduanero y cumplimiento de los requisitos no "
                "arancelarios antes del levante.")

# ================================================================== 3. Logística
with tabs[2]:
    total_dias = sum(exp["dias"])
    st.subheader(f"Ruta de la importación · {total_dias} días estimados")
    st.caption(f"Transporte {exp['transporte'].lower()} con ingreso por {exp['puerto']}. Las etapas siguen el flujo del "
               "despacho en el TICA; los plazos son estimaciones editables.")
    c1, c2 = st.columns([1, 1.6], gap="large")
    with c1:
        editado = st.data_editor(pd.DataFrame({"Etapa": ETAPAS, "Días": exp["dias"]}), hide_index=True,
                                 disabled=["Etapa"], use_container_width=True, key=f"{exp['id']}.dias",
                                 column_config={"Días": st.column_config.NumberColumn(min_value=0, step=1)})
        exp["dias"] = [int(x or 0) for x in editado["Días"]]
    with c2:
        inicio, barras = 0, []
        for etapa, dias in zip(ETAPAS, exp["dias"]):
            barras.append((etapa, inicio, dias))
            inicio += dias
        fig = go.Figure(go.Bar(y=[b[0] for b in barras][::-1], x=[b[2] for b in barras][::-1],
                               base=[b[1] for b in barras][::-1], orientation="h", marker_color=AZUL,
                               text=[f"{b[2]} d" for b in barras][::-1], textposition="outside"))
        fig.update_layout(height=380, margin=dict(l=10, r=30, t=10, b=10), xaxis_title="Días desde la cotización",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(gridcolor="#e6edf3"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if total_dias:
        mayor = ETAPAS[exp["dias"].index(max(exp["dias"]))]
        st.info(f"La etapa más larga es «{mayor.lower()}» ({max(exp['dias'])} días, "
                f"{max(exp['dias']) / total_dias:.0%} del total). Tramitar las notas técnicas en paralelo con la "
                "producción evita que el permiso detenga la mercancía en el depósito fiscal.")

# ================================================================== 4. Permisos
with tabs[3]:
    items = documentos_de(exp)
    listos = sum(1 for k, *_ in items if exp["checks"].get(k))
    st.subheader(f"Permisos y documentos · {listos} de {len(items)} completos")
    st.progress(listos / len(items))
    c1, c2 = st.columns(2, gap="large")
    for col, prefijo, titulo in ((c1, "p", "Requisitos no arancelarios"), (c2, "d", "Documentos del despacho")):
        with col:
            st.markdown(f"**{titulo}**")
            for k, nombre, detalle in items:
                if k.startswith(prefijo):
                    exp["checks"][k] = st.checkbox(f"{nombre}", value=exp["checks"].get(k, False),
                                                   key=f"{exp['id']}.{k}", help=detalle)
                    st.caption(detalle)
    st.caption("Las notas técnicas asociadas a cada inciso se consultan en el arancel integrado del TICA y se tramitan "
               "ante la institución rectora, en la mayoría de los casos por medio de la VUCE.")

# ================================================================== 5. Riesgos
with tabs[4]:
    st.subheader("Riesgos y mitigación")
    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        st.markdown("**Simulador cambiario**")
        var = st.slider("Variación del tipo de cambio (%)", -15, 15, 0, key=f"{exp['id']}.fx")
        if liq["va"] > 0:
            sim = calcular(exp, tipo_cambio=exp["tc"] * (1 + var / 100))
            dif = sim["obligacion"] - liq["obligacion"]
            kpis([("Tributos actuales", colones(liq["obligacion"]), f"Tipo de cambio {colones(exp['tc'])}", ""),
                  ("Tributos simulados", colones(sim["obligacion"]), f"Tipo de cambio {colones(sim['tc'])}", ""),
                  ("Diferencia", colones(dif), None, "mal" if dif > 0 else "ok")])
            st.caption("Todos los tributos parten del valor aduanero en colones, por lo que una variación cambiaria "
                       "se traslada casi en la misma proporción a la obligación tributaria y al costo de la mercancía.")
        z = [[sum(1 for r in RIESGOS if r[1] == p and r[2] == i) for i in (1, 2, 3)] for p in (1, 2, 3)]
        etiquetas = [[" ".join(f"R{k + 1}" for k, r in enumerate(RIESGOS) if r[1] == p and r[2] == i)
                      for i in (1, 2, 3)] for p in (1, 2, 3)]
        severidad = [[p * i for i in (1, 2, 3)] for p in (1, 2, 3)]
        fig = go.Figure(go.Heatmap(z=severidad, x=["Bajo", "Medio", "Alto"], y=["Baja", "Media", "Alta"],
                                   text=etiquetas, texttemplate="%{text}", showscale=False,
                                   colorscale=[[0, "#a7e3b9"], [0.45, "#ffd36b"], [1, "#ff9a5a"]], hoverinfo="skip"))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Impacto",
                          yaxis_title="Probabilidad", title="Matriz de probabilidad e impacto", title_font_size=14)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c2:
        color = lambda n: "#ff9a5a" if n >= 6 else "#ffd36b" if n >= 3 else "#a7e3b9"
        tabla(["Riesgo", "Nivel", "Mitigación"],
              [(f"<b>R{k + 1}</b> {r[0]}", f'<span class="nivel" style="background:{color(r[1] * r[2])}">{r[1] * r[2]}</span>', r[3])
               for k, r in enumerate(RIESGOS)])
        st.caption("Nivel = probabilidad × impacto, en escala de 1 a 9.")

# ================================================================== 6. Costo
with tabs[5]:
    st.subheader("Costo puesto en bodega y rentabilidad")
    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        campo(exp, "honorarios", "Honorarios del agente aduanero (¢)", min_value=0.0, step=5000.0)
        campo(exp, "almacenaje", "Almacenaje (¢)", min_value=0.0, step=5000.0)
        campo(exp, "transporte_local", "Transporte local (¢)", min_value=0.0, step=5000.0)
        exp["unidades"] = st.number_input("Unidades", min_value=1, value=int(exp["unidades"]), key=f"{exp['id']}.unid")
        campo(exp, "margen", "Margen de ganancia (%)", min_value=0.0, step=5.0)
        exp["credito_iva"] = st.toggle("El importador recupera el IVA como crédito fiscal", value=exp["credito_iva"],
                                       key=f"{exp['id']}.cred")
        st.caption("Si el IVA pagado en aduana se acredita, no forma parte del costo del producto, aunque sí afecta la "
                   "liquidez al momento de importar.")
    with c2:
        if liq["va"] > 0:
            c = costo_bodega(exp, liq)
            kpis([("Costo por unidad", colones(c["unitario"]), f"{exp['unidades']:,} unidades".replace(",", " "), ""),
                  ("Precio de venta sugerido", colones(c["precio"]), f"Margen {pct(exp['margen'], 0)}", ""),
                  ("Peso de los tributos", pct(c["peso_tributos"], 1), "sobre el costo total", "")])
            tabla(["Concepto", "Monto"], [
                ("Mercancía (valor aduanero)", colones(c["mercancia"])),
                ("Tributos" + (" sin IVA" if exp["credito_iva"] else ""), colones(c["tributos"])),
                ("Otros cargos", colones(c["otros"])),
                ("Agente, almacenaje y transporte local", colones(c["locales"])),
                ("Costo total puesto en bodega", colones(c["total"]))], numericas=(1,), suma=True)
            if exp["tratado"]:
                ahorro = max(0, calcular(exp, preferencial=False)["obligacion"] - calcular(exp, preferencial=True)["obligacion"])
                kpis([("Ahorro por aprovechar el tratado", colones(ahorro), "Tributos sin trato preferencial menos tributos con él", "ok" if ahorro else "")])
        else:
            st.info("Complete la liquidación para calcular el costo.")

# ================================================================== 7. Expediente compartido
with tabs[6]:
    st.subheader("Un expediente, todos los actores")
    st.caption("Propuesta de operación: importador, proveedor, transportista y agente aduanero trabajan sobre el mismo "
               "expediente, con los datos ingresados una sola vez.")
    roles = [("Importador", "Registra producto, valor e Incoterm; aprueba la liquidación y el costo final."),
             ("Proveedor", "Carga factura comercial, lista de empaque y prueba de origen."),
             ("Transportista", "Registra el embarque, el documento de transporte y la fecha de arribo."),
             ("Agente aduanero", "Valida inciso y valor; usa la liquidación como verificación previa del DUA; registra canal de aforo y levante.")]
    cols = st.columns(4)
    for col, (rol, tarea) in zip(cols, roles):
        with col:
            st.markdown(f"**{rol}**")
            st.write(tarea)
    st.markdown("##### Hoja de ruta de integración")
    tabla(["Función", "Versión actual", "Versión propuesta"], [
        ("Tarifas del inciso", "Registro manual con fecha de verificación", "Consulta automática del arancel integrado del TICA"),
        ("Tipo de cambio", "Registro manual", "Servicio web de indicadores económicos del BCCR"),
        ("Permisos", "Lista de control por tipo de mercancía", "Seguimiento del trámite en la VUCE"),
        ("Documentos", "Lista de control", "Repositorio compartido con control de versiones"),
        ("Desgravación arancelaria", "CAFTA-DR (Lista de Costa Rica)", "Todos los tratados vigentes")])

# ================================================================== 8. Fuentes
with tabs[7]:
    st.subheader("Fuentes y normativa")
    for tema, ref, url in FUENTES:
        st.markdown(f"**{tema}**  \n{ref} [{url}]({url})")
    st.markdown("##### Marco normativo")
    st.markdown("\n".join(f"- {n}" for n in NORMATIVA))
    st.markdown("##### Criterios de cálculo")
    st.markdown(
        "- El valor aduanero (CIF) se convierte a colones con el tipo de cambio de venta a la fecha de aceptación del DUA.\n"
        "- El DAI y la Ley 6946 se calculan sobre el valor aduanero; el selectivo de consumo suma el DAI a su base; "
        "el INDER y el IFAM acumulan los tributos anteriores; el IVA se calcula sobre el valor aduanero más todos los "
        "tributos y cargos.\n"
        "- El trato preferencial sustituye el DAI y la Ley 6946 por la tasa del tratado.\n"
        "- En el CAFTA-DR, el año uno es 2006 (Anexo 3.3, párrafos 4 y 5) y las tasas de transición se redondean hacia "
        "abajo al décimo de punto porcentual (párrafo 3).\n"
        "- La herramienta es de planificación y verificación: la declaración y la liquidación oficial corresponden al "
        "agente aduanero por medio del TICA.")
    st.caption("Validación: el motor reproduce los ejemplos oficiales del instructivo de la DGA (2023) para whisky "
               "(sección M) y ron con trato preferencial (sección N).")
