import ast
import json

NEGRO = "#1e1e1e"

ARCHIVOS = [
    "habilidad.py", "credencial_profesional.py", "franja.py", "nodo.py", "cola.py",
    "lista_enlazada.py", "agenda.py", "area_de_trabajo.py", "labor.py", "trabajador.py",
    "supervisor.py", "asignacion.py", "tipo_accion_bitacora.py", "sistema.py", "repositorio_csv.py",
]

# Atributos que son, ellos mismos, una estructura de datos de la materia (se subrayan)
# (el tipo real de cada uno ya se ve en TIPOS; aca solo se marca cuales
# subrayar por ser, ellos mismos, una estructura de datos de la materia)
ATRIBUTOS_ESTRUCTURA = {
    ("Trabajador", "repertorio_habilidades"),
    ("Trabajador", "atributos"),
    ("Trabajador", "agenda"),
    ("Sistema", "trabajadores_por_id"),
    ("Sistema", "solicitudes_pendientes"),
    ("Sistema", "ocupacion"),
    ("Sistema", "bitacora"),
    ("AreaDeTrabajo", "franjas_por_nombre"),
}
CLASES_ESTRUCTURA = {"Nodo", "Cola", "ListaEnlazada", "Agenda"}

# Tipo de cada atributo (la catedra no usa type hints en el codigo, pero el
# diagrama si los muestra para que se entienda de un vistazo). Para los que
# salen de una clase "como un enum" (constantes de clase, no un Enum real de
# Python), el tipo es el nombre de esa clase + sus valores posibles.
TIPOS = {
    ("Habilidad", "nombre"): "str",
    ("HabilidadDeTrabajador", "habilidad"): "Habilidad",
    ("HabilidadDeTrabajador", "nivel"): "NivelHabilidad (Basico=1, Intermedio=2, Avanzado=3)",
    ("HabilidadRequerida", "habilidad"): "Habilidad",
    ("HabilidadRequerida", "nivel_minimo"): "NivelHabilidad (Basico=1, Intermedio=2, Avanzado=3)",
    ("CredencialProfesional", "nombre"): "str",
    ("CredencialProfesional", "fecha_obtencion"): "date",
    ("CredencialProfesional", "fecha_caducidad"): "date",
    ("Franja", "nombre"): "TipoFranja (Manana, Tarde, Noche)",
    ("Franja", "capacidad"): "int",
    ("Nodo", "dato"): "object",
    ("Nodo", "siguiente"): "Nodo",
    ("ListaEnlazada", "inicio"): "Nodo",
    ("Cola", "inicio"): "Nodo",
    ("Cola", "fin"): "Nodo",
    ("Cola", "cantidad"): "int",
    ("AreaDeTrabajo", "nombre"): "str",
    ("AreaDeTrabajo", "credenciales_obligatorias"): "str[]",
    ("AreaDeTrabajo", "franjas"): "Franja[]",
    ("AreaDeTrabajo", "franjas_por_nombre"): "dict[str, Franja]",
    ("Labor", "id"): "int",
    ("Labor", "titulo"): "str",
    ("Labor", "descripcion"): "str",
    ("Labor", "duracion_horas"): "int",
    ("Labor", "habilidades_requeridas"): "HabilidadRequerida[]",
    ("Labor", "credenciales_requeridas"): "str[]",
    ("Labor", "area"): "AreaDeTrabajo",
    ("Trabajador", "id"): "int",
    ("Trabajador", "nombre"): "str",
    ("Trabajador", "habilidades"): "HabilidadDeTrabajador[]",
    ("Trabajador", "repertorio_habilidades"): "set[str]",
    ("Trabajador", "credenciales"): "CredencialProfesional[]",
    ("Trabajador", "horas_maximas_semana"): "int",
    ("Trabajador", "horas_asignadas"): "int",
    ("Trabajador", "atributos"): "dict  (**kwargs)",
    ("Trabajador", "agenda"): "Agenda",
    ("Asignacion", "trabajador"): "Trabajador",
    ("Asignacion", "labor"): "Labor",
    ("Asignacion", "franja"): "Franja",
    ("Asignacion", "fecha"): "date",
    ("Asignacion", "estado"): "EstadoAsignacion (Automatica, Pendiente, Aprobada)",
    ("Sistema", "trabajadores"): "Trabajador[]",
    ("Sistema", "areas"): "AreaDeTrabajo[]",
    ("Sistema", "labores"): "Labor[]",
    ("Sistema", "solicitudes_pendientes"): "Cola",
    ("Sistema", "asignaciones"): "Asignacion[]",
    ("Sistema", "trabajadores_por_id"): "dict[int, Trabajador]",
    ("Sistema", "ocupacion"): "dict[tupla, int]",
    ("Sistema", "bitacora"): "list[tupla(fecha, TipoAccionBitacora, Labor, Trabajador)]",
    ("RepositorioCSV", "ruta_archivo"): "str",
    ("RepositorioCSV", "columnas"): "list[str]",
}


