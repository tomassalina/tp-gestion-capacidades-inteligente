# Extensión de Análisis de Datos (NumPy + Matplotlib) — Explicación del trabajo

Este documento explica, para el Grupo 4, todo lo que se hizo en la carpeta `analisis/` para
cumplir con la consigna "Extensión de Análisis de Datos con NumPy y Matplotlib" sobre el TP
*Sistema de Gestión de Capacidades y Asignación de Personal*. Está pensado como material de
consulta para la defensa: qué se hizo, por qué, y con qué métrica/gráfico exacto respalda cada
afirmación.

## 1. Qué pide la consigna y qué se decidió hacer

La consigna pide:

1. Generar ~1000 registros de las entidades principales, **usando el propio sistema** (no pedirle
   el CSV final a una IA).
2. Elegir **3 ejercicios** de análisis de datos sobre ese dataset.
3. Para cada ejercicio: obtención de datos → cálculo de métricas → presentación de resultados →
   al menos un gráfico con Matplotlib → interpretación de resultados.
4. Usar NumPy en el cálculo de métricas (medias, medianas, desvíos, distribuciones de frecuencia,
   comparación de conjuntos, indicadores propios del dominio).

El material de la cátedra sugería 6 ejercicios posibles para este dominio (carga laboral,
credenciales, capacidad de áreas/franjas, eficiencia de asignación, localización inteligente de
personal). Elegimos los **3 que mejor se apoyan en datos y reglas que el sistema ya modela de
verdad** (horas máximas semanales, vigencia de credenciales, capacidad de franja), en vez de
inventar campos que el modelo de clases no tiene:

1. **Carga laboral** (horas asignadas vs. horas máximas semanales)
2. **Cumplimiento de credenciales** (activas vs. vencidas, causas de rechazo de asignaciones)
3. **Capacidad de áreas y franjas horarias** (ocupación real vs. capacidad)

## 2. Cómo se generó el dataset — `generar_dataset.py`

Punto clave: **no se inventaron datos sueltos**. El script importa las clases reales del core
(`Sistema`, `Trabajador`, `Supervisor`, `Labor`, `AreaDeTrabajo`, `Franja`, `Habilidad`,
`CredencialProfesional`, `Asignacion`) y arma el dataset *usando esas clases*, para que todo
quede sujeto a las mismas validaciones que ya existen (`Asignacion.validar_apto`,
`Trabajador.puede_tomar_horas`, etc.). Esto es importante porque significa que el dataset no
puede violar ninguna regla de negocio por construcción.

Se generó:

- **6 áreas** (Planta Robótica, Centro de Datos, Alta Tensión, Laboratorio Industrial, Centro
  Logístico, Planta Química), cada una con 3 franjas (Mañana/Tarde/Noche) con capacidad propia.
- **200 trabajadores** (y supervisores), con categoría (Técnico/Senior/Especialista/Supervisor),
  habilidades y credenciales aleatorias (20% de las credenciales vencidas a propósito).
- **150 labores**, cada una con 1-3 habilidades requeridas y 0-2 credenciales requeridas.
- **1000 asignaciones exitosas**, simuladas **semana a semana** (12 semanas de ~90 días), con
  `reiniciar_horas_trabajadores()` entre semana y semana — igual que hace el core en
  `ejecutar_acciones_semanales()`. Esto es importante: las horas máximas son un tope **semanal**,
  no un tope para todo el período, así que si no se resetean las horas en la simulación, en la
  segunda o tercera semana cualquiera "supera" artificialmente su límite.
- **339 conflictos**: cada vez que una combinación (trabajador, labor, franja, fecha) no pasa las
  validaciones del core, se captura la excepción real que tira `Asignacion` (`TrabajadorNoAptoError`,
  `HorasMaximasExcedidasError`, `FranjaSinLugarError`, `AsignacionDuplicadaError`) y se clasifica en
  un motivo legible (`FALTA_HABILIDAD`, `CREDENCIAL_VENCIDA`, `HORAS_EXCEDIDAS`, `FRANJA_COMPLETA`,
  `LABOR_YA_ASIGNADA`). Esto se guarda en `data/conflictos.csv`, que es un archivo propio (no existe
  en el core, porque el core sólo persiste las asignaciones que *sí* se concretaron).

