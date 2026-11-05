# Trabajo Práctico: Sistema de Gestión de Capacidades y Asignación Inteligente

## Situación Hipotética

Imaginemos que son parte del equipo de desarrollo de software en *Innovación Industrial Tech (IIT)*, una empresa líder en la gestión de infraestructuras críticas y plantas de producción de alta tecnología. IIT opera en diversos sectores, desde la manufactura avanzada hasta el mantenimiento de complejos centros de datos y sistemas energéticos. La eficiencia operativa, la seguridad del personal y el cumplimiento normativo son pilares fundamentales de su negocio.

Actualmente, IIT enfrenta un desafío significativo: la asignación manual de su personal técnico, a las distintas labores diarias. Este proceso es ineficiente, propenso a errores y no optimiza el uso de los recursos humanos. El personal debe ser asignado a diferentes áreas de trabajo (por ejemplo, "Planta de Ensamble Robótico", "Sala de Servidores Críticos", "Mantenimiento de Líneas de Alta Tensión"), cada una con sus propias complejidades y requisitos.

Cada miembro del personal posee un conjunto único de habilidades técnicas y credenciales profesionales específicas (como "Seguridad Eléctrica Nivel 3", "Manejo de Sustancias Peligrosas", "Certificación Cisco CCNA", "Trabajo en Altura"). Estas credenciales profesionales tienen una fecha de inicio y una fecha de expiración, y es fundamental que estén activas al momento de considerar a alguien para una asignación.

Las labores a realizar son diversas: desde mantenimiento preventivo, reparaciones urgentes, instalaciones de nuevos equipos, hasta supervisiones de seguridad. Cada labor tiene una duración prevista, y demanda un conjunto específico de competencias y credenciales para su ejecución segura y correcta. Además, ciertas labores solo pueden realizarse en un área de trabajo específica.

La jornada operativa se organiza en franjas horarias (Mañana, Tarde, Noche), y cada área de trabajo tiene un límite de personal por franja para asegurar la seguridad y el espacio adecuado. La empresa busca asegurar que ningún trabajador exceda el máximo de horas laborales semanales establecido por su contrato y que siempre se respeten las regulaciones laborales.

Los *Supervisores* de cada área de trabajo son responsables de validar las asignaciones finales, asegurándose de que el personal cumpla con todos los requisitos y de que las tareas se distribuyan equitativamente, o según prioridades específicas. Necesitan una herramienta que les permita visualizar rápidamente quién está disponible, quién es apto para una labor y qué labores aún no tienen asignación.

El sistema actual es ineficiente y no permite, por ejemplo, identificar rápidamente a un profesional con las credenciales activas para una labor urgente en un área específica, o determinar si un trabajador ya ha alcanzado su límite de horas semanales. Se requiere un sistema robusto que permita gestionar estas asignaciones de forma inteligente y segura.

Su misión es diseñar y desarrollar un prototipo de este *Sistema de Gestión de Capacidades y Asignación*, que permita automatizar y validar la asignación de personal a las diversas labores, considerando sus competencias, las credenciales activas, la disponibilidad de las áreas de trabajo y sus franjas horarias, y la carga laboral semanal de cada individuo. El diseño debe ser modular y permitir la futura incorporación de funcionalidades, como la priorización de tareas o la gestión de vacaciones.

## Requerimientos Técnicos Obligatorios

## Reglas de Negocio

1.  **Registro y Carga Laboral del Personal:** Cada miembro del personal se identifica de forma única y posee un nombre, un repertorio de habilidades y un conjunto de credenciales profesionales. Asimismo, se le establece un límite máximo de horas de trabajo por semana que no debe ser superado. Al inicio de su registro, no tendrá horas laborales asignadas.

2.  **Vigencia de Credenciales Profesionales:** Cada credencial profesional tiene un nombre, una fecha en que fue obtenida y otra en que caduca. Es fundamental poder determinar si una credencial está activa o vencida en un momento dado.

3.  **Descripción de Labores:** Cada labor se describe con un identificador único, un título, una explicación detallada y una duración estimada en horas. Para su ejecución, requiere un perfil específico de habilidades y un conjunto de credenciales profesionales. Además, cada labor se adscribe a un área de trabajo concreta.

4.  **Aptitud para la Labor:** Un trabajador solo puede ser considerado para una labor si posee *todas* las competencias exigidas por dicha labor y *todas* las credenciales profesionales requeridas que estén activas en la fecha de la asignación. De no cumplirse estos requisitos, el sistema debe indicar claramente la inaptitud del trabajador.

