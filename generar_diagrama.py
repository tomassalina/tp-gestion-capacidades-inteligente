import ast
import json

NEGRO = "#1e1e1e"

ARCHIVOS = [
    "habilidad.py", "credencial_profesional.py", "franja.py", "nodo.py", "cola.py",
    "lista_enlazada.py", "agenda.py", "area_de_trabajo.py", "labor.py", "trabajador.py",
    "supervisor.py", "asignacion.py", "tipo_accion_bitacora.py", "sistema.py", "repositorio_csv.py",
]

# Atributos que son, ellos mismos, una estructura de datos de la materia (se subrayan)
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
CLASES_ESTRUCTURA = {"Nodo", "Cola", "ListaEnlazada", "Agenda"}


def targets_de_assign(stmt):
    objetivos = []
    for target in stmt.targets:
        elementos_t = target.elts if isinstance(target, (ast.Tuple, ast.List)) else [target]
        for el in elementos_t:
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


def rect(x, y, width, height):
    return _base("rectangle", x, y, width, height)


def texto(x, y, width, cadena, size=14):
    el = _base("text", x, y, width, size + 6)
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


def linea(x1, y1, x2, y2, strokeWidth=1.3):
    el = _base("line", min(x1, x2), min(y1, y2), abs(x2 - x1) or 1, abs(y2 - y1) or 1)
    el["strokeWidth"] = strokeWidth
    el["points"] = [[x1 - el["x"], y1 - el["y"]], [x2 - el["x"], y2 - el["y"]]]
    el["lastCommittedPoint"] = None
    el["startBinding"] = None
    el["endBinding"] = None
    el["startArrowhead"] = None
    el["endArrowhead"] = None
    return el


def flecha(x1, y1, x2, y2, triangulo=False):
    el = _base("arrow", min(x1, x2), min(y1, y2), abs(x2 - x1) or 1, abs(y2 - y1) or 1)
    ox, oy = el["x"], el["y"]
    el["points"] = [[x1 - ox, y1 - oy], [x2 - ox, y2 - oy]]
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
ANCHO_CHAR = 6.6


def dibujar_clase(nombre, x, y, width):
    c = TODAS[nombre]
    caja_estructura = nombre in CLASES_ESTRUCTURA
    titulo = nombre if not c["bases"] else f"{nombre} (extiende {', '.join(c['bases'])})"

    lineas = []
    for attr in c["atributos"]:
        subrayar = caja_estructura or (nombre, attr) in ATRIBUTOS_ESTRUCTURA
        sufijo = f"  [{ATRIBUTOS_ESTRUCTURA[(nombre, attr)]}]" if (nombre, attr) in ATRIBUTOS_ESTRUCTURA else ""
        lineas.append((f"- {attr}{sufijo}", subrayar))
    if c["atributos"] and c["metodos"]:
        lineas.append(("", False))
    for met in c["metodos"]:
        lineas.append((f"+ {met}()", False))

    altura = TITLE_H + PAD + max(len(lineas), 1) * LINE_H + PAD
    elementos.append(rect(x, y, width, altura))
    elementos.append(texto(x + 10, y + 5, width - 20, titulo, size=17))
    cy = y + TITLE_H + PAD
    for contenido, subrayar in lineas:
        if contenido:
            elementos.append(texto(x + 14, cy, width - 28, contenido, size=12))
            if subrayar:
                ancho_aprox = min(len(contenido) * ANCHO_CHAR, width - 28)
                elementos.append(linea(x + 14, cy + 13.5, x + 14 + ancho_aprox, cy + 13.5))
        cy += LINE_H
    cajas[nombre] = (x, y, width, altura)
    return altura


def apilar(nombre, x, y_prev_fin, ancho, gap=50):
    y = y_prev_fin + gap if y_prev_fin is not None else 40
    altura = dibujar_clase(nombre, x, y, ancho)
    return y + altura


def flecha_entre(origen, destino, triangulo=False, label=None, lo="r", ld="l"):
    ox, oy, ow, oh = cajas[origen]
    dx, dy, dw, dh = cajas[destino]
    puntos = {"r": (ow, oh / 2), "l": (0, oh / 2), "b": (ow / 2, oh), "t": (ow / 2, 0)}
    x1, y1 = ox + puntos[lo][0], oy + puntos[lo][1]
    x2, y2 = dx + puntos[ld][0], dy + puntos[ld][1]
    elementos.append(flecha(x1, y1, x2, y2, triangulo=triangulo))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        elementos.append(texto(mx - len(label) * 3, my - 8, len(label) * 7 + 14, label, size=12))