# Tipo de cada parametro de los metodos "principales" (ni accesor ni
# persistencia). Igual que con TIPOS: la catedra no usa type hints, esto es
# solo para que el diagrama se entienda de un vistazo.
TIPOS_PARAMETRO = {
    "other": "object", "nivel_minimo": "NivelHabilidad", "fecha_referencia": "date",
    "credencial": "str", "franja": "Franja", "nombre_franja": "str",
    "habilidad_de_trabajador": "HabilidadDeTrabajador", "otro_trabajador": "Trabajador",
    "clave": "str", "valor_por_defecto": "object", "habilidades_requeridas": "HabilidadRequerida[]",
    "credenciales_requeridas": "str[]", "fecha": "date", "horas_a_sumar": "int", "horas": "int",
    "asignacion": "Asignacion", "sistema": "Sistema", "labor": "Labor",
    "nuevo_trabajador": "Trabajador", "area": "AreaDeTrabajo", "trabajador": "Trabajador",
    "asignaciones_existentes": "Asignacion[]", "id": "int", "fecha_obtencion": "date",
    "fecha_caducidad": "date", "tipo_accion": "TipoAccionBitacora (Propuesta, Aprobacion, Reversion)", "nombre": "str",
    "horas_max": "int", "**atributos": "", "nombre_requerido": "str",
    "dato": "object", "valor": "object", "nodo_actual": "Nodo", "filas": "list[dict]",
}


def tipo_de_parametro(nombre_parametro):
    if nombre_parametro.startswith("**"):
        return nombre_parametro + " (kwargs opcionales)"
    return f"{nombre_parametro}: {TIPOS_PARAMETRO.get(nombre_parametro, '?')}"


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
        parametros = {}
        for it in nodo.body:
            if isinstance(it, ast.FunctionDef) and it.name != "__init__":
                nombres = [a.arg for a in it.args.args if a.arg != "self"]
                if it.args.kwarg:
                    nombres.append(f"**{it.args.kwarg.arg}")
                parametros[it.name] = nombres
        clases.append({"nombre": nodo.name, "bases": bases, "atributos": atributos, "metodos": metodos, "parametros": parametros})
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


def es_accesor(met, atributos):
    return any(met in (f"get_{attr}", f"set_{attr}") for attr in atributos)


def es_persistencia(met):
    if met.startswith("guardar") or met.startswith("cargar_"):
        return True
    return "desde_texto" in met or "desde_fila" in met or "a_texto" in met


def dibujar_clase(nombre, x, y, width):
    c = TODAS[nombre]
    caja_estructura = nombre in CLASES_ESTRUCTURA
    titulo = nombre if not c["bases"] else f"{nombre} (extiende {', '.join(c['bases'])})"

    lineas = []
    for attr in c["atributos"]:
        subrayar = caja_estructura or (nombre, attr) in ATRIBUTOS_ESTRUCTURA
        tipo = TIPOS.get((nombre, attr), "?")
        lineas.append((f"- {attr}: {tipo}", subrayar))

    # metodos agrupados (conservando el orden original dentro de cada grupo):
    # 1) accesores get_/set_, 2) logica de negocio, 3) persistencia (CSV)
    accesores = [m for m in c["metodos"] if es_accesor(m, c["atributos"])]
    persistencia = [m for m in c["metodos"] if not es_accesor(m, c["atributos"]) and es_persistencia(m)]
    negocio = [m for m in c["metodos"] if m not in accesores and m not in persistencia]

    grupos = [g for g in [accesores, negocio, persistencia] if g]
    if c["atributos"] and grupos:
        lineas.append(("", False))
    presupuesto_chars = (width - 28) / ANCHO_CHAR
    for i, grupo in enumerate(grupos):
        if i > 0:
            lineas.append(("", False))
        for met in grupo:
            if grupo is not negocio:
                lineas.append((f"+ {met}()", False))
                continue
            partes = [tipo_de_parametro(p) for p in c["parametros"].get(met, [])]
            if not partes:
                lineas.append((f"+ {met}()", False))
            elif len(f"+ {met}({', '.join(partes)})") <= presupuesto_chars:
                lineas.append((f"+ {met}({', '.join(partes)})", False))
            else:
                lineas.append((f"+ {met}(", False))
                for parte in partes:
                    lineas.append((f"    {parte},", False))
                lineas.append((")", False))

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


def flecha_horizontal_entre_columnas(origen, destino, y_absoluto, triangulo=False):
    # conecta dos cajas de columnas distintas a una altura fija en comun, asi
    # queda perfectamente horizontal aunque las dos cajas tengan alturas y
    # posiciones verticales totalmente distintas
    ox, oy, ow, oh = cajas[origen]
    dx, dy, dw, dh = cajas[destino]
    x1 = ox + ow if dx > ox else ox
    x2 = dx if dx > ox else dx + dw
    elementos.append(flecha(x1, y_absoluto, x2, y_absoluto, triangulo=triangulo))