5.  **Respeto por la Carga Horaria Máxima:** Al asignar una labor a un trabajador, el sistema debe asegurar que la duración prevista de la labor no supere el límite máximo de horas semanales del trabajador, tomando en cuenta las horas ya comprometidas para esa semana. Si este límite se sobrepasa, el sistema debe notificar que la carga laboral es excesiva.

6.  **Límite de Personal por Franja Horaria y Área:** Cada franja horaria en un área de trabajo específica tiene un número máximo de personal permitido. No es posible asignar a un trabajador a una franja horaria si al hacerlo se excede la capacidad designada para esa combinación de franja y área. En tal situación, el sistema debe señalar que la franja horaria está completa.

7.  **Exclusividad de Asignación:** Una labor particular solo puede ser confiada a *un único* trabajador para una franja horaria y fecha específica. Si se intenta volver a asignar una labor que ya ha sido comprometida para ese momento, el sistema debe advertir que la labor ya tiene una asignación.

8.  **Facultades de Supervisión:** Los *Supervisores*, además de poder realizar labores como cualquier otro trabajador, poseen la facultad de formalizar una asignación, transformando su estatus de 'Pendiente' a 'Aprobada'.

9.  **Contabilidad de Horas Asignadas:** Cuando una labor es exitosamente propuesta a un trabajador (previo a la formalización por parte de un supervisor), las horas previstas de esa labor deben sumarse a la carga laboral actual del trabajador para la semana.

10. **Credenciales Obligatorias por Área:** Cada área de trabajo puede requerir un conjunto específico de credenciales profesionales que son obligatorias para cualquier trabajador que realice alguna labor en dicho espacio. Un trabajador solo podrá ser asignado a una labor en esa área si posee todas estas credenciales activas. En caso contrario, el sistema debe señalar que el trabajador no es apto para esa área.

11. **Localización de Personal Disponible:** El sistema debe ser capaz de identificar, para una labor, franja horaria y fecha determinadas, qué trabajadores están disponibles. Esto implica que los trabajadores encontrados deben poseer las habilidades y credenciales activas (tanto las de la labor como las obligatorias del área), que la labor no los lleve a exceder su límite de horas semanales, y que la franja horaria en el área de trabajo aún tenga capacidad.

12. **Inicio de Nueva Semana:** Al comienzo de cada nueva semana, la contabilidad de horas laborales asignadas a cada trabajador debe ser reestablecida a cero, reflejando el inicio de un nuevo ciclo.

## Notas

- Se prohíbe el uso de la librería pandas; el objetivo es evaluar el manejo de estructuras nativas (listas, diccionarios) y la lógica de algoritmos manuales.

- Es requisito obligatorio presentar un diagrama de flujo previo a la codificación para organizar la arquitectura lógica y prevenir fallos de diseño.

- Cada implementación debe estar debidamente sustentada; el alumno debe ser capaz de explicar y justificar técnicamente las decisiones tomadas en el código.

- Se recomienda el uso de la librería estándar de Python (como datetime o math) para optimizar tareas específicas y evitar la redacción innecesaria de funciones ya existentes.

## Extensión de Consigna: Capacidades Inteligentes (`**kwargs`)

Registro de nuevo personal con atributos opcionales:

```python
def registrar_personal(self, id, nombre, horas_max, **atributos)
```

Registra un nuevo miembro del personal con sus atributos opcionales.

**Por qué:** El personal puede tener atributos variables según el rol: idiomas, área de origen, turnos preferidos, certificaciones iniciales. Con `**kwargs` el sistema almacena esos atributos como un diccionario interno sin necesidad de definir cada campo por separado, y el código cliente puede consultar atributo por clave.

## Extensión de Consigna: Urgencias, Reversiones y Trazabilidad de Asignaciones

Tras las primeras semanas de uso del prototipo, los supervisores de IIT detectaron nuevas necesidades operativas. El sistema debe incorporar los siguientes comportamientos **sin romper las reglas de negocio 1 a 12 ni las pruebas existentes**.

### Nuevas Reglas de Negocio

13. **Labores urgentes en espera:** Cuando se solicita cubrir una labor urgente y no existe personal disponible (según la regla 11), la labor no se descarta: queda en espera. Cada vez que se libera capacidad (por una reversión, por el inicio de una nueva semana o por el alta de personal), el sistema intenta cubrir las labores en espera **respetando estrictamente el orden en que fueron quedando pendientes**. Si la primera de ellas sigue sin poder cubrirse, conserva su lugar y no es adelantada por las siguientes. Debe poder consultarse cuántas labores esperan y cuál es la próxima a atender, sin alterar la espera. *(Estructura prevista: cola FIFO. Pendiente de implementar.)*

