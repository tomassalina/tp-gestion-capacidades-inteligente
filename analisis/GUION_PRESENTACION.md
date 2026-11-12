# Guión para la defensa — CapacIA (Grupo 4)

Guión pensado para leer/practicar antes de presentar `presentacion_defensa.pptx`. Duración
estimada: 6-8 minutos hablando con calma. Las diapositivas 8 a 11 (el análisis de datos) están
desarrolladas con más detalle porque es la parte que probablemente más nos van a preguntar — ahí
vive el NumPy/Matplotlib real.

Al final hay una sección de **preguntas esperables** con la respuesta ya preparada.

---

## Diapositiva 1 — Portada

"Buenas tardes, somos el Grupo 4. Les venimos a presentar CapacIA: un sistema de asignación
inteligente de personal industrial. Antes de pasar a los números, les contamos rápido el problema
que resuelve y cómo funciona por dentro — y después nos metemos de lleno en los datos, que es lo
que más les va a interesar."

## Diapositiva 2 — Agenda

"Vamos a hablar de cinco cosas: el problema que vimos, cómo lo resolvimos, cómo lo validamos con
datos — esta es la parte central —, la oportunidad de negocio, y qué estamos pidiendo."

## Diapositiva 3-4 — El problema

"La asignación manual de personal, cuando hay que cruzar habilidades, credenciales, horas máximas
y turnos al mismo tiempo, no escala. Vimos cuatro síntomas típicos: sobrecarga invisible porque
nadie ve el reparto real de horas; riesgo de cumplimiento cuando se asigna a alguien con una
credencial vencida; capacidad ociosa en turnos que nadie mira; y decisiones lentas porque rehacer
el cronograma a mano lleva horas."

## Diapositiva 5-6 — La solución

"CapacIA no es una interfaz más: es un motor de reglas que valida cuatro cosas en el momento en
que se intenta cada asignación — habilidades, credenciales vigentes, horas máximas semanales y
capacidad de la franja. Si alguna regla no se cumple, la asignación nunca se concreta, y el motivo
exacto queda registrado como un conflicto. Esto es clave: **no es una afirmación de marketing**,
es literalmente el código que ya tenemos funcionando y testeado con 128 tests."

## Diapositiva 7 — Transición a la validación

"Para demostrar que esto funciona con datos reales — no con un ejemplo de tres personas —, armamos
un piloto simulado: generamos un dataset usando las clases reales del sistema, no datos sueltos,
para que todo respete las mismas reglas de negocio."

## Diapositiva 8 — El piloto, en números

*(Esta es la entrada al análisis de datos. Conviene explicar bien cómo se armó el dataset, porque
seguro preguntan esto.)*

"Simulamos 200 trabajadores, 6 áreas de planta, 150 tipos de labor, y un período de 12 semanas
(90 días). Sobre eso corrimos el motor de asignación semana a semana — reseteando las horas de
cada trabajador al empezar cada semana, igual que hace el sistema real — y dejamos que compita por
cada tarea quien tuviera las habilidades y credenciales necesarias. El resultado: 1.000
asignaciones que sí se concretaron, y 339 intentos que el sistema rechazó automáticamente, cada
uno con su motivo exacto guardado. Ese archivo de conflictos es nuestro, no viene del sistema
original, porque el core sólo guarda lo que se concreta; nosotros necesitábamos ver también lo que
se bloqueó para poder analizarlo."

## Diapositiva 9 — Hallazgo 1: Carga laboral

*(La parte más técnica. Acá conviene mostrar que entendemos la métrica, no solo leerla.)*

"Para cada trabajador, calculamos cuántas horas tuvo asignadas en cada una de las 12 semanas, y
las comparamos contra su tope semanal — eso nos da un % de utilización por semana, que promediamos
en todo el período. Usamos NumPy para armar una matriz de 200 trabajadores por 12 semanas y
vectorizar esa cuenta en vez de hacerlo con loops.

Un dato importante: la utilización nunca puede pasar el 100%, y no es casualidad — es porque el
motor de reglas directamente no deja crear una asignación que exceda el tope semanal. Lo
confirmamos en los datos: cero trabajadores lo superaron. El hallazgo interesante no es sobrecarga,
entonces, sino **concentración**: el 43% de la plantilla — 86 de 200 — no recibió ninguna
asignación en las 12 semanas, y el 95% usó en promedio menos del 30% de su capacidad. Sin un motor
que cruce automáticamente quién es apto para cada tarea, el trabajo se termina concentrando
siempre en el mismo grupo chico de trabajadores 'compatibles', y el resto queda ocioso sin que
nadie lo note."

## Diapositiva 10 — Hallazgo 2: Cumplimiento de credenciales