def flecha_elbow(puntos, triangulo=False):
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    el = _base("arrow", min(xs), min(ys), (max(xs) - min(xs)) or 1, (max(ys) - min(ys)) or 1)
    ox, oy = el["x"], el["y"]
    el["points"] = [[px - ox, py - oy] for px, py in puntos]
    el["lastCommittedPoint"] = None
    el["startBinding"] = None
    el["endBinding"] = None
    el["startArrowhead"] = None
    el["endArrowhead"] = "triangle_outline" if triangulo else "arrow"
    el["elbowed"] = True
    el["roundness"] = {"type": 2}
    return el


def flecha_salteando(origen_abajo, destino_arriba, lado="r", triangulo=False):
    # conecta dos cajas de la MISMA columna que no son vecinas directas: en
    # vez de pegarse al borde, hace un "elbow" bien ancho hacia afuera para
    # rodear la caja que queda en el medio sin tocarla
    ox, oy, ow, oh = cajas[origen_abajo]
    dx, dy, dw, dh = cajas[destino_arriba]
    x = ox + ow if lado == "r" else ox
    bulto = x + 90 if lado == "r" else x - 90
    elementos.append(flecha_elbow(
        [(x, oy), (bulto, oy), (bulto, dy + dh), (x, dy + dh)],
        triangulo=triangulo,
    ))


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

# Columna 4: AreaDeTrabajo, Franja, Labor
fin4 = apilar("AreaDeTrabajo", COL4, None, ANCHO4, gap=0)
fin4 = apilar("Franja", COL4, fin4, ANCHO4)
fin4 = apilar("Labor", COL4, fin4, ANCHO4)

fin = max(fin, fin3, fin4)

# ---------------------------------------------------------------------------
# Clases "secundarias" (Nodo, Cola, ListaEnlazada, RepositorioCSV): todas
# juntas, una fila horizontal debajo de todo. Cola queda centrada bajo Sistema
# (que la usa) y ListaEnlazada centrada bajo Agenda (que hereda de ella), asi
# esas dos flechas verticales quedan rectas; Nodo pegado a Cola (horizontal).
# ---------------------------------------------------------------------------
y_sec = fin + 60
ANCHO_SEC = 320
x_cola = cajas["Sistema"][0] + (cajas["Sistema"][2] - ANCHO_SEC) / 2    # centrada bajo Sistema
x_nodo = x_cola - ANCHO_SEC - 40
x_lista = cajas["Agenda"][0] + (cajas["Agenda"][2] - ANCHO_SEC) / 2     # centrada bajo Agenda
x_repo = x_lista + ANCHO_SEC + 40

dibujar_clase("Nodo", x_nodo, y_sec, ANCHO_SEC)
dibujar_clase("Cola", x_cola, y_sec, ANCHO_SEC)
dibujar_clase("ListaEnlazada", x_lista, y_sec, ANCHO_SEC)
dibujar_clase("RepositorioCSV", x_repo, y_sec, ANCHO_SEC)
fin = max(cajas[n][1] + cajas[n][3] for n in ["Cola", "Nodo", "ListaEnlazada", "RepositorioCSV"])

# ---------------------------------------------------------------------------
# Flechas: entre cajas adyacentes (mismo lugar o misma fila/columna), para que
# queden derechas y cortas. Las relaciones de "tiene un" que no se pueden
# dibujar derechas ya se ven en el tipo de cada atributo (ej: "franja: Franja").
# ---------------------------------------------------------------------------
flecha_entre("Supervisor", "Trabajador", triangulo=True, lo="t", ld="b")       # herencia
flecha_entre("Sistema", "Supervisor", lo="t", ld="b")                         # gestiona
flecha_entre("Sistema", "Cola", lo="b", ld="t")                               # tiene (solicitudes_pendientes)

flecha_entre("HabilidadDeTrabajador", "Habilidad", triangulo=True, lo="t", ld="b")
flecha_salteando("HabilidadRequerida", "Habilidad", lado="r")                 # salta HabilidadDeTrabajador
flecha_horizontal_a_altura_fija("Cola", "Nodo", 70, triangulo=True)           # usa (vecinas en la fila)
flecha_entre("Agenda", "ListaEnlazada", triangulo=True, lo="b", ld="t")       # herencia (Agenda queda arriba)

flecha_horizontal_entre_columnas("Trabajador", "Agenda", punto_de_borde(cajas["Agenda"], "l")[1])  # tiene
flecha_horizontal_entre_columnas("CredencialProfesional", "Trabajador", punto_de_borde(cajas["CredencialProfesional"], "r")[1])  # posee
flecha_horizontal_entre_columnas("Asignacion", "Trabajador", punto_de_borde(cajas["Asignacion"], "r")[1])  # trabajador

flecha_entre("Franja", "AreaDeTrabajo", triangulo=True, lo="t", ld="b")       # tiene
flecha_salteando("Labor", "AreaDeTrabajo", lado="r")                          # salta Franja, en

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