14. **Reversión de propuestas:** Un supervisor puede revertir asignaciones que aún estén en estado 'Pendiente'. La reversión siempre actúa sobre **la propuesta más reciente** realizada en su área; si se revierte nuevamente, actúa sobre la anterior, y así sucesivamente. Revertir debe devolver al trabajador las horas descontadas y liberar el cupo en la franja correspondiente. Una asignación ya 'Aprobada' no puede revertirse: si la propuesta más reciente está aprobada, el sistema debe informarlo y no revertir ninguna otra. *(Estructura prevista: cola LIFO/pila. Pendiente de implementar.)*

15. **Brecha de capacidades:** Cuando un trabajador resulta inapto para una labor (reglas 4 y 10), el sistema debe informar **exactamente qué habilidades y qué credenciales le faltan**, sin repeticiones. Además, debe permitir consultar qué habilidades tienen en común dos trabajadores y cuáles posee uno pero no el otro. Registrar dos veces la misma habilidad en un trabajador no debe alterar su repertorio. **(Implementado — ver abajo.)**

16. **Ocupación por momento y lugar:** El sistema debe responder de forma inmediata, sin recorrer todas las asignaciones, cuántas personas hay asignadas para una combinación determinada de fecha, franja horaria y área de trabajo. Una vez registrada, la combinación que identifica ese momento y lugar no debe poder alterarse por error desde otra parte del código. **(Implementado — ver abajo.)**

17. **Agenda personal del trabajador:** Cada trabajador mantiene su agenda de asignaciones **siempre ordenada cronológicamente** (por fecha y franja). Las asignaciones no llegan en orden: es habitual que se agregue una labor anterior a otras ya agendadas, o que se revierta una del medio de la agenda. Estas inserciones y bajas intermedias no deben requerir reordenar ni desplazar el resto de la agenda. La agenda solo se consulta recorriéndola desde la asignación más próxima hacia las posteriores. **(Implementado — ver abajo.)**

18. **Bitácora de auditoría:** Toda propuesta, aprobación y reversión debe dejar un registro con fecha y hora, tipo de acción, labor y trabajador involucrados. Los registros de la bitácora son definitivos: una vez creados, ningún campo puede modificarse. **(Implementado — ver abajo.)**

### Requisitos de la Extensión

- La resolución de esta extensión debe emplear **al menos cuatro estructuras de datos de naturaleza distinta**, elegidas según el comportamiento que exige cada regla. Para las estructuras que no son nativas de Python, se usan las implementaciones desarrolladas en la cátedra.
- Por cada regla nueva corresponde **justificar por escrito** qué estructura se eligió y por qué es más adecuada que las alternativas (considerando el orden de acceso, la unicidad, la mutabilidad y el costo de las operaciones frecuentes).
- Actualizar el diagrama de flujo con los nuevos circuitos (espera de urgencias y reversión).

### Pruebas mínimas esperadas

- Tres labores urgentes sin personal; al liberarse capacidad para la segunda pero no para la primera, ninguna se cubre fuera de orden.
- Tres propuestas seguidas y tres reversiones: se revierten en el orden inverso y las horas y cupos vuelven exactamente a su valor inicial.
- Intento de reversión cuando la propuesta más reciente está aprobada.
- Brecha de capacidades con faltantes de la labor y del área a la vez, sin elementos repetidos.
- Ocupación consultada antes y después de asignar y de revertir.
- Inserción de una asignación anterior a las ya agendadas y baja de una intermedia, verificando el orden resultante.
- Intento de modificar un registro de la bitácora.

### Qué se implementó de esta extensión (reglas 15, 16, 17 y 18)

**Regla 15 — Brecha de capacidades (`set`):** en `Trabajador` (`trabajador.py`), el repertorio de habilidades se mantiene deduplicado mediante un `set` interno de nombres (`repertorio_habilidades`): registrar dos veces la misma habilidad no altera el repertorio (`agregar_habilidad`, y también el constructor y `set_habilidades`). `obtener_habilidades_faltantes` y `obtener_credenciales_faltantes` devuelven `set`s con lo que falta, sin repetidos. `Asignacion.evaluar_aptitud` evalúa habilidades y credenciales (de la labor y del área) **juntas** y, si falla, levanta un único `TrabajadorNoAptoError` que trae la brecha completa (unión, sin duplicados) en `habilidades_faltantes` y `credenciales_faltantes`. Además, `habilidades_en_comun` y `habilidades_exclusivas` permiten comparar el repertorio de dos trabajadores usando intersección y diferencia de conjuntos.

