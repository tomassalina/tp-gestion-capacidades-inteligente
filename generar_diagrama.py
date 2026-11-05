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

# Clases que son "como un enum" (constantes de clase, sin instancias): no
# tienen atributos de instancia que el AST pueda ver, asi que se listan a mano
CONSTANTES_DE_CLASE = {
    "TipoAccionBitacora": ["Propuesta", "Aprobacion", "Reversion"],
}

# Atributos cuyo valor sale de una clase de constantes (no es un Enum real de
# Python, la catedra no lo enseña asi; es "como un enum" por convencion propia)
ATRIBUTOS_PSEUDO_ENUM = {
    ("HabilidadDeTrabajador", "nivel"): "como un enum: Basico=1, Intermedio=2, Avanzado=3",
    ("HabilidadRequerida", "nivel_minimo"): "como un enum: Basico=1, Intermedio=2, Avanzado=3",
    ("Franja", "nombre"): "como un enum: Manana, Tarde, Noche",
    ("Asignacion", "estado"): "como un enum: Automatica, Pendiente, Aprobada",
}


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
        if (nombre, attr) in ATRIBUTOS_PSEUDO_ENUM:
            sufijo += f"  ({ATRIBUTOS_PSEUDO_ENUM[(nombre, attr)]})"
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


def punto_de_borde(caja, lado):
    x, y, w, h = caja
    puntos = {"r": (w, h / 2), "l": (0, h / 2), "b": (w / 2, h), "t": (w / 2, 0)}
    dx, dy = puntos[lado]
    return x + dx, y + dy


def flecha_entre(origen, destino, triangulo=False, lo="r", ld="l"):
    x1, y1 = punto_de_borde(cajas[origen], lo)
    x2, y2 = punto_de_borde(cajas[destino], ld)
    elementos.append(flecha(x1, y1, x2, y2, triangulo=triangulo))


def flecha_horizontal_a_altura_fija(origen, destino, y, triangulo=False):
    # para cajas vecinas en una misma fila con distinta altura: al conectarlas
    # por el centro vertical de cada una quedarian en diagonal, asi que se usa
    # una unica altura fija (relativa a esa fila) para los dos extremos.
    ox, oy, ow, oh = cajas[origen]
    dx, dy, dw, dh = cajas[destino]
    x1 = ox + ow if dx > ox else ox
    x2 = dx if dx > ox else dx + dw
    elementos.append(flecha(x1, oy + y, x2, dy + y, triangulo=triangulo))


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

# Columna 3: Habilidad, HabilidadDeTrabajador, HabilidadRequerida, Agenda
fin3 = apilar("Habilidad", COL3, None, ANCHO3, gap=0)
fin3 = apilar("HabilidadDeTrabajador", COL3, fin3, ANCHO3)
fin3 = apilar("HabilidadRequerida", COL3, fin3, ANCHO3)
fin3 = apilar("Agenda", COL3, fin3, ANCHO3)

# Columna 4: AreaDeTrabajo, Franja, Labor, TipoAccionBitacora
fin4 = apilar("AreaDeTrabajo", COL4, None, ANCHO4, gap=0)
fin4 = apilar("Franja", COL4, fin4, ANCHO4)
fin4 = apilar("Labor", COL4, fin4, ANCHO4)
fin4 = apilar("TipoAccionBitacora", COL4, fin4, ANCHO4)

fin = max(fin, fin3, fin4)

# ---------------------------------------------------------------------------
# Clases "secundarias" (Nodo, Cola, ListaEnlazada, RepositorioCSV): todas
# juntas, una fila horizontal debajo de todo. Cola y ListaEnlazada se alinean
# por x con Nodo (que usan ambas) y Agenda (que hereda de ListaEnlazada), para
# que esas flechas sigan siendo rectas.
# ---------------------------------------------------------------------------
y_sec = fin + 60
ANCHO_SEC = 320
x_lista = cajas["Agenda"][0] + (cajas["Agenda"][2] - ANCHO_SEC) / 2  # centrada bajo Agenda
x_nodo = x_lista - ANCHO_SEC - 40
x_cola = x_nodo - ANCHO_SEC - 40
x_repo = x_lista + ANCHO_SEC + 40

dibujar_clase("Cola", x_cola, y_sec, ANCHO_SEC)
dibujar_clase("Nodo", x_nodo, y_sec, ANCHO_SEC)
dibujar_clase("ListaEnlazada", x_lista, y_sec, ANCHO_SEC)
dibujar_clase("RepositorioCSV", x_repo, y_sec, ANCHO_SEC)
fin = max(cajas[n][1] + cajas[n][3] for n in ["Cola", "Nodo", "ListaEnlazada", "RepositorioCSV"])

# ---------------------------------------------------------------------------
# Flechas: solo entre cajas adyacentes de la misma columna, asi quedan
# verticales y cortas (sin cruzar el diagrama de punta a punta). El resto de
# las relaciones ya se ve en el tipo de cada atributo (ej: "franja: Franja").
# ---------------------------------------------------------------------------
flecha_entre("Supervisor", "Trabajador", triangulo=True, lo="t", ld="b")       # herencia
flecha_entre("Sistema", "Supervisor", lo="t", ld="b")                         # gestiona

flecha_entre("HabilidadDeTrabajador", "Habilidad", triangulo=True, lo="t", ld="b")
flecha_horizontal_a_altura_fija("Cola", "Nodo", 70, triangulo=True)           # usa (vecinas en la fila)
flecha_horizontal_a_altura_fija("ListaEnlazada", "Nodo", 70, triangulo=True)  # usa (vecinas en la fila)
flecha_entre("Agenda", "ListaEnlazada", triangulo=True, lo="b", ld="t")       # herencia (Agenda queda arriba)

flecha_entre("Franja", "AreaDeTrabajo", triangulo=True, lo="t", ld="b")       # tiene

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
