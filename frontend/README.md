# Frontend (Streamlit)

## Qué es esta carpeta

Esta carpeta contiene únicamente la interfaz web del TP, hecha con [Streamlit](https://streamlit.io/).
Está separada a propósito de las clases principales del TP (`sistema.py`, `trabajador.py`,
`supervisor.py`, etc., ubicadas en el directorio padre).

El profesor permite que el frontend esté armado con ayuda de IA, pero las clases del TP
(el "core" del dominio) tienen que mantenerse con el estilo estándar de la materia, sin
tocar ni duplicar su lógica. Por eso todo el código moderno/idiomático (type hints,
comprehensions, f-strings, Streamlit) vive solo acá adentro, y el resto del proyecto no
se modifica.

## Cómo se conecta al código del TP

`app.py` agrega el directorio padre a `sys.path` (con `sys.path.insert(0, ...)`) e importa
directamente las clases reales: `Sistema`, `Trabajador`, `Supervisor`, `AreaDeTrabajo`,
`Labor`, `Franja`, `Habilidad`, `CredencialProfesional`, etc.

La UI **no reimplementa ninguna regla de negocio**: todas las validaciones y reglas
(horas máximas, habilidades requeridas, credenciales vigentes, capacidad de franjas,
transición de estados de una asignación, etc.) viven en esas clases y se invocan a
través de sus métodos públicos (`sistema.registrar_personal(...)`,
`sistema.generar_sugerencias(...)`, `sistema.ciclo_semanal(...)`,
`supervisor.aprobar_asignacion(...)`, `supervisor.reasignar_asignacion(...)`,
`supervisor.agregar_regla_area(...)`, etc.). El frontend solo arma la interfaz y
muestra/envía datos.

**Nota técnica importante**: los archivos del core (`asignacion.py`, `trabajador.py`,
`sistema.py`, etc.) tienen sus tests de `pytest` escritos en el mismo archivo que la
clase (no en archivos `test_*.py` separados), con un `import pytest` incondicional al
principio del archivo de tests. Esto significa que **`pytest` es una dependencia real
en tiempo de ejecución** para poder importar esos módulos desde `app.py`, aunque el
frontend en sí no use pytest para nada. Por eso está listado en `requirements.txt`.

## Cómo correr la app

Esta máquina tiene un `python3` de Homebrew (3.14.5) con un bug conocido en `pyexpat`
que puede romper `pip`/`streamlit`. Se verificó que el siguiente camino funciona bien,
usando `python3.12` (disponible en `/opt/homebrew/bin/python3.12`) a través de `uv`:

```bash
cd frontend
uv venv --python 3.12 .venv
uv pip install -r requirements.txt --python .venv/bin/python
.venv/bin/python -m streamlit run app.py
```

Esto abre la app en `http://localhost:8501`. Los tres comandos de arriba son los que se
probaron realmente en esta máquina (instalación de dependencias y arranque del servidor
sin excepciones de Python).

Si preferís no crear el venv manualmente, también funciona (se probó explícitamente):

```bash
cd frontend
uv run --python 3.12 --with-requirements requirements.txt streamlit run app.py
```

(`uv run --python 3.12 streamlit run app.py` a secas **no funciona** en esta máquina:
al no haber un `pyproject.toml` en `frontend/`, `uv` no instala las dependencias de
`requirements.txt` solo y falla con `Failed to spawn: streamlit`. Por eso hace falta
`--with-requirements requirements.txt`, o directamente el camino del `.venv` de arriba).

## Qué tiene la app

La app arranca con datos de ejemplo precargados (un área "Cocina", una labor, franjas
y un par de trabajadores + una supervisora) para poder probarla sin cargar nada a mano.
Tiene 4 pestañas:

- **Personal**: tabla con los trabajadores actuales (horas asignadas/máximas,
  habilidades, credenciales, atributos) y un formulario para registrar uno nuevo. El
  formulario permite agregar pares clave/valor libres *antes* de enviar, que se pasan
  como `**atributos` a `sistema.registrar_personal(...)`.
- **Áreas y Labores**: lista las áreas (con sus franjas y credenciales obligatorias) y
  las labores (con sus requisitos de habilidades/credenciales), leído directamente de
  los objetos reales.
- **Asignaciones**: botones para `generar_sugerencias(fecha)` y `ciclo_semanal(fecha)`,
  un flujo manual opcional para `solicitar_asignacion(...)` +
  `ejecutar_acciones_del_sistema(...)`, y por cada asignación Sugerida/Pendiente,
  acciones para aprobarla o reasignarla a otro trabajador usando los métodos reales de
  `Supervisor`.
- **Reglas**: formulario para que la supervisora agregue una credencial obligatoria a
  un área vía `supervisor.agregar_regla_area(area, credencial)`.
