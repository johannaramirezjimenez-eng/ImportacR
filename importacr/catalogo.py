"""Catálogos de referencia de ImportaCR: mercancías, países, tratados, rutas, riesgos y fuentes."""

TICA_URL = "https://ticaconsultas.hacienda.go.cr/tica/hdbaranc.aspx"

# Requisitos no arancelarios por tipo de mercancía (lectura del curso, Módulo 3,
# "¿Qué permisos requiero y cómo los obtengo?").
TIPOS = {
    "Cosmético o producto de higiene": {
        "permisos": [("Registro sanitario o notificación del producto", "Ministerio de Salud · VUCE"),
                     ("Etiquetado en español", "Ministerio de Salud")]},
    "Bebida alcohólica": {
        "alcohol": True,
        "nota": "Suelen aplicar selectivo de consumo, INDER, IFAM e impuesto específico por mililitro de alcohol absoluto.",
        "permisos": [("Registro sanitario de bebida alcohólica", "Ministerio de Salud · VUCE"),
                     ("Etiquetado en español conforme al reglamento técnico centroamericano", "Ministerio de Salud")]},
    "Alimento o bebida no alcohólica": {
        "nota": "Las bebidas carbonatadas y los refrescos pueden pagar INDER e impuesto específico.",
        "permisos": [("Registro sanitario del alimento", "Ministerio de Salud · VUCE"),
                     ("Etiquetado nutricional y en español", "Ministerio de Salud")]},
    "Producto agrícola o vegetal": {
        "permisos": [("Registro como importador", "Ministerio de Agricultura y Ganadería"),
                     ("Permiso fitosanitario de importación", "Servicio Fitosanitario del Estado (SFE)")]},
    "Producto o subproducto de origen animal": {
        "permisos": [("Registro como importador", "Ministerio de Agricultura y Ganadería"),
                     ("Permiso zoosanitario de importación", "SENASA")]},
    "Medicamento o producto natural": {
        "permisos": [("Registro sanitario del medicamento o producto natural", "Ministerio de Salud · VUCE")]},
    "Equipo o material biomédico": {
        "permisos": [("Registro de equipo y material biomédico", "Ministerio de Salud · VUCE")]},
    "Químico, plaguicida o sustancia peligrosa": {
        "permisos": [("Registro del producto químico o plaguicida", "Ministerio de Salud o MAG, según el producto"),
                     ("Hoja de datos de seguridad", "Proveedor")]},
    "Maquinaria o equipo industrial": {
        "permisos": [("Notas técnicas asociadas al inciso", "Arancel integrado del TICA"),
                     ("Ficha técnica y manual del equipo", "Proveedor")]},
    "Electrónico o electrodoméstico": {
        "permisos": [("Notas técnicas asociadas al inciso", "Arancel integrado del TICA"),
                     ("Ficha técnica del equipo", "Proveedor")]},
    "Textil, ropa o calzado": {
        "permisos": [("Etiquetado de composición y origen", "Reglamento técnico aplicable"),
                     ("Notas técnicas asociadas al inciso", "Arancel integrado del TICA")]},
    "Otra mercancía": {
        "permisos": [("Notas técnicas asociadas al inciso", "Arancel integrado del TICA")]},
}

DOCUMENTOS = [
    ("Factura comercial", "Proveedor: mercancía, cantidades, valor e Incoterm."),
    ("Documento de transporte", "Conocimiento de embarque, guía aérea o carta de porte a nombre del importador."),
    ("Declaración del valor aduanero", "Importador, bajo juramento."),
    ("Declaración Única Aduanera (DUA)", "Agente aduanero, transmitida por el TICA."),
    ("Registro como importador", "Dirección General de Aduanas, cuando la importación es habitual."),
]

