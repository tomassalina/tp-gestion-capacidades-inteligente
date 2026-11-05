import json

AZUL_BORDE = "#1971c2"
AZUL_TEXTO = "#1971c2"
NEGRO = "#1e1e1e"

_seed = [9000]


def next_seed():
    _seed[0] += 1
    return _seed[0]


def _base(tipo, x, y, width, height, **extra):
    s = next_seed()
    el = {
        "id": f"{tipo}-{s}",
        "type": tipo,
        "x": x, "y": y, "width": width, "height": height,
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
        el["strokeColor"] = AZUL_BORDE
    return el


def texto(x, y, width, texto_str, size=16, azul=False, bold_title=False):
    el = _base("text", x, y, width, size + 6)
    el["strokeColor"] = AZUL_TEXTO if azul else NEGRO
    el["text"] = texto_str
    el["fontSize"] = size
    el["fontFamily"] = 1
    el["textAlign"] = "left"
    el["verticalAlign"] = "top"
    el["containerId"] = None
    el["originalText"] = texto_str
    el["lineHeight"] = 1.25
    el["baseline"] = size - 2
    return el


def flecha(x1, y1, x2, y2, triangulo=False, azul=False):
    el = _base("arrow", x1, y1, x2 - x1, y2 - y1)
    if azul:
        el["strokeColor"] = AZUL_BORDE
    el["points"] = [[0, 0], [x2 - x1, y2 - y1]]
    el["lastCommittedPoint"] = None
    el["startBinding"] = None
    el["endBinding"] = None
    el["startArrowhead"] = None
    el["endArrowhead"] = "triangle_outline" if triangulo else "arrow"
    return el


elementos = []
cajas = {}  # nombre -> (x, y, w, h) para calcular flechas despues

LINE_H = 20
PAD = 14
TITLE_H = 28


def clase(nombre_box, x, y, width, titulo, lineas, azul_caja=False):
    """lineas: lista de (texto, es_azul). Calcula el alto solo y devuelve (x,y,w,h)."""
    altura = TITLE_H + PAD + len(lineas) * LINE_H + PAD
    elementos.append(rect(x, y, width, altura, azul=azul_caja))
    elementos.append(texto(x + 10, y + 6, width - 20, titulo, size=19, azul=azul_caja))
    cy = y + TITLE_H + PAD
    for linea, es_azul in lineas:
        elementos.append(texto(x + 14, cy, width - 28, linea, size=14, azul=es_azul))
        cy += LINE_H
    cajas[nombre_box] = (x, y, width, altura)
    return (x, y, width, altura)


def arrow_between(origen, destino, triangulo=False, azul=False, lado_origen="r", lado_destino="l"):
    ox, oy, ow, oh = cajas[origen]
    dx, dy, dw, dh = cajas[destino]
    puntos_o = {"r": (ox + ow, oy + oh / 2), "l": (ox, oy + oh / 2), "b": (ox + ow / 2, oy + oh), "t": (ox + ow / 2, oy)}
    puntos_d = {"r": (dx + dw, dy + dh / 2), "l": (dx, dy + dh / 2), "b": (dx + dw / 2, dy + dh), "t": (dx + dw / 2, dy)}
    x1, y1 = puntos_o[lado_origen]
    x2, y2 = puntos_d[lado_destino]
    elementos.append(flecha(x1, y1, x2, y2, triangulo=triangulo, azul=azul))


B = False  # atajo: linea negra
A = True   # atajo: linea azul (estructura de datos)

# ---------------------------------------------------------------------------
# Fila 1: primitivas de estructuras de datos (todo azul)
# ---------------------------------------------------------------------------
clase("nodo", 40, 40, 260, "Nodo", [
    ("dato", B), ("siguiente: Nodo", B),
    ("get_dato() / get_siguiente()", B),
    ("set_siguiente(siguiente)", B),
], azul_caja=True)

clase("lista_enlazada", 340, 40, 320, "ListaEnlazada", [
    ("inicio: Nodo", B),
    ("insertar_inicio(dato)", B),
    ("insertar_despues_de(nodo, dato)", B),
    ("buscar(valor)  [recursivo]", B),
    ("eliminar(valor)  [recursivo]", B),
    ("recorrer()  [while, no recursivo]", B),
    ("esta_vacia() / get_inicio()", B),
], azul_caja=True)

clase("cola", 700, 40, 300, "Cola", [
    ("inicio: Nodo, fin: Nodo", B),
    ("cantidad: int", B),
    ("encolar(dato) / desencolar()", B),
    ("esta_vacia() / get_inicio()", B),
    ("get_cantidad()", B),
], azul_caja=True)

clase("agenda", 1040, 40, 300, "Agenda", [
    ("extends ListaEnlazada", B),
    ("agregar(asignacion)  [recursivo:", B),
    ("  insertar_ordenado_despues]", B),
    ("hereda: eliminar, recorrer,", B),
    ("  esta_vacia, get_inicio", B),
], azul_caja=True)

# ---------------------------------------------------------------------------
# Fila 2: clases de valor (habilidades, credenciales, franjas)
# ---------------------------------------------------------------------------
clase("habilidad", 40, 300, 260, "Habilidad", [
    ("nombre: str", B),
    ("get_nombre() / set_nombre()", B),
    ("__eq__ / __hash__ (por nombre)", B),
    ("guardar() / cargar_todas()", B),
])

clase("habilidad_de_trabajador", 340, 300, 280, "HabilidadDeTrabajador", [
    ("habilidad: Habilidad", B),
    ("nivel: int", B),
    ("cumple_nivel_minimo(nivel_minimo)", B),
])

clase("habilidad_requerida", 660, 300, 280, "HabilidadRequerida", [
    ("habilidad: Habilidad", B),
    ("nivel_minimo: int", B),
])

clase("credencial", 980, 300, 280, "CredencialProfesional", [
    ("nombre, fecha_obtencion,", B),
    ("  fecha_caducidad", B),
    ("esta_activa(fecha)", B),
])

clase("franja", 1300, 300, 260, "Franja", [
    ("nombre: str, capacidad: int", B),
    ("(no trackea ocupacion: es de Sistema)", B),
])

# ---------------------------------------------------------------------------
# Fila 3: catalogo (area, labor)
# ---------------------------------------------------------------------------
clase("area", 40, 500, 320, "AreaDeTrabajo", [
    ("nombre: str", B),
    ("credenciales_obligatorias: list", B),
    ("franjas: list[Franja]", B),
    ("franjas_por_nombre: dict", A),
    ("buscar_franja(nombre)  [dict, O(1)]", A),
    ("agregar_franja(franja)", B),
])

clase("labor", 400, 500, 320, "Labor", [
    ("titulo, descripcion, duracion_horas", B),
    ("habilidades_requeridas: list", B),
    ("credenciales_requeridas: list", B),
    ("area: AreaDeTrabajo", B),
])

# ---------------------------------------------------------------------------
# Fila 4: personas
# ---------------------------------------------------------------------------
clase("trabajador", 40, 760, 380, "Trabajador", [
    ("id, nombre, horas_maximas_semana,", B),
    ("  horas_asignadas", B),
    ("habilidades: list[HabilidadDeTrabajador]", B),
    ("repertorio_habilidades: set", A),
    ("credenciales: list", B),
    ("atributos: dict  (**kwargs)", A),
    ("agenda: Agenda", A),
    ("agregar_habilidad()  [usa el set]", A),
    ("habilidades_en_comun/exclusivas()", A),
    ("  [interseccion / diferencia de sets]", A),
    ("tiene_habilidades / tiene_credenciales_activas", B),
    ("puede_tomar_horas / sumar_horas / restar_horas", B),
    ("agregar_a_agenda / sacar_de_agenda", A),
    ("solicitar_asignacion(sistema, ...)", B),
])

clase("supervisor", 500, 760, 320, "Supervisor", [
    ("extends Trabajador", B),
    ("aprobar_asignacion(sistema, asignacion)", B),
    ("rechazar_asignacion(sistema, asignacion)", B),
    ("reasignar_asignacion(asignacion, nuevo)", B),
    ("asignar_trabajador(sistema, ...)", B),
    ("agregar_regla_area(area, credencial)", B),
])

# ---------------------------------------------------------------------------
# Fila 5: asignacion
# ---------------------------------------------------------------------------
clase("asignacion", 40, 1080, 380, "Asignacion", [
    ("trabajador, labor, franja, fecha, estado", B),
    ("evaluar_aptitud(trab, labor, fecha)", B),
    ("  [static, regla 15: brecha completa]", B),
    ("contar_ocupantes(asigs, franja, area, fecha)", B),
    ("validar_apto(...)  [static]", B),
    ("aprobar() / rechazar() / reasignar(nuevo)", B),
    ("guardar() / cargar_todas()", B),
])

clase("tipo_accion_bitacora", 500, 1080, 280, "TipoAccionBitacora", [
    ("PROPUESTA / APROBACION / REVERSION", B),
    ("(constantes de clase, sin instancias)", B),
])

# ---------------------------------------------------------------------------
# Fila 6: Sistema (orquestador)
# ---------------------------------------------------------------------------
clase("sistema", 900, 760, 460, "Sistema", [
    ("trabajadores, areas, labores: list", B),
    ("trabajadores_por_id: dict", A),
    ("  [buscar por legajo en O(1)]", A),
    ("solicitudes_pendientes: Cola", A),
    ("asignaciones: list[Asignacion]", B),
    ("ocupacion: dict con clave (fecha,franja,area)", A),
    ("  [tupla como clave, regla 16]", A),
    ("bitacora: list de tuplas (fecha,tipo,labor,trab)", A),
    ("  [regla 18, inmutable]", A),
    ("buscar_trabajador_por_id(id)  [dict]", A),
    ("solicitar_asignacion / buscar_trabajadores_disponibles", B),
    ("generar_sugerencias(fecha) / ciclo_semanal(fecha)", B),
    ("registrar_ocupacion / contar_ocupacion  [dict]", A),
    ("registrar_en_bitacora / obtener_bitacora  [tupla]", A),
    ("guardar_todo() / cargar_todo()", B),
])

clase("repositorio_csv", 900, 1240, 460, "RepositorioCSV", [
    ("ruta_archivo: str, columnas: list", B),
    ("create(**datos) / find(id) / find_all()", B),
    ("update(id, **datos) / delete(id)", B),
    ("generico: no sabe nada del dominio", B),
])

# ---------------------------------------------------------------------------
# Flechas: herencia (triangulo) y composicion/uso
# ---------------------------------------------------------------------------
arrow_between("supervisor", "trabajador", triangulo=True, lado_origen="l", lado_destino="r")
arrow_between("agenda", "lista_enlazada", triangulo=True, azul=True, lado_origen="t", lado_destino="b")
arrow_between("cola", "nodo", azul=True, lado_origen="l", lado_destino="r")
arrow_between("lista_enlazada", "nodo", azul=True, lado_origen="t", lado_destino="b")
arrow_between("trabajador", "agenda", azul=True, lado_origen="t", lado_destino="b")
arrow_between("trabajador", "habilidad_de_trabajador", lado_origen="t", lado_destino="b")
arrow_between("labor", "habilidad_requerida", lado_origen="t", lado_destino="b")
arrow_between("habilidad_de_trabajador", "habilidad", lado_origen="t", lado_destino="b")
arrow_between("habilidad_requerida", "habilidad", lado_origen="t", lado_destino="r")
arrow_between("labor", "area", lado_origen="l", lado_destino="r")
arrow_between("area", "franja", lado_origen="r", lado_destino="l")
arrow_between("asignacion", "trabajador", lado_origen="t", lado_destino="b")
arrow_between("asignacion", "labor", lado_origen="r", lado_destino="b")
arrow_between("sistema", "trabajador", lado_origen="l", lado_destino="r")
arrow_between("sistema", "asignacion", lado_origen="l", lado_destino="r")
arrow_between("sistema", "repositorio_csv", lado_origen="b", lado_destino="t")
arrow_between("sistema", "cola", azul=True, lado_origen="t", lado_destino="b")

# ---------------------------------------------------------------------------
# Referencia de colores
# ---------------------------------------------------------------------------
elementos.append(rect(1460, 1080, 340, 150))
elementos.append(texto(1475, 1090, 310, "Referencia", size=18))
elementos.append(texto(1475, 1125, 310, "Negro: clases/atributos/metodos", size=14))
elementos.append(texto(1475, 1145, 310, "  comunes (POO, sin estructura", size=14))
elementos.append(texto(1475, 1165, 310, "  de datos especifica)", size=14))
elementos.append(texto(1475, 1190, 310, "Azul: estructura de datos de la", size=14, azul=True))
elementos.append(texto(1475, 1210, 310, "  materia (dict, set, tupla, Cola,", size=14, azul=True))

diagrama = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elementos,
    "appState": {"gridSize": 20, "viewBackgroundColor": "#ffffff"},
    "files": {},
}

with open("diagrama_clases_v4.excalidraw", "w") as f:
    json.dump(diagrama, f, indent=2)

print(f"Generado diagrama_clases_v4.excalidraw con {len(elementos)} elementos ({len(cajas)} clases)")
