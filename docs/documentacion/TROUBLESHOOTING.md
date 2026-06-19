# Troubleshooting de stark

Soluciones a los problemas más comunes durante el uso de stark, agrupadas en generales (los tres flujos de construcción) y específicas de mantenimiento. Para el camino feliz ve a [QUICKSTART.md](QUICKSTART.md); para el detalle exhaustivo, [REFERENCIA.md](REFERENCIA.md).

---

## General (los tres flujos de construcción)

### "Los subagentes no aparecen al ejecutar `/agents`"

**Posibles causas:**

- **Path incorrecto:** la carpeta `.claude/agents/` debe estar en la raíz del repo donde abres Claude Code, no anidada.
- **Frontmatter roto:** abre cada `.md` de los agentes y verifica que el YAML al inicio (entre `---` y `---`) esté bien formado. Errores comunes: comillas mal cerradas, indentación inconsistente.
- **Nombres con mismatch:** el campo `name:` dentro del YAML debe coincidir con el nombre del archivo (sin la extensión `.md`). Si renombraste un archivo, también renombra el `name:`.
- **Versión de Claude Code muy vieja:** actualiza con `claude update`.

### "El agente no aplica las reglas del SKILL"

**Posibles causas:**

- Tu versión de Claude Code no soporta el campo `skills:` en subagents (feature relativamente reciente).
  - **Solución rápida:** edita el system prompt del subagente y agrega al inicio del cuerpo: `Antes de cualquier acción, lee .claude/skills/<nombre>/SKILL.md y aplica sus reglas estrictamente.`
- **Path incorrecto:** el SKILL debe estar en `.claude/skills/<nombre>/SKILL.md` (carpeta con el mismo nombre que el `name:` del SKILL).

### "El agente quiere inventar en lugar de preguntar"

Esto pasa cuando:

- El system prompt no se cargó bien (verifica el frontmatter del subagente).
- El modelo configurado es muy chico (los subagentes están en `model: opus` por defecto — si cambiaste a sonnet o haiku, vuelve a Opus).
- El material que cargaste en `docs/inputs/` es muy parco — si tienes poco contexto, el agente tiene poco con qué identificar huecos.

**Mitigación inmediata:** dile explícitamente "no rellenes huecos, hazme preguntas numeradas sobre cualquier ambigüedad".

### "El `requirements.md` me quedó enorme (100+ Requirements)"

El feature es demasiado grande. Pártelo:

1. Identifica subdominios funcionales (ej. "autenticación", "cálculo de impuestos", "exportación de reportes").
2. Crea un repo o sub-feature por cada uno, con su propio `requirements.md` / `design.md` / `tasks.md`.
3. Documenta las dependencias entre sub-features en un archivo raíz.

**Heurística:** si tu `requirements.md` pasa de 30–40 Requirements, ya es demasiado para un solo ciclo.

### "Hay contradicciones entre `requirements` y `design`"

Probablemente cambiaron requirements después de aprobar design (o viceversa) y no se sincronizó. Solución:

1. Vuelve a la fase que cambió primero.
2. Vuelve a ejecutar la siguiente fase con el cambio.
3. No edites manualmente `design.md` sin volver a validar contra `requirements.md`.

**Anti-patrón:** tratar de "remendar" el `design.md` a mano para que cuadre con el nuevo requirement. Casi siempre rompe la trazabilidad.

### "El agente marca una tarea como `[x]` pero el código no funciona"

Esto es el modo de falla más común de SDD. Causas:

- La tarea no tenía "Criterio de hecho" suficientemente concreto.
- El agente se auto-validó optimista (los agentes implementadores siempre son optimistas sobre su trabajo).

**Mitigación:**

- Antes de marcar `[x]`, corre tú los tests específicos de la tarea.
- Verifica manualmente que se cumple el criterio EARS referenciado en el footer.
- Si vas a aceptar `[x]` solo por la declaración del agente, mínimo lee el diff completo del código que generó.

**Solución estructural:** en el siguiente ciclo, considera meter un subagente verificador independiente (no incluido en este framework v1) que revise el output con goal opuesto: encontrar fallas, no completar.

### "El agente entró en loop preguntándome cosas que ya respondí"

Pasa cuando:

- Cerraste y reabriste Claude Code (perdió contexto de la sesión).
- La conversación se volvió muy larga (>50 turns) y el agente está perdiendo coherencia.

**Solución:**

1. Termina lo que estés haciendo con un buen estado del archivo (requirements.md guardado).
2. Abre conversación nueva.
3. Invoca al subagente diciéndole: "lee docs/requirements.md actual y continúa desde el Requirement N en adelante".

---

## Mantenimiento

### "El agente `analista-feature-mantenimiento` me dice que el feature requiere cambiar arquitectura"