Al final se llama a `Sistema.guardar_todo()` (el mismo mecanismo de persistencia que usa el resto
del TP), así que los CSV en `analisis/data/` tienen exactamente el mismo formato que los que genera
el sistema real.

## 3. Los 3 ejercicios: datos, métricas, gráficos e interpretación

### Ejercicio 1 — Carga laboral

**Obtención de datos:** se cruza `asignaciones.csv` (quién hizo qué, cuándo) con `labores.csv`
(cuánto dura cada labor) y `trabajadores.csv`/`supervisores.csv` (tope semanal y categoría).

**Métricas (NumPy):** por cada trabajador y cada una de las 12 semanas simuladas se arma una
matriz `horas_matriz` (trabajadores × semanas) con `numpy`, se divide por el tope semanal de cada
uno (`horas_matriz / maximas[:, None] * 100`) y se promedia por fila (`.mean(axis=1)`) para obtener
la utilización semanal promedio de cada trabajador. Se calculan media, mediana y desvío estándar
con `np.mean`/`np.median`/`np.std`, y se usan máscaras booleanas (`utilizacion < 30`,
`horas_matriz.sum(axis=1) == 0`) para contar casos.

> ⚠️ **Nota importante (un error real que encontramos y corregimos):** la primera versión de este
> ejercicio sumaba las horas de **todo el período simulado (90 días)** y las dividía por un tope
> que es **semanal**, lo que daba utilizaciones de hasta 700% — un número sin sentido. El error
> era de normalización (comparar un total acumulado contra un tope de un solo período). Se corrigió
> repartiendo cada asignación en la semana exacta en la que ocurrió (`(fecha - fecha_min).days // 7`)
> y promediando la utilización semana por semana. Como el generador ya respeta el tope semanal al
> crear cada asignación, esta métrica corregida queda matemáticamente acotada entre 0% y 100%.

**Resultados:**
- Utilización semanal promedio: **5,3%** (mediana 1,0%, desvío 10,2).
- **0 trabajadores** superaron su tope semanal en las 12 semanas (confirma que el motor de reglas
  nunca lo permite — no es optimismo, es una restricción matemática del generador).
- **86 de 200 trabajadores (43%)** no recibieron ninguna asignación en todo el período.
- **95%** de la plantilla usa, en promedio, menos del 30% de su capacidad semanal.

**Gráficos:** `01_histograma_utilizacion.png` (histograma de la utilización semanal promedio) y
`02_boxplot_categoria.png` (boxplot por categoría de trabajador).

**Interpretación:** el hallazgo no es sobrecarga (el sistema la impide por diseño), sino
**concentración**: sin cruzar automáticamente quién es apto para qué, el trabajo tiende a caer
siempre sobre el mismo subconjunto de trabajadores "compatibles" con las labores existentes,
dejando a casi la mitad de la plantilla sin ninguna tarea en tres meses.

### Ejercicio 2 — Cumplimiento de credenciales

**Obtención de datos:** se decodifican las credenciales de cada trabajador desde el CSV (reusando
`CredencialProfesional.desde_texto` del core, no un parser propio) y se compara `fecha_caducidad`
contra la fecha de hoy. Se cruza con `conflictos.csv` para ver cuántos rechazos hubo por motivo.

**Métricas (NumPy):** conteo de activas/vencidas; `np.unique(..., return_counts=True)` sobre los
nombres de credenciales para el ranking de más demandadas y sobre los tipos de conflicto para la
distribución de causas de rechazo.

**Resultados:**
- **81,1%** de las credenciales de la plantilla están activas (18,9% vencidas).
- De los **339 conflictos** totales, **270 (79,6%)** son por falta de habilidad, **38 (11,2%)**
  por labor ya asignada, **23 (6,8%)** por credencial vencida, 5 (1,5%) por horas excedidas y
  3 (0,9%) por franja completa.
- La credencial más demandada es "Trabajo en Altura" (92 veces entre toda la plantilla).

**Gráficos:** `03_barras_credenciales.png` (activas vs. vencidas) y
`04_barras_causas_rechazo.png` (barras horizontales con las 5 causas de rechazo, ordenadas).

**Interpretación:** la causa dominante de rechazo es la falta de habilidad, no las credenciales —
la plantilla simulada está, en general, bien certificada. Aun así, cada bloqueo por credencial
vencida es un riesgo de seguridad o cumplimiento evitado automáticamente antes de que ocurra.