_UE = "Acuerdo de Asociación Centroamérica–Unión Europea"
_AELC = "TLC Centroamérica–AELC"
_MCCA = "Mercado Común Centroamericano"
_CAFTA = "CAFTA-DR"
_CARICOM = "TLC Costa Rica–CARICOM"
PAISES = {
    "Alemania": _UE, "Bélgica": _UE, "España": _UE, "Francia": _UE, "Irlanda": _UE,
    "Italia": _UE, "Países Bajos": _UE, "Portugal": _UE,
    "Reino Unido": "Acuerdo de Asociación Centroamérica–Reino Unido",
    "Suiza": _AELC, "Noruega": _AELC,
    "Estados Unidos": _CAFTA, "República Dominicana": _CAFTA,
    "México": "TLC Centroamérica–México", "Canadá": "TLC Costa Rica–Canadá",
    "Panamá": "TLC Centroamérica–Panamá",
    "Guatemala": _MCCA, "El Salvador": _MCCA, "Honduras": _MCCA, "Nicaragua": _MCCA,
    "Chile": "TLC Centroamérica–Chile", "Perú": "TLC Costa Rica–Perú",
    "Colombia": "TLC Costa Rica–Colombia", "China": "TLC Costa Rica–China",
    "Singapur": "TLC Costa Rica–Singapur", "Corea del Sur": "TLC Centroamérica–Corea",
    "Trinidad y Tobago": _CARICOM, "Jamaica": _CARICOM, "Barbados": _CARICOM,
    "Argentina": None, "Brasil": None, "India": None, "Japón": None,
    "Taiwán": None, "Turquía": None, "Vietnam": None, "Otro país": None,
}

# Puerto o aduana de ingreso: medio de transporte y días estimados por etapa.
PUERTOS = {
    "Moín (Limón)": ("Marítimo", [5, 15, 25, 1, 2, 3, 1, 1, 2]),
    "Caldera": ("Marítimo", [5, 15, 30, 1, 2, 3, 1, 1, 2]),
    "Juan Santamaría (aéreo)": ("Aéreo", [4, 10, 4, 1, 1, 3, 1, 1, 1]),
    "Peñas Blancas (terrestre)": ("Terrestre", [4, 10, 6, 1, 1, 3, 1, 1, 1]),
}

ETAPAS = [
    "Cotización y selección del proveedor",
    "Producción y alistamiento",
    "Transporte internacional",
    "Transmisión del manifiesto al TICA",
    "Traslado a depósito fiscal",
    "Notas técnicas de la institución rectora",
    "DUA y pago electrónico de tributos",
    "Validación y canal de aforo",
    "Levante, transporte local y entrega",
]

# (riesgo, probabilidad 1-3, impacto 1-3, mitigación)
RIESGOS = [
    ("Variación del tipo de cambio entre la compra y la aceptación del DUA", 3, 2,
     "Simular escenarios, adquirir divisas por adelantado o pactar el tipo de cambio con la entidad bancaria."),
    ("Error en la clasificación arancelaria o en el valor declarado", 2, 3,
     "Validar el inciso con el agente aduanero antes del embarque y conservar el respaldo documental del valor."),
    ("Rechazo o atraso de la nota técnica", 2, 3,
     "Iniciar el registro ante la institución rectora antes de la compra y revisar los requisitos en la VUCE."),
    ("Certificado de origen inválido y pérdida del trato preferencial", 2, 2,
     "Revisar con el proveedor las reglas de origen y el formato de certificación del tratado."),
    ("Asignación de canal rojo y revisión física", 2, 2,
     "Presentar documentación completa y consistente; prever días adicionales en el plan."),
    ("Cambios regulatorios o en tarifas e impuestos específicos", 1, 2,
     "Verificar las tarifas en el TICA en cada operación y registrar la fecha de verificación."),
    ("Atrasos navieros o congestión portuaria", 2, 2,
     "Mantener holgura en el calendario y comunicación temprana con el transportista."),
]