Esto **NO** es un bug — es por diseño. El agente detectó que tu feature no se puede meter sin tocar arquitectura existente (ej. cambiar el stack, reemplazar un módulo entero, romper compatibilidad hacia atrás).

**Opciones:**

1. **Reescritura previa del módulo afectado:** salir del pipeline de mantenimiento, hacer un ciclo SDD completo de brownfield-rewrite para ese módulo, después volver a mantenimiento para el feature.
2. **Reducir el scope del feature:** limitar lo que el feature hace para evitar el cambio arquitectónico.
3. **Aceptar el cambio arquitectónico** y documentarlo con un ADR especial en el `design.md` delta marcado como alerta crítica.

El framework no decide por ti — **te obliga a hacer la decisión explícita.**

### "`requirements.md` de mantenimiento me quedó documentando todo el sistema en vez del delta"

Pasa cuando:

- El `intent.md` está demasiado vago y el agente intenta inferir todo del código.
- Falta el sustrato (`CLAUDE.md`, `BIG_PICTURE.md`) y el agente intenta reconstruirlo.

**Solución:**

1. Mejora el `intent.md`: agrega más contexto sobre **QUÉ específicamente** cambia y **QUÉ NO**.
2. Si falta sustrato, pausa y corre `onboarding` y `reglas-negocio` antes de continuar.
3. Vuelve a invocar al agente diciendo: "el scope es solo el delta — Surface of Contact ≤ N módulos, no documentar el sistema completo".

### "Las invariantes que detectó el agente son demasiado vagas"

Pasa cuando:

- El sustrato `REGLAS_DE_NEGOCIO.md` no existe o está incompleto.
- El código tiene comportamientos críticos sin tests que los documenten.

**Solución:**

- Pídele al agente que referencie código para cada invariante (`<!-- source: archivo:líneas -->`). Sin fuente, no es invariante.
- Si una invariante no se puede traducir a un test concreto, descártala — no era invariante real, era deseo.
- Si descubres comportamientos críticos sin test durante este análisis, ese gap se llena con tareas de Blindar en el `tasks.md`. Es valioso descubrirlo aquí, no en producción.

### "El `design` delta propone tocar cosas fuera de Surface of Contact"

El agente debería detectarlo en su Fase 5 (Validación de no-invasión), pero si se le escapó:

**Solución:**

- Vuelve al humano: ¿el componente extra **sí** se debería tocar (entonces actualizar Surface of Contact del requirements — válvula de retorno al analista) o **no** se debería tocar (entonces quitar del design)?
- **NO permitas que el design crezca silenciosamente.** Cada componente fuera de Surface of Contact es un riesgo no autorizado.

### "El `tasks.md` me ordenó por capas en vez de por riesgo"

El agente correcto para mantenimiento es `descompositor-riesgo-mantenimiento`, **NO** `descompositor-tareas`. Si invocaste el equivocado, el output sale en formato de construcción (Setup → Data Model → ...) en vez de riesgo (Regression Shield → ... → No-Regression Validation).

**Solución:**

1. Borra el `tasks.md` generado.
2. Vuelve a invocar con `descompositor-riesgo-mantenimiento`.
3. Verifica que el agente detecta el contexto de mantenimiento (lee Surface of Contact + Invariantes del requirements).

### "Tarea de modificación marca `[x]` pero el módulo modificado tiene tests rotos"

Esto significa que el agente codificador rompió código existente sin que tú lo notaras. Es exactamente lo que mantenimiento debe prevenir.

**Solución estructural:**

- Antes de marcar `[x]` en cualquier tarea de Modificar, siempre ejecuta los tests del módulo modificado.
- Si el agente declara "tests pasan" sin haberlos corrido, no le creas. Verifica tú.
- Si descubres regresión tarde, revierte el commit de esa tarea y vuelve a hacerla con más cuidado (probablemente faltaba un test de blindaje que no se escribió).

### "Corrí No-Regression Validation y descubrí que una invariante se rompió"

**No cierres el feature.** Detente y diagnostica:

1. ¿Qué tarea(s) tocaron el módulo donde se rompió la invariante?
2. ¿Esas tareas tenían footer `_Invariants: I.X_` correctamente?
3. ¿Existía un test de blindaje (Blindar I.X) que debió detectar el problema antes? ¿pasó cuando se escribió?

**Si el test de blindaje sigue verde pero la invariante está rota** → el test estaba mal escrito. Corrige el test, después corrige el código.

**Si el test de blindaje está roto** → el código rompió lo que el blindaje protegía. Corrige el código.

El gate final está ahí para atrapar exactamente esto. Si saltó la alarma, hizo su trabajo. Ahora el tuyo es resolverlo antes de cerrar.
