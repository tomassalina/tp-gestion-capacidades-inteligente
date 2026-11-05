import ast
import json

AZUL = "#1971c2"
NEGRO = "#1e1e1e"

ARCHIVOS = [
    "habilidad.py", "credencial_profesional.py", "franja.py", "nodo.py", "cola.py",
    "lista_enlazada.py", "agenda.py", "area_de_trabajo.py", "labor.py", "trabajador.py",
    "supervisor.py", "asignacion.py", "tipo_accion_bitacora.py", "sistema.py", "repositorio_csv.py",
]

# Atributos que son, ellos mismos, una estructura de datos de la materia (se pintan de azul)
ATRIBUTOS_ESTRUCTURA = {
    ("Trabajador", "repertorio_habilidades"): "set",
    ("Trabajador", "atributos"): "dict (**kwargs)",
    ("Trabajador", "agenda"): "Agenda (lista enlazada)",
    ("Sistema", "trabajadores_por_id"): "dict",
    ("Sistema", "solicitudes_pendientes"): "Cola",
    ("Sistema", "ocupacion"): "dict + tupla como clave",
    ("Sistema", "bitacora"): "list de tuplas",
    ("AreaDeTrabajo", "franjas_por_nombre"): "dict",
}
# Clases que SON una estructura de datos de punta a punta (toda la caja en azul)
CLASES_ESTRUCTURA = {"Nodo", "Cola", "ListaEnlazada", "Agenda"}


def targets_de_assign(stmt):
    objetivos = []
    for target in stmt.targets:
        elementos = target.elts if isinstance(target, (ast.Tuple, ast.List)) else [target]
        for el in elementos:
            if isinstance(el, ast.Attribute) and isinstance(el.value, ast.Name) and el.value.id == "self":
                objetivos.append(el.attr)
    return objetivos


def extraer_clases(archivo):
    with open(archivo) as f:
        arbol = ast.parse(f.read())
    clases = []
    for nodo in arbol.body:
        if not isinstance(nodo, ast.ClassDef):
            continue
        bases = [b.id for b in nodo.bases if isinstance(b, ast.Name)]
        atributos = []
        init = next((it for it in nodo.body if isinstance(it, ast.FunctionDef) and it.name == "__init__"), None)
        if init:
            for stmt in ast.walk(init):
                if isinstance(stmt, ast.Assign):
                    for attr in targets_de_assign(stmt):
                        if attr not in atributos:
                            atributos.append(attr)
        metodos = [it.name for it in nodo.body if isinstance(it, ast.FunctionDef) and it.name != "__init__"]
        clases.append({"nombre": nodo.name, "bases": bases, "atributos": atributos, "metodos": metodos})
    return clases


TODAS = {}
for archivo in ARCHIVOS:
    for c in extraer_clases(archivo):
        TODAS[c["nombre"]] = c

# Clases que van como caja completa en el diagrama (se omiten los simples contenedores de constantes/excepciones)
CLASES_A_DIBUJAR = [
    "Habilidad", "HabilidadDeTrabajador", "HabilidadRequerida", "CredencialProfesional", "Franja",
    "Nodo", "ListaEnlazada", "Cola", "Agenda",
    "AreaDeTrabajo", "Labor",
    "Trabajador", "Supervisor",
    "Asignacion", "TipoAccionBitacora",
    "Sistema", "RepositorioCSV",
]

_seed = [9000]


def next_seed():
    _seed[0] += 1
    return _seed[0]


def _base(tipo, x, y, width, height, **extra):
    s = next_seed()
    el = {
        "id": f"{tipo}-{s}", "type": tipo, "x": x, "y": y, "width": width, "height": height,
        "strokeColor": NEGRO, "strokeWidth": 2, "angle": 0,
        "backgroundColor": "transparent", "fillStyle": "solid", "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
        "isDeleted": False, "boundElements": None, "updated": 1, "link": None, "locked": False,
        "seed": s, "version": 1, "versionNonce": s + 1, "index": f"a{s}",
    }
    el.update(extra)
    return el


def rect(x, y, width, height, azul=False):
    el = _base("rectangle", x, y, width, height)
    if azul:
        el["strokeColor"] = AZUL
    return el