*Por qué un `set` y no una lista:* la pregunta de negocio es siempre "¿tiene esta habilidad o no?", nunca "¿en qué posición está?" — no hay orden que preservar. Un `set` resuelve la membresía y la deduplicación en O(1) amortizado, y las operaciones de brecha/comparación (unión, intersección, diferencia) son directamente las operaciones nativas del tipo, en lugar de tener que escribir bucles manuales para evitar repetidos como exigiría una lista.

**Regla 16 — Ocupación por momento y lugar (`dict` + tupla como clave):** `Sistema` mantiene `ocupacion`, un diccionario que mapea una clave `(fecha, franja, area)` (una tupla comun, inmutable) a la cantidad de personas asignadas. `contar_ocupacion(fecha, franja, area)` responde en O(1) sin recorrer `asignaciones`. El contador se incrementa en el mismo punto donde se crea cada propuesta (`procesar_solicitudes_pendientes`, `generar_sugerencias`, `Supervisor.asignar_trabajador`) y se decrementa al revertir (`Sistema.revertir_asignacion`).

*Por qué un `dict` con clave tupla:* se necesita acceso directo por clave compuesta sin recorrer nada, que es exactamente lo que ofrece un diccionario (hashing en O(1)) frente a recorrer una lista de asignaciones en O(n). Se usa una tupla simple (no una clase propia) porque sus campos no se pueden reasignar una vez creada: así la combinación fecha+franja+área que identifica ese "momento y lugar" queda protegida de una modificación accidental desde cualquier otra parte del código, cosa que una clase mutable no garantizaría.

**Regla 17 — Agenda personal del trabajador (lista enlazada + recursión):** cada `Trabajador` tiene su propia `Agenda` (`agenda.py`), una lista enlazada simple (reutiliza la misma clase `Nodo` de `Cola`, en `nodo.py`) que mantiene sus asignaciones ordenadas por fecha y franja. `Agenda.agregar`/`Agenda.eliminar` son **recursivas**: en cada llamada comparan contra el nodo actual (caso base: encontré el lugar o se acabó la cadena) o siguen con el resto de la lista (caso recursivo, un nodo más adelante — eso da el progreso). `Trabajador.agregar_a_agenda`/`sacar_de_agenda` se llaman automáticamente desde `Asignacion` (al crearse, al rechazar, al reasignar), así que la agenda nunca se arma a mano.

*Por qué una lista enlazada y no una lista de Python:* la cátedra lo deja explícito en la comparación de la Clase 7 — buscar es `O(n)` en ambas estructuras por igual, no hay ventaja ahí. La ventaja real es insertar: en una lista de Python insertar en el medio reorganiza/desplaza el resto; en una lista enlazada "solo cambia referencias". Como las asignaciones no llegan en orden (se puede agregar o revertir una del medio en cualquier momento), insertar/eliminar sin desplazar nada es exactamente el problema que hay que resolver.

*Por qué recursión para insertar/eliminar y no para recorrer:* la Clase 10 es explícita en que la recursión conviene cuando el problema se resuelve con una versión más chica de sí mismo, y que un `for`/`while` es mejor para un recorrido lineal directo. Insertar en el lugar correcto de una cadena enlazada es naturalmente eso: "si el lugar es acá, inserto; si no, resuelvo el mismo problema sobre el resto de la cadena" — por eso `recorrer()` se dejó con un `while` simple (no gana nada volviéndolo recursivo) y `insertar_despues`/`eliminar_desde` sí son recursivas.

**Regla 18 — Bitácora de auditoría (`tupla`):** `Sistema` mantiene `bitacora`, una lista donde cada entrada es una **tupla** `(fecha_hora, tipo_accion, labor, trabajador)` creada con `registrar_en_bitacora`. Se registra una entrada en cada propuesta (creación de una `Asignacion`), cada aprobación (`Sistema.aprobar_asignacion`) y cada reversión (`Sistema.revertir_asignacion`). `obtener_bitacora()` devuelve una tupla de tuplas (no la lista interna), así que ni los registros ni la colección que se expone hacia afuera pueden alterarse. A diferencia de `ocupacion` y `asignaciones`, la bitácora **no se reinicia** en `ciclo_semanal`: es un historial permanente.

*Por qué una tupla y no una lista o un diccionario:* cada registro es un hecho que ya ocurrió y que por consigna debe ser "definitivo". Una tupla no tiene métodos para modificar sus campos una vez creada (`registro[1] = ...` lanza `TypeError`), a diferencia de una lista, que sí permite `append`/`__setitem__`. No se eligió un diccionario porque el orden de los cuatro campos es fijo y conocido de antemano (no hace falta buscar por clave), así que una tupla es la estructura más simple y liviana que ya impone, por construcción, la inmutabilidad que pide la regla.