CAPITULOS = {
    1: "Animales vivos", 2: "Carne y despojos comestibles",
    3: "Pescados, crustáceos, moluscos y demás invertebrados acuáticos",
    4: "Leche y productos lácteos; huevos; miel natural", 5: "Los demás productos de origen animal",
    6: "Plantas vivas y productos de la floricultura", 7: "Hortalizas, plantas, raíces y tubérculos alimenticios",
    8: "Frutas y frutos comestibles", 9: "Café, té, yerba mate y especias", 10: "Cereales",
    11: "Productos de la molinería; malta; almidón", 12: "Semillas y frutos oleaginosos; plantas industriales o medicinales",
    13: "Gomas, resinas y demás jugos y extractos vegetales", 14: "Materias trenzables y demás productos vegetales",
    15: "Grasas y aceites animales o vegetales", 16: "Preparaciones de carne, pescado o crustáceos",
    17: "Azúcares y artículos de confitería", 18: "Cacao y sus preparaciones",
    19: "Preparaciones a base de cereales, harina, almidón o leche; pastelería",
    20: "Preparaciones de hortalizas, frutas u otros frutos", 21: "Preparaciones alimenticias diversas",
    22: "Bebidas, líquidos alcohólicos y vinagre", 23: "Residuos de la industria alimentaria; alimentos para animales",
    24: "Tabaco y sucedáneos del tabaco elaborados", 25: "Sal; azufre; tierras y piedras; yesos, cales y cementos",
    26: "Minerales metalíferos, escorias y cenizas", 27: "Combustibles minerales, aceites minerales y sus derivados",
    28: "Productos químicos inorgánicos", 29: "Productos químicos orgánicos", 30: "Productos farmacéuticos",
    31: "Abonos", 32: "Extractos curtientes o tintóreos; pinturas, barnices y tintas",
    33: "Aceites esenciales; perfumería, cosmética y tocador", 34: "Jabón, detergentes, ceras y velas",
    35: "Materias albuminoideas; colas; enzimas", 36: "Pólvoras y explosivos; fósforos; materias inflamables",
    37: "Productos fotográficos o cinematográficos", 38: "Productos diversos de las industrias químicas",
    39: "Plástico y sus manufacturas", 40: "Caucho y sus manufacturas", 41: "Pieles y cueros",
    42: "Manufacturas de cuero; artículos de viaje y bolsos", 43: "Peletería y sus confecciones",
    44: "Madera, carbón vegetal y manufacturas de madera", 45: "Corcho y sus manufacturas",
    46: "Manufacturas de espartería o cestería", 47: "Pasta de madera; papel o cartón para reciclar",
    48: "Papel y cartón y sus manufacturas", 49: "Productos editoriales y de las artes gráficas",
    50: "Seda", 51: "Lana y pelo fino u ordinario", 52: "Algodón", 53: "Las demás fibras textiles vegetales",
    54: "Filamentos sintéticos o artificiales", 55: "Fibras sintéticas o artificiales discontinuas",
    56: "Guata, fieltro y tela sin tejer; cordeles y cordajes", 57: "Alfombras y revestimientos textiles para el suelo",
    58: "Tejidos especiales; encajes; tapicería; bordados", 59: "Telas impregnadas o recubiertas; artículos técnicos textiles",
    60: "Tejidos de punto", 61: "Prendas y complementos de vestir, de punto",
    62: "Prendas y complementos de vestir, excepto los de punto", 63: "Los demás artículos textiles confeccionados",
    64: "Calzado y sus partes", 65: "Sombreros y demás tocados", 66: "Paraguas, bastones, látigos y fustas",
    67: "Plumas preparadas; flores artificiales; manufacturas de cabello",
    68: "Manufacturas de piedra, yeso, cemento, amianto o mica", 69: "Productos cerámicos",
    70: "Vidrio y sus manufacturas", 71: "Perlas, piedras y metales preciosos; bisutería; monedas",
    72: "Fundición, hierro y acero", 73: "Manufacturas de fundición, hierro o acero", 74: "Cobre y sus manufacturas",
    75: "Níquel y sus manufacturas", 76: "Aluminio y sus manufacturas", 77: "Reservado",
    78: "Plomo y sus manufacturas", 79: "Cinc y sus manufacturas", 80: "Estaño y sus manufacturas",
    81: "Los demás metales comunes; cermets", 82: "Herramientas, cuchillería y cubiertos de metal común",
    83: "Manufacturas diversas de metal común", 84: "Reactores nucleares, calderas, máquinas y aparatos mecánicos",
    85: "Máquinas, aparatos y material eléctrico; aparatos de sonido e imagen",
    86: "Vehículos y material para vías férreas", 87: "Vehículos automóviles, tractores, velocípedos y demás vehículos terrestres",
    88: "Aeronaves, vehículos espaciales y sus partes", 89: "Barcos y demás artefactos flotantes",
    90: "Instrumentos y aparatos de óptica, medida, control o médico-quirúrgicos", 91: "Aparatos de relojería",
    92: "Instrumentos musicales", 93: "Armas, municiones y sus partes",
    94: "Muebles; artículos de cama; aparatos de alumbrado; construcciones prefabricadas",
    95: "Juguetes, juegos y artículos de recreo o deporte", 96: "Manufacturas diversas",
    97: "Objetos de arte o colección y antigüedades",
}