def texto(x, y, width, cadena, size=14, azul=False):
    el = _base("text", x, y, width, size + 6)
    el["strokeColor"] = AZUL if azul else NEGRO
    el["text"] = cadena
    el["fontSize"] = size
    el["fontFamily"] = 1
    el["textAlign"] = "left"
    el["verticalAlign"] = "top"
    el["containerId"] = None
    el["originalText"] = cadena
    el["lineHeight"] = 1.25
    el["baseline"] = size - 2
    return el


def flecha(x1, y1, x2, y2, triangulo=False, azul=False):
    el = _base("arrow", x1, y1, x2 - x1, y2 - y1)
    if azul:
        el["strokeColor"] = AZUL
    el["points"] = [[0, 0], [x2 - x1, y2 - y1]]
    el["lastCommittedPoint"] = None
    el["startBinding"] = None
    el["endBinding"] = None
    el["startArrowhead"] = None
    el["endArrowhead"] = "triangle_outline" if triangulo else "arrow"
    return el


elementos = []
cajas = {}
LINE_H = 18
PAD = 12
TITLE_H = 26
ANCHOS = {
    "Habilidad": 260, "HabilidadDeTrabajador": 280, "HabilidadRequerida": 280, "CredencialProfesional": 300,
    "Franja": 260, "Nodo": 260, "ListaEnlazada": 340, "Cola": 300, "Agenda": 340,
    "AreaDeTrabajo": 340, "Labor": 320, "Trabajador": 420, "Supervisor": 340,
    "Asignacion": 400, "TipoAccionBitacora": 300, "Sistema": 460, "RepositorioCSV": 400,
}


def dibujar_clase(nombre, x, y):
    c = TODAS[nombre]
    width = ANCHOS[nombre]
    caja_azul = nombre in CLASES_ESTRUCTURA
    titulo = nombre if not c["bases"] else f"{nombre}({', '.join(c['bases'])})"

    lineas = []
    for attr in c["atributos"]:
        es_azul = caja_azul or (nombre, attr) in ATRIBUTOS_ESTRUCTURA
        sufijo = f"  [{ATRIBUTOS_ESTRUCTURA[(nombre, attr)]}]" if (nombre, attr) in ATRIBUTOS_ESTRUCTURA else ""
        lineas.append((f"{attr}{sufijo}", es_azul))
    if c["atributos"] and c["metodos"]:
        lineas.append(("", False))
    for met in c["metodos"]:
        lineas.append((met + "()", caja_azul))

    altura = TITLE_H + PAD + max(len(lineas), 1) * LINE_H + PAD
    elementos.append(rect(x, y, width, altura, azul=caja_azul))
    elementos.append(texto(x + 10, y + 5, width - 20, titulo, size=18, azul=caja_azul))
    cy = y + TITLE_H + PAD
    for linea, es_azul in lineas:
        elementos.append(texto(x + 14, cy, width - 28, linea, size=12, azul=es_azul))
        cy += LINE_H
    cajas[nombre] = (x, y, width, altura)


# ---------------------------------------------------------------------------
# Layout: filas por tema, la Y de cada fila se calcula segun la altura real
# de la fila anterior (las cajas tienen alturas muy distintas: Trabajador y
# Sistema son enormes comparadas con Nodo o TipoAccionBitacora).
# ---------------------------------------------------------------------------
GAP_FILA = 60


def altura_de(nombre):
    return cajas[nombre][3]


y = 40
dibujar_clase("Nodo", 40, y)
dibujar_clase("ListaEnlazada", 340, y)
dibujar_clase("Cola", 740, y)
dibujar_clase("Agenda", 1100, y)
y += max(altura_de(n) for n in ["Nodo", "ListaEnlazada", "Cola", "Agenda"]) + GAP_FILA

dibujar_clase("Habilidad", 40, y)
dibujar_clase("HabilidadDeTrabajador", 340, y)
dibujar_clase("HabilidadRequerida", 660, y)
dibujar_clase("CredencialProfesional", 980, y)
dibujar_clase("Franja", 1320, y)
y += max(altura_de(n) for n in ["Habilidad", "HabilidadDeTrabajador", "HabilidadRequerida", "CredencialProfesional", "Franja"]) + GAP_FILA