"Acá decodificamos las credenciales de cada trabajador — reusando el mismo parser que usa el
sistema real para no inventar un formato propio — y las comparamos contra la fecha de hoy para ver
cuáles seguían vigentes. El 81% de las credenciales de la plantilla están activas. Después cruzamos
esto con los 339 conflictos: la causa más común de rechazo, por lejos, es la falta de habilidad
(80%), no las credenciales (7%) — la plantilla simulada está, en general, bien certificada. Aun
así, cada uno de esos rechazos por credencial vencida es un accidente o una sanción que el sistema
evitó antes de que pasara, no después."

*(Si preguntan por qué no hay un gráfico de torta acá: "Decidimos usarlo con barras horizontales
en vez de torta porque las 5 categorías son muy desparejas — una tiene 80% y otra 0,9% — y en una
torta esas diferencias chicas son difíciles de comparar a simple vista. Con barras ordenadas se lee
mejor.")*

## Diapositiva 11 — Hallazgo 3: Capacidad de áreas y franjas

"Para este ejercicio armamos dos matrices de 6 áreas por 3 franjas: una con la capacidad que
declara cada área y otra con la ocupación real que registramos. La capacidad de una franja es un
tope por día, así que para compararla contra todo el período tuvimos que escalarla por la cantidad
de días simulados — si no, cualquier combinación da más de 100% sólo por acumular 90 días contra
la capacidad de un solo día. Con esa normalización, la ocupación promedio del período es 14%, y la
combinación más exigida es Planta Robótica en el turno Tarde, con un 32%. Casi no hubo rechazos por
franja completa — sólo 3 de 339 —, lo que confirma que, en este piloto, el cuello de botella no es
la capacidad instalada sino, otra vez, la falta de personal apto para cubrir cada tarea."

## Diapositiva 12 — Oportunidad de negocio

"Con el motor ya validado, la oportunidad es clara: un mercado de plantas industriales con turnos
y credenciales obligatorias, un modelo de ingresos tipo SaaS por trabajador gestionado, y lo más
importante — pasar de 200 a 2.000 trabajadores es un cambio de escala de datos, no de arquitectura,
porque el motor de reglas ya es el mismo que usamos en el piloto."

## Diapositiva 13 — Cierre

"Estamos buscando una ronda semilla para escalar el piloto a producción, con un plan concreto de
próximos pasos. Gracias, quedamos abiertos a preguntas."

---

## Preguntas esperables sobre el análisis de datos (con respuesta lista)

**¿Por qué eligieron estos 3 ejercicios y no otros de los que proponía la cátedra?**
Porque son los que mejor se apoyan en datos y reglas que el sistema ya modela de verdad (horas
máximas semanales, vigencia de credenciales, capacidad de franja), sin tener que inventar campos
que las clases del TP no tienen.

**¿Cómo generaron el dataset sin inventar los datos sueltos?**
El generador (`generar_dataset.py`) instancia las clases reales del sistema (`Sistema`,
`Trabajador`, `Labor`, `Asignacion`, etc.) y arma cada asignación llamando al constructor real, que
valida todas las reglas de negocio. Si una combinación no cumple una regla, se captura la excepción
real que tira el sistema y se registra como conflicto — no se "simulan" conflictos a mano.

**¿Qué funciones de NumPy usaron específicamente?**
`np.mean`, `np.median`, `np.std` para las métricas descriptivas; `np.unique(..., return_counts=True)`
para las distribuciones de frecuencia (credenciales más demandadas, causas de rechazo); matrices 2D
con `np.zeros` y operaciones vectorizadas (`np.where`, división elemento a elemento) para el
heatmap de área × franja; máscaras booleanas (`utilizacion < 30`) para contar casos; `np.argmax` +
`np.unravel_index` para encontrar la combinación más saturada.

**¿Por qué la utilización de ningún trabajador supera el 100%?**
Porque el motor de reglas no permite crear una asignación que haga que un trabajador supere su tope
semanal — lo rechaza con `HorasMaximasExcedidasError` antes de que se concrete. No es un límite que
pusimos en el gráfico, es una propiedad del sistema que confirmamos con los datos.

**¿Cómo se dieron cuenta de que había que normalizar por semana en vez de por todo el período?**
Al correr el análisis la primera vez, el histograma de utilización daba valores de hasta 700%, algo
imposible dado que el tope es semanal. Revisando el cálculo, estábamos sumando las horas de los 90
días contra un tope de una sola semana. Lo corregimos repartiendo cada asignación en la semana en
la que ocurrió y promediando la utilización semana por semana.

**¿Por qué sacaron el gráfico de torta?**
Con 5 categorías muy desparejas en tamaño, una torta hace difícil comparar las porciones chicas
entre sí. Elegimos barras horizontales ordenadas de mayor a menor, que comunican la misma
información pero se leen con más precisión.

**¿De dónde salen los conflictos, si el sistema original no los persiste?**
`Sistema.guardar_todo()` sólo persiste lo que se concretó. Como para el análisis necesitábamos ver
también los rechazos, agregamos nuestro propio `conflictos.csv`, generado capturando las excepciones
reales durante la simulación — no es parte del core, es un artefacto propio del análisis.