# Términos de uso común que no aparecen en las descripciones del arancel.
# Cada término apunta a los códigos (o prefijos) del Sistema Armonizado donde se clasifica.
SINONIMOS = {
    "whisky": ["220830"], "ron": ["220840"], "ginebra": ["220850"], "vodka": ["220860"],
    "licor": ["2208"], "vino": ["2204"], "cerveza": ["2203"], "cafe": ["0901"], "chocolate": ["1806"],
    "perfume": ["3303"], "maquillaje": ["3304"], "cosmetico": ["3304"], "serum": ["330499"],
    "crema facial": ["330499"], "protector solar": ["330499"], "champu": ["330510"], "shampoo": ["330510"],
    "jabon": ["3401"], "pasta dental": ["330610"], "celular": ["851713"], "telefono": ["8517"],
    "smartphone": ["851713"], "laptop": ["847130"], "computadora": ["8471"], "tablet": ["847130"],
    "televisor": ["8528"], "refrigeradora": ["8418"], "lavadora": ["8450"], "audifonos": ["851830"],
    "impresora": ["8443"], "zapatos": ["64"], "calzado": ["64"], "tenis": ["6404"], "juguete": ["9503"],
    "bicicleta": ["8712"], "motocicleta": ["8711"], "carro": ["8703"], "automovil": ["8703"],
    "llanta": ["4011"], "medicamento": ["3004"], "suplemento": ["210690"], "envasadora": ["8422"],
    "empacadora": ["8422"], "muebles": ["9403"], "silla": ["9401"], "anteojos": ["9004"], "lentes": ["9004"],
    "arroz": ["1006"], "azucar": ["1701"], "leche": ["0401", "0402"], "queso": ["0406"],
    "comida para perros": ["230910"], "alimento para mascotas": ["230910"], "pollo": ["0207"],
    "aceite de oliva": ["1509"], "harina": ["1101"], "bolsas plasticas": ["3923"],
}

# Referencias formales (APA 7) que respaldan el sistema.
FUENTES = [
    ("Cálculo de la obligación tributaria",
     "Dirección General de Aduanas. (2023). *Instructivo cálculo para la obligación tributaria para la importación de mercancías* (MH-DGA-PRO09-INS-004, versión 01). Ministerio de Hacienda.",
     "https://www.hacienda.go.cr/docs/INSTRUCTIVO_CALCULO_OBLIGACION_TRIBUTARIA.pdf"),
    ("Lista arancelaria y categorías de desgravación",
     "Ministerio de Comercio Exterior. (s. f.). *Lista de Costa Rica. Anexo 3.3 del Tratado de Libre Comercio República Dominicana–Centroamérica–Estados Unidos*.",
     "https://comex.go.cr/media/9707/lista-de-costa-rica.pdf"),
    ("Notas generales de la Lista de Costa Rica",
     "Ministerio de Comercio Exterior. (s. f.). *Notas generales. Lista arancelaria de la República de Costa Rica* (Anexo 3.3).",
     "https://www.comex.go.cr/media/4094/00_notas-generales-lista-arancelaria-de-la-republica-de-costa-rica.pdf"),
    ("Tarifas vigentes y notas técnicas",
     "Ministerio de Hacienda. (s. f.). *Consulta del arancel integrado* [Sistema TICA].",
     TICA_URL),
]

NORMATIVA = [
    "Ley General de Aduanas (Ley 7557) y CAUCA / RECAUCA",
    "Ley de Fortalecimiento de las Finanzas Públicas (Ley 9635): Impuesto al Valor Agregado",
    "Ley 6946: impuesto del 1 % sobre el valor aduanero",
    "Tratado de Libre Comercio República Dominicana–Centroamérica–Estados Unidos (Ley 8622)",
    "Leyes aprobatorias de los demás tratados comerciales vigentes",
]