dibujar_clase("AreaDeTrabajo", 40, y)
dibujar_clase("Labor", 420, y)
dibujar_clase("TipoAccionBitacora", 780, y)
y += max(altura_de(n) for n in ["AreaDeTrabajo", "Labor", "TipoAccionBitacora"]) + GAP_FILA

dibujar_clase("Trabajador", 40, y)
dibujar_clase("Supervisor", 520, y)
y += max(altura_de(n) for n in ["Trabajador", "Supervisor"]) + GAP_FILA

dibujar_clase("Asignacion", 40, y)
dibujar_clase("Sistema", 520, y)
dibujar_clase("RepositorioCSV", 1040, y)
y += max(altura_de(n) for n in ["Asignacion", "Sistema", "RepositorioCSV"]) + GAP_FILA
Y_REFERENCIA = y


def flecha_entre(origen, destino, triangulo=False, azul=False, lo="r", ld="l"):
    ox, oy, ow, oh = cajas[origen]
    dx, dy, dw, dh = cajas[destino]
    puntos = {"r": (ow, oh / 2), "l": (0, oh / 2), "b": (ow / 2, oh), "t": (ow / 2, 0)}
    puntos_d = {"r": (dw, dh / 2), "l": (0, dh / 2), "b": (dw / 2, dh), "t": (dw / 2, 0)}
    x1, y1 = ox + puntos[lo][0], oy + puntos[lo][1]
    x2, y2 = dx + puntos_d[ld][0], dy + puntos_d[ld][1]
    elementos.append(flecha(x1, y1, x2, y2, triangulo=triangulo, azul=azul))


flecha_entre("Supervisor", "Trabajador", triangulo=True, lo="t", ld="b")
flecha_entre("Agenda", "ListaEnlazada", triangulo=True, azul=True, lo="l", ld="r")
flecha_entre("Cola", "Nodo", azul=True, lo="l", ld="r")
flecha_entre("ListaEnlazada", "Nodo", azul=True, lo="l", ld="r")
flecha_entre("Trabajador", "Agenda", azul=True, lo="t", ld="b")
flecha_entre("Trabajador", "HabilidadDeTrabajador", lo="t", ld="b")
flecha_entre("Labor", "HabilidadRequerida", lo="t", ld="b")
flecha_entre("HabilidadDeTrabajador", "Habilidad", lo="l", ld="r")
flecha_entre("HabilidadRequerida", "Habilidad", lo="t", ld="r")
flecha_entre("Labor", "AreaDeTrabajo", lo="l", ld="r")
flecha_entre("AreaDeTrabajo", "Franja", lo="r", ld="t")
flecha_entre("Asignacion", "Trabajador", lo="t", ld="b")
flecha_entre("Asignacion", "Labor", lo="t", ld="b")
flecha_entre("Sistema", "Asignacion", lo="l", ld="r")
flecha_entre("Sistema", "Trabajador", lo="t", ld="b")
flecha_entre("Sistema", "RepositorioCSV", lo="r", ld="l")
flecha_entre("Sistema", "Cola", azul=True, lo="t", ld="b")

# Referencia de colores
rx, ry = 40, Y_REFERENCIA
elementos.append(rect(rx, ry, 340, 110))
elementos.append(texto(rx + 15, ry + 10, 310, "Referencia", size=17))
elementos.append(texto(rx + 15, ry + 40, 310, "Negro: POO comun (sin estructura", size=12))
elementos.append(texto(rx + 15, ry + 56, 310, "de datos especifica de la materia)", size=12))
elementos.append(texto(rx + 15, ry + 78, 310, "Azul: estructura de datos de la materia", size=12, azul=True))

diagrama = {
    "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
    "elements": elementos, "appState": {"gridSize": 20, "viewBackgroundColor": "#ffffff"}, "files": {},
}

with open("diagrama_clases_v4.excalidraw", "w") as f:
    json.dump(diagrama, f, indent=2)

print(f"Generado con {len(elementos)} elementos, {len(cajas)} clases")
for n in CLASES_A_DIBUJAR:
    c = TODAS[n]
    print(f"  {n}: {len(c['atributos'])} atributos, {len(c['metodos'])} metodos")