# ---------------------------------------------------------------------------
# Layout por columnas, igual topologia que diagrama_clases_v3 (misma posicion
# relativa entre clases), pero con el contenido completo derivado del codigo
# y alturas calculadas (las cajas ahora son mas grandes que en la v3).
# ---------------------------------------------------------------------------
COL1, COL2, COL3, COL4 = 40, 540, 1080, 1620
ANCHO1, ANCHO2, ANCHO3, ANCHO4 = 420, 460, 400, 380

# Columna 1: CredencialProfesional, Asignacion
fin = apilar("CredencialProfesional", COL1, None, ANCHO1, gap=0)
fin = apilar("Asignacion", COL1, fin, ANCHO1)

# Columna 2: Trabajador, Supervisor, Sistema
fin = apilar("Trabajador", COL2, None, ANCHO2, gap=0)
fin = apilar("Supervisor", COL2, fin, ANCHO2)
fin = apilar("Sistema", COL2, fin, ANCHO2)

# Columna 3: Habilidad, HabilidadDeTrabajador, HabilidadRequerida, Nodo, ListaEnlazada, Cola, Agenda
fin = apilar("Habilidad", COL3, None, ANCHO3, gap=0)
fin = apilar("HabilidadDeTrabajador", COL3, fin, ANCHO3)
fin = apilar("HabilidadRequerida", COL3, fin, ANCHO3)
fin = apilar("Nodo", COL3, fin, ANCHO3)
fin = apilar("ListaEnlazada", COL3, fin, ANCHO3)
fin = apilar("Cola", COL3, fin, ANCHO3)
fin = apilar("Agenda", COL3, fin, ANCHO3)

# Columna 4: AreaDeTrabajo, Franja, Labor, TipoAccionBitacora, RepositorioCSV
fin = apilar("AreaDeTrabajo", COL4, None, ANCHO4, gap=0)
fin = apilar("Franja", COL4, fin, ANCHO4)
fin = apilar("Labor", COL4, fin, ANCHO4)
fin = apilar("TipoAccionBitacora", COL4, fin, ANCHO4)
fin = apilar("RepositorioCSV", COL4, fin, ANCHO4)

# ---------------------------------------------------------------------------
# Flechas: herencia (triangulo hueco) y relaciones de uso/composicion
# ---------------------------------------------------------------------------
flecha_entre("Supervisor", "Trabajador", triangulo=True, lo="t", ld="b")
flecha_entre("Agenda", "ListaEnlazada", triangulo=True, lo="t", ld="b")
flecha_entre("Cola", "Nodo", triangulo=True, label="usa", lo="t", ld="b")
flecha_entre("ListaEnlazada", "Nodo", triangulo=True, lo="r", ld="r")
flecha_entre("HabilidadDeTrabajador", "Habilidad", triangulo=True, label="usa", lo="t", ld="b")
flecha_entre("HabilidadRequerida", "HabilidadDeTrabajador", triangulo=True, lo="t", ld="b")
flecha_entre("Trabajador", "HabilidadDeTrabajador", label="tiene", lo="r", ld="l")
flecha_entre("Trabajador", "CredencialProfesional", label="posee", lo="l", ld="r")
flecha_entre("Trabajador", "Agenda", label="tiene", lo="r", ld="l")
flecha_entre("Labor", "HabilidadRequerida", label="requiere", lo="l", ld="r")
flecha_entre("Labor", "AreaDeTrabajo", label="en", lo="r", ld="l")
flecha_entre("AreaDeTrabajo", "Franja", triangulo=True, label="tiene", lo="b", ld="t")
flecha_entre("Asignacion", "Trabajador", label="trabajador", lo="r", ld="l")
flecha_entre("Asignacion", "Labor", label="labor", lo="r", ld="l")
flecha_entre("Asignacion", "Franja", label="franja", lo="r", ld="l")
flecha_entre("Sistema", "Supervisor", label="gestiona", lo="l", ld="r")
flecha_entre("Sistema", "Cola", label="usa", lo="r", ld="l")
flecha_entre("Sistema", "RepositorioCSV", label="persiste con", lo="r", ld="l")

# Referencia
rx, ry = COL1, fin + 60
elementos.append(rect(rx, ry, 360, 90))
elementos.append(texto(rx + 15, ry + 8, 330, "Referencia", size=16))
elementos.append(texto(rx + 15, ry + 36, 330, "Subrayado = estructura de datos de la materia", size=12))
elementos.append(linea(rx + 15, ry + 54, rx + 15 + 19 * ANCHO_CHAR, ry + 54))
elementos.append(texto(rx + 15 + 19 * ANCHO_CHAR + 10, ry + 36, 150, "(este texto, por ejemplo)", size=12))

diagrama = {
    "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
    "elements": elementos, "appState": {"gridSize": 20, "viewBackgroundColor": "#ffffff"}, "files": {},
}

with open("diagrama_clases_v4.excalidraw", "w") as f:
    json.dump(diagrama, f, indent=2)

print(f"Generado con {len(elementos)} elementos, {len(cajas)} clases")