> Nota de diseño: se descartó a propósito el gráfico de torta que había en la primera versión.
> Con 5 categorías muy desparejas (79,6% vs. 0,9%), un gráfico de torta hace difícil comparar las
> categorías chicas entre sí; unas barras horizontales ordenadas de mayor a menor comunican lo
> mismo de forma más precisa y son más fáciles de leer en una diapositiva.

### Ejercicio 3 — Capacidad de áreas y franjas horarias

**Obtención de datos:** se decodifica la capacidad de cada franja desde `areas.csv` y se cuenta,
por cada combinación (área, franja), cuántas asignaciones reales hubo.

**Métricas (NumPy):** se arman dos matrices 2D (6 áreas × 3 franjas) con `np.zeros` — una de
ocupación real y otra de capacidad —, y se calcula el porcentaje de ocupación con división
vectorizada (`np.where(capacidad > 0, ocupacion / capacidad * 100, 0)`). La celda más saturada se
encuentra con `np.argmax` + `np.unravel_index`.

> Nota técnica: la capacidad de una franja es un tope **por día** (así la valida el core). Para
> compararla contra la ocupación acumulada de todo el período simulado, la capacidad se multiplica
> por la cantidad de días distintos del dataset (`capacidad_diaria * n_dias_unicos`) — si no se
> hace esto, cualquier combinación área/franja da más de 100% de ocupación por sumar ~90 días de
> uso contra la capacidad de un solo día.

**Resultados:**
- Ocupación promedio del período: **14,2%**.
- Combinación más saturada: **Planta Robótica / Tarde**, con **32,5%** de su capacidad.
- Sólo **3 rechazos** por franja completa en los 339 conflictos totales.

**Gráficos:** `05_heatmap_area_franja.png` (heatmap Área × Franja con el % de ocupación anotado en
cada celda) y `06_barras_rechazos_franja.png` (rechazos por franja completa, agrupados por área).

**Interpretación:** hay capacidad instalada sin usar en la mayoría de los turnos. La próxima
inversión en infraestructura o personal debería dirigirse a los puntos que realmente se saturan
(como Planta Robótica en el turno Tarde), no repartirse parejo entre todas las áreas.

## 4. Archivos de la carpeta `analisis/`

```
analisis/
  generar_dataset.py        # genera el dataset usando las clases reales del core
  analisis_capacidades.py   # los 3 ejercicios: metricas con NumPy + graficos con Matplotlib
  requirements.txt          # numpy, matplotlib (el core sigue sin dependencias externas)
  data/                     # CSVs generados (incluye conflictos.csv, que es propio del analisis)
  graficos/                 # los 6 PNG (2 por ejercicio)
  resumen_metricas.json     # todas las metricas calculadas, en un solo archivo (insumo del PPTX)
  presentacion_defensa.pptx # la presentacion para la defensa
```

## 5. Cómo reproducir todo

```bash
cd analisis
pip install -r requirements.txt   # o: uv pip install -r requirements.txt
python generar_dataset.py         # regenera data/ (dataset nuevo, con otra semilla aleatoria fija)
python analisis_capacidades.py    # regenera graficos/ y resumen_metricas.json
```

El generador usa `random.seed(42)`, así que correrlo de nuevo da siempre el mismo dataset
(reproducible), salvo que se cambie esa semilla.

## 6. Qué cubre cada requisito de la consigna

| Requisito de la consigna | Dónde está |
|---|---|
| Dataset generado con el propio sistema (no pedido a una IA) | `generar_dataset.py`, usa las clases reales |
| ~1000 registros de la entidad principal | 1000 asignaciones (+ 339 conflictos, + 200 trabajadores, + 150 labores) |
| 3 ejercicios con obtención de datos, métricas, resultados, gráfico e interpretación | Sección 3 de este documento, implementado en `analisis_capacidades.py` |
| Uso de NumPy (medias, medianas, desvíos, distribuciones de frecuencia, indicadores propios) | `np.mean`, `np.median`, `np.std`, `np.unique(return_counts=True)`, matrices 2D, máscaras booleanas, `np.argmax`/`np.unravel_index` |
| Gráficos con título, ejes y leyenda | Los 6 PNG en `graficos/` |
| Interpretación de resultados | Sección 3 de este documento + la diapositiva de "lectura de negocio" de cada hallazgo en el PPTX |
