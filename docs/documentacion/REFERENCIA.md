# Referencia de stark

> **Referencia detallada por fase. Para el camino feliz, ve a [`QUICKSTART.md`](QUICKSTART.md).**

Detalle exhaustivo de cada fase: qué esperar del agente, cómo validar su output, y el patrón de ejecución del código. No es un tutorial lineal — para eso está [`QUICKSTART.md`](QUICKSTART.md). ¿Algo se trabó? → [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md). ¿Por qué el framework decide lo que decide? → [`PRINCIPIOS.md`](PRINCIPIOS.md) y [`DECISIONES.md`](DECISIONES.md).

Vocabulario de casos de uso: **nuevo** (greenfield), **reingeniería** (brownfield-rewrite), **mantenimiento** y **prototipo**.

---

## Índice

1. [Fase 1: Init / elegir caso de uso](#1-fase-1-init--elegir-caso-de-uso)
2. [Fase 2: Requirements (levantamiento)](#2-fase-2-requirements-levantamiento)
3. [Fase 3: Prototipo visual (opcional)](#3-fase-3-prototipo-visual-opcional)
4. [Fase 4: Design (diseño técnico)](#4-fase-4-design-diseño-técnico)
5. [Fase 5: Tasks (descomposición)](#5-fase-5-tasks-descomposición)
6. [Fase 6: Build / Ejecución del código](#6-fase-6-build--ejecución-del-código)
7. [Glosario](#7-glosario)

### Tiempo estimado por fase

| Tarea | Tiempo |
|-------|--------|
| Setup inicial del repo | 5–10 minutos |
| Requirements | 30–90 minutos |
| Design | 45–90 minutos |
| Tasks | 20–45 minutos |
| Build (código) | Depende del feature; una tarea = 15–45 min en sesión |

No es rápido. Es predecible. Esa es la diferencia con vibe-coding.

---

## 1. Fase 1: Init / elegir caso de uso

Antes de invocar cualquier agente, decides en qué caso de uso vives. Esto se hace una vez por proyecto (o una vez por feature en mantenimiento). El detalle de instalación según caso está en [`QUICKSTART.md`](QUICKSTART.md); aquí solo el árbol de decisión para los casos límite.

| Tu situación | Caso de uso | Agente inicial |
|--|--|--|
| Cliente nuevo, idea nueva, tienes entrevistas/transcripciones/formularios. | Nuevo (greenfield) | `analista-entrevistas` |
| Sistema legacy roto/anticuado que vas a rehacer. Tienes acceso al código + análisis previo. | Reingeniería | `arqueologo-codigo` |
| Sistema en producción que funciona. Quieres agregar algo sin romper. | Mantenimiento | `analista-feature-mantenimiento` |

### Casos límite

Árbol de decisión: ¿tienes un sistema en producción? **NO** → **nuevo** (inputs: entrevistas, formularios, imágenes). **SÍ** → ¿reescribir arquitectura completa, o solo agregar feature? Reescribir → **reingeniería** (inputs: arqueología previa + código legacy). Agregar → **mantenimiento** (inputs: intent del feature + código en prod; sustrato en §2).

Los dos casos que confunden:

| Tu situación | Resolución |
|--|--|
| Sistema legacy pero el feature nuevo no existe en él (mitad y mitad) | Decide caso por caso: si vas a redescribir el sistema viejo + agregar nuevo, reingeniería + nuevo (dos `requirements.md`). Si vas a respetar el viejo y solo agregar, mantenimiento. |
| Sistema en producción + el feature requiere rehacer arquitectura | NO es mantenimiento. Es reingeniería parcial del módulo afectado primero, después feature de mantenimiento. |

**Instalación del framework en mantenimiento:** NO creas un repo nuevo — el framework se agrega encima del repo legacy (`.claude/`, `templates/`, `docs/documentacion/`, `docs/features/`). El paso a paso está en [`QUICKSTART.md`](QUICKSTART.md). ⚠️ Si el repo legacy ya tiene `.claude/` propio o `CLAUDE.md` en raíz, aborta y resuelve caso por caso (renombrar, fusionar manual, o preguntar al cliente).

---

## 2. Fase 2: Requirements (levantamiento)

Esta fase produce el `requirements.md` correspondiente a tu caso. Tres caminos:

| Caso de uso | Subagente | Output |
|--|--|--|
| Nuevo | `analista-entrevistas` | `docs/requirements.md` (sistema completo) |
| Reingeniería | `arqueologo-codigo` | `docs/requirements.md` (sistema completo, descrito desde código) |
| Mantenimiento | `analista-feature-mantenimiento` | `docs/features/<slug>/requirements.md` (delta del feature) |

### 2A. Nuevo — usando `analista-entrevistas`

Mete en `docs/inputs/` todo lo que tengas (transcripciones, screenshots, fotos de diagramas, PDFs, notas); el agente lee todo. Invocación:

```
Use the analista-entrevistas subagent to produce docs/requirements.md
from the material in docs/inputs/
```

#### Qué esperar

El agente va a ejecutar 5 fases internamente. Tu trabajo es responder cuando pregunte.

| Fase del agente | Qué hace | Tu trabajo |
|--|--|--|
| 1. Inventario | Lista todos los archivos que encontró, te resume qué leyó. | Confirmar que su lectura inicial es correcta. Si malinterpretó algo, corrígelo ahora. |
| 2. Identificación de huecos | Te entrega preguntas numeradas sobre cosas ambiguas, casos borde no cubiertos, actores no definidos, restricciones no funcionales ausentes. | Responder **TODAS** las preguntas por número. No le dejes rellenar con suposiciones. |
| 3. Síntesis incremental | Genera el `requirements.md` sección por sección y te lo muestra. | Revisar cada Requirement N y decir si captura lo levantado o si falta/sobra algo. |
| 4. Auto-validación | Ejecuta el checklist del SKILL contra el archivo. Te reporta cada ítem como ✅ o ❌. | Esperar a que llegue a 100% ✅. |
| 5. Cierre | Declara "listo para revisión final". | Hacer tú la revisión manual y aprobar (o pedir cambios). |

#### Cómo validar el output

Antes de aprobar, verifica manualmente:

- [ ] Cada `### Requirement N` tiene una **User Story:** en español con la fórmula completa "Como X, quiero Y, para Z".
- [ ] Cada Requirement tiene al menos un criterio EARS en inglés.
- [ ] Los criterios usan **SOLO** `SHALL` (nunca `should`, `would`, `may`).
- [ ] No hay implementación (frameworks, librerías, bases de datos específicas) — eso va en design, no aquí.
- [ ] Existe la sección `## Out of Scope` con cosas explícitas que NO se van a hacer.
- [ ] Tú puedes leer el documento de corrido y entender qué hay que construir.

Si todo eso está, di explícitamente algo como **"aprobado, sigue con design"**. Si no, pide los cambios específicos y el agente itera.

### 2B. Reingeniería — usando `arqueologo-codigo`

Mete en `docs/analysis/` tus `.md` de análisis arqueológico previo. Asegúrate de que el código legacy esté accesible. Invocación:

```
Use the arqueologo-codigo subagent to produce docs/requirements.md
from the analysis in docs/analysis/ and the legacy code in [ruta_al_código]
```

#### Qué esperar

Similar al analista, pero el agente clasifica cada comportamiento en una categoría:

- **feature intencional** (alta confianza, va al `requirements.md`)
- **probable feature** (media confianza, va con anotación)
- **probable bug** (NO va al requirements, va a sección Detected Anomalies para que tú decidas)
- **ambiguo** (te pregunta antes de clasificar)

Cada criterio derivado de código lleva un comentario de trazabilidad:

```
1. WHEN the user clicks "Calcular" THE SYSTEM SHALL recalculate all fields.
   <!-- confidence: high; source: src/forms/calc.js:142-178 -->
```

Además de la estructura normal, este `requirements.md` tendrá secciones extras: `## Detected Anomalies` (cosas que parecen bug, tú decides si se preservan o corrigen), `## Open Questions` (lo que ni el agente ni tú resolvieron al momento) y `## Coverage Map` (tabla "módulo legacy → Requirement que lo cubre", para detectar código huérfano o requirements sin código).

#### Cómo validar

Mismo checklist que nuevo, **MÁS:**

- [ ] Cada criterio derivado de código tiene su `<!-- confidence: X; source: Y -->`.
- [ ] No quedan criterios con confianza `low` sin resolución (o se promovieron, o se movieron a `Open Questions`).
- [ ] La sección `## Detected Anomalies` tiene contenido si se detectaron cosas raras.
- [ ] La sección `## Coverage Map` está completa.

### 2C. Mantenimiento — usando `analista-feature-mantenimiento`

Pipeline para agregar un feature a un sistema en producción sin romper lo que ya funciona.

#### Pre-requisito recomendado: generar el sustrato

Antes del primer feature, una sola vez por repo, corre estas dos skills desde Claude Code:

```
/onboarding         → genera docs/CLAUDE.md y docs/BIG_PICTURE.md
/reglas-negocio     → genera docs/REGLAS_DE_NEGOCIO.md
```

Los tres archivos viven en `docs/` raíz (no dentro de `features/`) porque aplican a todo el sistema. El agente de mantenimiento los lee como contexto base. **Si no los generas:** el pipeline funciona igual, pero el agente infiere más del código y aumenta la probabilidad de perder invariantes. Inversión: 5–10 minutos cada skill, una vez por sistema.

#### Preparar el feature

Define un slug (kebab-case: `exportar-reportes-pdf`, `auth-mfa`), crea `docs/features/<slug>/`, copia `templates/intent.md` dentro y rellénalo. Secciones del template: **Qué queremos**, **Por qué**, **Quién pidió**, **En qué área del sistema vive** (intuición inicial), **Out of scope explícito**, **Pistas técnicas conocidas** (opcional), **Stakeholder técnico**, **Fecha / urgencia**. Escríbelo en prosa libre — es un input para el agente, no un documento formal; él lo refina y formaliza después. Invocación:

```
Use the analista-feature-mantenimiento subagent to produce
docs/features/<slug>/requirements.md from the intent at
docs/features/<slug>/intent.md and the production code in this repo
```

#### Qué esperar

El agente va a ejecutar 7 fases internamente. Tu trabajo es responder cuando pregunte.

| Fase del agente | Qué hace | Tu trabajo |
|--|--|--|
| 1. Lectura del intent + sustrato | Lee `intent.md`, `docs/CLAUDE.md`, `docs/BIG_PICTURE.md`, `docs/REGLAS_DE_NEGOCIO.md` (si existen), mapea estructura del código. Reporta qué encontró. | Confirmar la lectura inicial. Si malinterpretó algo, corrígelo. Si falta sustrato, el agente te avisa — decide si pausas para correrlo o continúas. |
| 2. Triangulación intent ↔ código | Para cada capacidad del intent, localiza módulos relacionados en el código y mapea Surface of Contact (qué módulos toca el feature, lee, modifica, o NO toca). | Validar el mapa preliminar. |
| 3. Identificación de invariantes | Infiere invariantes preservadas (comportamientos del sistema que NO deben cambiar) con referencias al código. Te las presenta numeradas (I.1, I.2, ...). | Confirmar o descartar cada invariante numerada. Mejor sobre-listar y descartar que omitir. |
| 4. Resolución de huecos | Preguntas numeradas sobre actores, casos borde, NFR del feature, out-of-scope, términos ambiguos. | Responder **TODAS** las preguntas por número. |
| 5. Síntesis incremental | Genera el `requirements.md` sección por sección y te lo muestra. | Revisar cada sección. Surface of Contact e Invariantes Preservadas son las más críticas. |
| 6. Auto-validación | Ejecuta el checklist del SKILL contra el archivo. Reporta ✅ / ❌. | Esperar a 100% ✅. |
| 7. Cierre | Declara "listo para revisión final". | Hacer tú la revisión manual y aprobar (o pedir cambios). |

#### Cómo validar el output

El `requirements.md` de mantenimiento es distinto del de nuevo. Verifica:

- [ ] Existe sección `## Contexto` con qué/por qué/quién/dónde vive el feature.
- [ ] Existe sección `## Surface of Contact` con tabla rellena. Cada fila lista un módulo/archivo/endpoint/tabla que el feature toca, lee, o explícitamente NO toca, con su nivel de riesgo.
- [ ] Existe sección `## Invariantes Preservadas` con mínimo una invariante numerada **I.N**, cada una con comentario `<!-- source: archivo:líneas -->`.
- [ ] Existe sección `## Tests Existentes a Preservar` con tabla que indica qué tests cubren cada invariante (y cuáles son gaps sin test).
- [ ] Existe sección `## Requirements` (del delta) con al menos un `### Requirement N` que describe solo el feature nuevo, no el sistema.
- [ ] Cada Requirement con **User Story:** "Como X, quiero Y, para Z". en español.
- [ ] Acceptance Criteria en inglés con `SHALL` únicamente.
- [ ] Existe sección `## Out of Scope` (del feature) explícita.
- [ ] El requirements **NO** documenta el sistema completo — solo el delta.
- [ ] El requirements **NO** propone reescribir arquitectura existente. Si lo hace, pausa: probablemente el caso correcto es reingeniería, no mantenimiento.

Si todo está, di explícitamente **"aprobado, sigue con design"** (o pasa a la fase opcional de prototipo si el feature tiene UI nueva).

#### Caso especial: el feature requiere cambiar arquitectura

Si descubres que el feature no se puede meter sin tocar arquitectura existente (ej. necesitas Redis y el sistema no lo tenía, o el feature implica rehacer el módulo de auth), el agente te lo señala como **alerta crítica**. Opciones:

1. **Salir del pipeline de mantenimiento** y planear una reingeniería del módulo afectado antes del feature. Después, volver a mantenimiento para el feature.
2. **Reducir scope del feature** para evitar el cambio arquitectónico.
3. **Aceptar el cambio arquitectónico** y documentarlo explícitamente con un ADR especial en el design (eso ya es mantenimiento con riesgo elevado — el humano decide).

El framework no te obliga a una opción — **te obliga a hacer explícita la decisión.**

---

## 3. Fase 3: Prototipo visual (opcional)

Opcional y transversal a los tres casos. Aplica cuando el proyecto o feature tiene UI relevante y quieres validar visualmente con el cliente antes de pasar a diseño técnico. Si es backend puro, CLI o librería, sáltala.

### Pre-requisito

- **Nuevo / reingeniería:** `docs/requirements.md` aprobado por ti.
- **Mantenimiento:** `docs/features/<slug>/requirements.md` aprobado por ti, y el feature introduce UI nueva o cambios visuales que el cliente quiere validar.

### Diferencia de path según caso

| Caso de uso | Carpeta del prototipo |
|--|--|
| Nuevo / reingeniería | `docs/prototype/` |
| Mantenimiento | `docs/features/<slug>/prototype/` |

El agente `prototipador-visual` detecta automáticamente cuál usar leyendo qué `requirements.md` está aprobado. Si dudas, pasa el path explícitamente en la invocación.

### ¿Cuándo usarla?

| Tu situación | ¿Invocar prototipo? |
|--|--|
| Proyecto con UI, cliente no-técnico que necesita "ver para creer" | Sí |
| Proyecto con UI, pero el flujo es tan simple que con requirements queda claro | Probablemente no |
| Backend puro, CLI, librería sin frontend | No |

**La regla práctica:** si sospechas que el cliente va a decir "no, así no" cuando vea la UI final, vale la pena invertir en esta fase. Es 100x más barato cambiar un HTML throwaway que código de producción.

### Preparar el material (opcional pero recomendado)

Crea `docs/prototype/context/` y mete lo que tengas: `branding.md` (colores, tipografía, tono), `logos/` (PNG, SVG), `referencias/` (screenshots de competidores, inspiración). Si no tienes nada, el agente genera con placeholders genéricos en la primera iteración (colores neutros, logo `[LOGO]` en cuadro gris, tipografía del sistema). El branding se incorpora en iteraciones posteriores. Invocación:

```
Use the prototipador-visual subagent to produce docs/prototype/
```

### Qué esperar (iteración 1)

| Fase del agente | Qué hace | Tu trabajo |
|--|--|--|
| 1. Lectura | Lee `requirements.md`, `context/` y `CONSTITUTION.md` (si existe). Reporta: cantidad de requirements, pantallas inferidas, estado del branding, plataforma de despliegue. | Confirmar que su lectura es correcta. |
| 2. Plataforma | Te pregunta dónde desplegar (Railway default, Netlify, Vercel, Cloudflare Pages, GitHub Pages, manual). Solo pregunta si no está en `CONSTITUTION.md`. | Elegir con un número. |
| 3. Inventario de pantallas | Lista las pantallas que va a generar, para qué Requirement aplica cada una, y qué interacciones serán simuladas vs. estáticas. | Aprobar el plan o ajustar. |
| 4. Generación | Genera `docs/prototype/` completo: HTML + Tailwind CDN, banner permanente "MOCKUP NO FUNCIONAL", datos falsos, `server.js` con basic auth, `DEPLOY.md`, y `validation-log-v1.md` vacío. | Revisar los archivos generados. |
| 5. Auto-validación | Ejecuta checklist del SKILL ítem por ítem. Reporta ✅ o ❌. | Esperar 100% ✅. |
| 6. Cierre | Te dice que despliegues manualmente con las instrucciones de `DEPLOY.md`. | Desplegar, mostrar al cliente. |

**Importante:** el agente **NO** hace `git push` ni despliega por su cuenta. Tú controlas qué se publica. Si quieres que él haga push, díselo explícitamente en la sesión.

### Despliegue (tú lo haces)

Sigue las instrucciones de `docs/prototype/DEPLOY.md`. Flujo típico con Railway: **setup (una vez)** — crear proyecto, conectar repo, root directory `docs/prototype/`, env vars `AUTH_USER` y `AUTH_PASS`; **redeploy (cada iteración)** — `git add docs/prototype/ && git commit && git push`, Railway redespliega solo.

### El loop iterativo con el cliente

Se repite hasta que el cliente apruebe:

1. Le muestras al cliente la URL desplegada con las credenciales.
2. El cliente da feedback (verbal, por Slack, Loom, lo que sea).
3. Tú transcribes el feedback en `docs/prototype/validation-log-v1.md`:
   - **Cambios cosméticos** → lo que el agente puede iterar en HTML (color, posición, texto).
   - **Cambios estructurales** → cosas que implican requirements nuevos (rol nuevo, entidad nueva, flujo nuevo).
   - **Preguntas sin resolver** → dudas que quedaron abiertas.
4. Decisión: marcas si está aprobado, si necesita otra iteración, o si hay que volver al analista.
5. Invocas al agente de nuevo:
   ```
   Use the prototipador-visual subagent to iterate on docs/prototype/
   based on validation-log-v1.md
   ```
6. El agente genera v2, tú despliegas, muestras, transcribes, repites.

#### Cambios estructurales: la válvula de retorno

Si el cliente pide algo que no está en requirements (un actor nuevo, una entidad nueva, un flujo completo nuevo, una integración externa), el agente se detiene. No intenta resolverlo en HTML — eso rompería la trazabilidad EARS. El flujo es:

1. El agente te avisa: "Esto es un cambio estructural, necesita pasar por analista-entrevistas."
2. Tú invocas al `analista-entrevistas` para actualizar `requirements.md`.
3. Apruebas el requirements actualizado (gate humano normal).
4. Vuelves a invocar al `prototipador-visual` con el contexto enriquecido.

### Cuándo cerrar el loop

Cuando el cliente aprueba explícitamente:

- En el último `validation-log-v{N}.md`, marca `Status: APROBADO` con fecha.
- Commit final con tag `prototype-approved-v{N}`.

Sin esa aprobación explícita, **no avances a Fase 4 (design).**

### Cómo validar antes de mostrar al cliente

Antes de cada despliegue, verifica:

- [ ] Todas las pantallas tienen el banner fijo amarillo "MOCKUP NO FUNCIONAL" (no removible).
- [ ] Los datos visibles son obviamente falsos ("Cliente Demo", "$1,234.56", "usuario@ejemplo.com").
- [ ] El HTML usa solo Tailwind CDN + JS vanilla — no hay React, Vue ni nada con build.
- [ ] `DEPLOY.md` tiene instrucciones claras y NO contiene credenciales reales.
- [ ] Los clicks navegan entre pantallas pero no ejecutan lógica de negocio real.
- [ ] Si hubo cambios estructurales, se canalizaron al analista-entrevistas antes de iterar.

### Heurísticas importantes

- **Iteración 1 no necesita branding.** Valida estructura y flujo, no pulido visual.
- **Si llegas a la iteración 4–5** y el cliente sigue pidiendo cambios estructurales, el problema está en `requirements.md`. Vuelve al analista para una pasada completa.
- **El prototipo NO decide el stack.** Que esté en HTML+Tailwind no significa que el sistema final lo será. Eso lo decide `design.md`.
- **El prototipo es throwaway.** No se reutiliza como código de producción.

Si el cliente aprobó el prototipo, di explícitamente **"aprobado, sigue con design"** y pasa a la [Fase 4](#4-fase-4-design-diseño-técnico).

---

## 4. Fase 4: Design (diseño técnico)

Distinto agente según caso. Asegúrate de invocar el correcto.

| Caso de uso | Subagente | Output |
|--|--|--|
| Nuevo / reingeniería | `disenador-arquitecto` | `docs/design.md` |
| Mantenimiento | `disenador-delta-mantenimiento` | `docs/features/<slug>/design.md` |

### Pre-requisito

- **Nuevo / reingeniería:** `docs/requirements.md` aprobado por ti.
- **Mantenimiento:** `docs/features/<slug>/requirements.md` aprobado por ti.

### (Opcional pero recomendado) Crea un `CONSTITUTION.md`

Antes de invocar al diseñador, si tienes decisiones técnicas estándar del proyecto o del cliente (stack obligatorio, patrones, librerías vetadas), crea un `CONSTITUTION.md` en la raíz con esas decisiones inmutables. El agente lo va a leer y respetar. Estructura típica: `## Stack obligatorio` (lenguaje, frontend, backend, BD con versiones), `## Patrones obligatorios` (repository pattern, servicios sin estado, error handling tipado), `## Librerías vetadas` (con su alternativa). Sin `CONSTITUTION.md`, el agente te va a preguntar todas estas cosas en la Fase 2 de su workflow.

### Invocación

**Nuevo / reingeniería:**

```
Use the disenador-arquitecto subagent to produce docs/design.md
```

**Mantenimiento:**

```
Use the disenador-delta-mantenimiento subagent to produce
docs/features/<slug>/design.md
```

### Qué esperar (nuevo + reingeniería)

| Fase del agente | Qué hace | Tu trabajo |
|--|--|--|
| 1. Lectura | Lee `requirements.md` y `CONSTITUTION.md` si existe. Te lista cuántos Requirements detectó y qué decisiones técnicas faltan. | Confirmar el alcance. |
| 2. Decisiones técnicas | Te entrega preguntas numeradas sobre stack, persistencia, despliegue, autenticación, integraciones. | Responder. Si ya están en `CONSTITUTION.md`, el agente las usa sin preguntar. |
| 3. Generación | Genera las 9 secciones del `design.md` una por una. | Revisar cada sección antes de aprobar la siguiente. |
| 4. Trazabilidad | Construye la tabla final conectando cada criterio EARS → componente → test. | Verificar que no haya huecos. |
| 5. Auto-validación | Ejecuta checklist del SKILL. | Esperar 100% ✅. |
| 6. Cierre | Declara listo. | Tú apruebas o pides cambios. |

### Qué esperar (mantenimiento)

El agente `disenador-delta-mantenimiento` ejecuta 7 fases internas (similares pero acotadas al delta):

| Fase del agente | Qué hace | Tu trabajo |
|--|--|--|
| 1. Lectura completa | Lee `requirements.md` del feature, `BIG_PICTURE.md`, `REGLAS_DE_NEGOCIO.md`, `CONSTITUTION.md` si existen, y los componentes listados en Surface of Contact. Reporta stack heredado, patrones detectados, componentes del delta. | Confirmar alcance. |
| 2. Mapeo de invariantes a tests | Para cada invariante del requirements, identifica si tiene test existente. Las que no tienen test van a Regression Shield. | Validar el mapeo. |
| 3. Decisiones técnicas (solo del delta) | Preguntas numeradas sobre decisiones **NUEVAS** del feature. NO te pregunta stack porque está heredado. | Responder. Si una decisión nueva contradice una decisión heredada, el agente te alerta — decides cómo proceder. |
| 4. Generación | Genera las 9 secciones del design delta (200–600 líneas, no 300–800). | Revisar sección por sección. La sección 2.2 (Delta Architecture con Mermaid) y la sección 8 (tabla invariantes → tests) son las más críticas. |
| 5. Validación de no-invasión | Cruza componentes del design contra Surface of Contact del requirements. Si el design propone tocar algo no autorizado, te alerta. | Decidir: actualizar Surface of Contact (vuelta al analista) o quitar del design. |
| 6. Auto-validación | Checklist del SKILL `sdd-design-delta`. | Esperar 100% ✅. |
| 7. Cierre | Declara listo. | Tú apruebas o pides cambios. |

### Las 9 secciones que debe tener el `design.md`

**Nuevo / reingeniería** (`docs/design.md`):

1. Overview
2. Architecture (con diagrama Mermaid)
3. Data Model
4. Interface Contracts
5. Technical Decisions (ADRs)
6. Critical Flows (diagramas de secuencia Mermaid)
7. Error & Edge Case Strategy
8. Testing Strategy
9. Traceability (tabla obligatoria)

**Mantenimiento** (`docs/features/<slug>/design.md`) — mismas 9 secciones pero acotadas al delta:

1. Overview del Delta
2. Architecture (2.1 Arquitectura Heredada inmutable + 2.2 Delta Architecture con Mermaid diferenciando nuevo/modificado/existente)
3. Data Model Delta (solo entidades nuevas o modificaciones, `ALTER` explícito si modifica)
4. Interface Contracts Delta (endpoints nuevos + extensiones a existentes con qué preservan)
5. Technical Decisions (ADRs del delta, prefijo D001) + sección "Decisiones heredadas que se mantienen"
6. Critical Flows Afectados + sección "Coexistencia con flujos existentes"
7. Error & Edge Case Strategy del Delta
8. Testing Strategy (delta + tabla obligatoria invariantes → tests de regresión)
9. Traceability (tabla doble: criterios EARS del delta + invariantes preservadas)

### Cómo validar

**Nuevo / reingeniería:**

- [ ] Tiene las 9 secciones en orden.
- [ ] Entre 300–800 líneas. Si pasa de 800, el feature es muy grande y hay que partirlo en sub-features.
- [ ] Cero funciones completas de código (pseudocódigo está bien, código no).
- [ ] Cada ADR tiene consecuencias positivas **Y NEGATIVAS** (si no, la decisión no se pensó).
- [ ] Los errores están tipados como enum ("USER_NOT_FOUND"), no descritos en prosa.
- [ ] La tabla de Traceability está completa: cada criterio EARS aparece con su componente y su test.

**Mantenimiento (adicional a lo anterior):**

- [ ] Entre 200–600 líneas (más corto porque es solo delta).
- [ ] La sección 2 tiene 2.1 Arquitectura Heredada **Y** 2.2 Delta Architecture.
- [ ] El diagrama Mermaid de 2.2 distingue visualmente componentes nuevos / modificados / existentes (colores o estilos distintos).
- [ ] Ningún componente del design queda fuera de la Surface of Contact del requirements (no se invade territorio no autorizado).
- [ ] La sección 6 tiene "Coexistencia con flujos existentes" si Surface of Contact tiene filas riesgo medio/alto.
- [ ] ADRs solo para decisiones **NUEVAS** del delta (prefijo D001). Decisiones heredadas se citan, no se redeciden.
- [ ] Sección 8 tiene tabla Invariante → Test que la valida → ¿Existe hoy?. Cualquier invariante sin test existente lleva tarea de blindaje en `tasks.md`.
- [ ] Sección 9 Traceability tiene doble tabla: criterios EARS del delta + invariantes preservadas.
- [ ] Cambios en data model son compatibles hacia atrás (`NOT NULL` con `DEFAULT`, etc.).

Si todo está, di explícitamente **"aprobado, sigue con tasks"**.

---

## 5. Fase 5: Tasks (descomposición)

Distinto agente según caso.

| Caso de uso | Subagente | Output | Orden |
|--|--|--|--|
| Nuevo / reingeniería | `descompositor-tareas` | `docs/tasks.md` | Rebanadas verticales (default); por capa solo si el design declara `layered` |
| Mantenimiento | `descompositor-riesgo-mantenimiento` | `docs/features/<slug>/tasks.md` | Por riesgo de regresión |

### Pre-requisito

- **Nuevo / reingeniería:** `docs/design.md` aprobado por ti.
- **Mantenimiento:** `docs/features/<slug>/design.md` aprobado por ti.

### Invocación

**Nuevo / reingeniería:**

```
Use the descompositor-tareas subagent to produce docs/tasks.md
```

**Mantenimiento:**

```
Use the descompositor-riesgo-mantenimiento subagent to produce
docs/features/<slug>/tasks.md
```

### Qué esperar (nuevo / reingeniería)

El agente:

1. Lee `design.md` y `requirements.md` completos.
2. Te lista cuántas tareas estima generar (aproximado).
3. Mapea cada criterio EARS a tarea(s) tentativa(s).
4. Genera el `tasks.md`. Por default usa **walking skeleton + rebanadas verticales** (`delivery_strategy: vertical`): cada Slice atraviesa las capas necesarias para entregar valor end-to-end. Solo si el `design.md` declara `delivery_strategy: layered` lo descompone por capas (Setup → Data Model → Data Access → Business Logic → API → UI → Integration Tests → Documentation).
5. Cada tarea tiene checkbox, número, verbo concreto, sub-pasos, criterio de hecho, y footer _Requirements: X.Y_.
6. Hace una pasada de podado (quita redundantes, parte las grandes, promueve tests a tareas independientes).
7. Auto-valida.

### Qué esperar (mantenimiento)

El agente `descompositor-riesgo-mantenimiento`:

1. Lee `design.md` delta y `requirements.md` delta completos.
2. Mapea estructura de tests existentes (con Glob/Read).
3. Te lista cantidad estimada de tareas, cuántas invariantes a blindar, cuántos puntos de integración aislados.
4. Genera el `tasks.md` con estructura por riesgo:
   - **Regression Shield** (PRIMERO): verificar suite existente + Blindar invariantes sin test
   - **Spike** (opcional)
   - **Data Model Delta** (si aplica)
   - **Backend Delta**
   - **API Delta**
   - **Frontend Delta** (si aplica)
   - **Integration** (una tarea aislada por punto de coexistencia)
   - **Integration Tests** (E2E del feature)
   - **No-Regression Validation** (ÚLTIMO): suite completa + verificar todas las invariantes
   - **Documentation**
5. Cada tarea con footer doble: _Requirements: X.Y_ | _Invariants: I.A_.
6. Hace pasada de podado y auto-valida.

### Cómo validar

**Nuevo / reingeniería:**

- [ ] El archivo está organizado por rebanadas verticales (walking skeleton + slices end-to-end); por capas solo si el design declaró `delivery_strategy: layered`.
- [ ] Cada tarea tiene los 5 elementos: checkbox + número + verbo + sub-pasos + criterio de hecho + footer.
- [ ] Tareas son chiquitas (1–3 archivos, 50–200 líneas estimadas).
- [ ] Tests están como tareas independientes, no como sub-pasos.
- [ ] Cada criterio EARS del `requirements.md` aparece referenciado en al menos una tarea.
- [ ] Hay al menos una tarea de tests E2E al final.

**Mantenimiento (adicional):**

- [ ] La primera sección es `## Regression Shield`. Tiene al menos: tarea 1 = ejecutar suite existente + una tarea Blindar por cada invariante sin test.
- [ ] Las tareas con verbo Blindar van **ANTES** de las tareas que modifican el módulo correspondiente.
- [ ] Cada tarea tiene footer doble: _Requirements: X.Y_ | _Invariants: I.A_ (al menos uno con referencia, no ambos `-`).
- [ ] Las tareas de Modificar declaran explícitamente **QUÉ preservar** (referencia a la invariante correspondiente).
- [ ] Sección `## Integration` tiene una tarea aislada por cada punto de coexistencia (cada fila de Surface of Contact con riesgo medio/alto). NO se agrupan.
- [ ] La última sección es `## No-Regression Validation` con una tarea final de verbo Verificar regresión que cubre **TODAS** las invariantes.
- [ ] Cada invariante del requirements aparece referenciada en al menos una tarea.
- [ ] Cada criterio EARS del delta aparece referenciado en al menos una tarea de implementación.

### Recomendación importante

Dale una hora a podar `tasks.md` tú misma antes de empezar a ejecutar. Esa hora te ahorra cinco horas de errores durante el desarrollo. Busca:

- Tareas demasiado grandes que el agente no partió → pártelas.
- Tareas redundantes "por completitud" → quítalas.
- Tests escondidos como sub-pasos → promuévelos a tarea.
- **(Mantenimiento)** Tareas de integración agrupadas → sepáralas, una por punto de coexistencia.
- **(Mantenimiento)** Tareas de modificación sin invariante a preservar → revisa si te falta el blindaje correspondiente en Regression Shield.

---

## 6. Fase 6: Build / Ejecución del código

Aquí ya no usas los subagentes del framework. Usas Claude Code directamente con sus capacidades estándar, por lotes de tareas (por default cada lote es una rebanada vertical / Slice; en modo `layered`, una capa), con tu revisión al cerrar cada lote.

> El comando `/stark-build` encapsula este patrón de ejecución por lotes. Lo de abajo es el detalle de qué hace y por qué — léelo una vez.

### Principio rector: la corrección manda sobre el ahorro

Antes de cualquier técnica de ahorro, fija esto:

**El código se genera desde la especificación leída, nunca desde lo que el agente "recuerde" o infiera.** Si el agente no tiene un criterio EARS o una sección del design frente a él, NO debe implementarlo de memoria — debe leerlo o preguntar. Un token ahorrado a costa de una inferencia incorrecta cuesta una sesión completa de re-trabajo.

Por lo tanto, **el ahorro de tokens nunca viene de leer menos especificación.** Viene de leer la especificación completa **UNA sola vez** y reutilizar ese contexto en varias tareas. Esa es la única forma de ahorro compatible con SDD.

### El patrón recomendado: trabajar por lotes

La unidad de trabajo es el **lote:** un grupo de tareas contiguas — en modo vertical (el default) una **rebanada vertical** (un Slice end-to-end); en modo `layered`, una capa — ejecutadas en una sola conversación, con el contexto completo cargado al inicio.

**¿Por qué es a la vez lo más correcto y lo más barato?**

- **Correcto:** el agente tiene `requirements.md` y `design.md` **ÍNTEGROS** en contexto durante todo el lote. Cada decisión se toma con la spec completa a la vista — sin fragmentos, sin inferencias.
- **Barato:** esos documentos se pagan una vez por lote, no una vez por tarea. Abrir una conversación nueva por cada tarea obliga al agente a releer todo desde cero (~56k tokens de spec por tarea, multiplicado por 48 tareas).

### El procedimiento

1. Abre una conversación nueva en Claude Code.

2. Dale este prompt (cambia los números por los de tu lote):

```
Lee COMPLETOS docs/tasks.md, docs/requirements.md y docs/design.md, una sola vez.

Después ejecuta las tareas 3, 4 y 5 (capa Data Model) en orden, una por una.
Reglas:
- Implementa cada tarea ÚNICAMENTE desde lo que dicen los documentos leídos.
  Si algo no está especificado o es ambiguo, DETENTE y pregúntame; no lo infieras.
- Respeta las erratas y resoluciones de la sección "Erratas" de tasks.md.
- No releas los documentos entre tareas: ya los tienes en contexto.

Al terminar cada tarea, repórtame: qué archivos creó, si cumple su
"Criterio de hecho", y el resultado de sus tests. NO marques [x]: eso lo hago yo.
```

3. Tres líneas de ese prompt garantizan la corrección — **no las quites por acortar:**

| Línea | Qué previene |
|--|--|
| "Lee COMPLETOS … una sola vez" | Que trabaje con fragmentos o de memoria. |
| "Si algo no está especificado… DETENTE y pregúntame; no lo infieras" | Que rellene huecos con suposiciones plausibles pero incorrectas. |
| "NO marques [x]: eso lo hago yo" | Que se auto-apruebe código sin tu revisión. |

4. Tú revisas el resultado de cada tarea del lote: corres los tests, lees el código, verificas el criterio de hecho.

5. Marcas `[x]` solo las que pasen. Cierras la conversación. Abres otra para el siguiente lote.

### Encadenar el siguiente lote en la MISMA conversación (aún más barato)

Si tras revisar un lote la conversación sigue sana (el agente responde coherente, no se ha hecho eterna), no hace falta abrir una nueva: puedes encargarle el siguiente lote ahí mismo. El contexto ya está cargado — no se relee nada, no se repaga nada.

```
Revisé el lote anterior: aprobado. Contexto ya cargado, no releas los
documentos ni reinspecciones la estructura del proyecto.

Ejecuta las tareas 21 a 25 (Business Logic: servicios y validadores)
de corrido, en orden. Mismas reglas: solo lo especificado en los
documentos, si algo es ambiguo DETENTE y pregúntame, y NO marques [x].

Al terminar cada tarea repórtame archivos, criterio de hecho y tests.
```

### Cuándo encadenar y cuándo cerrar

| Señal | Qué hacer |
|--|--|
| El lote anterior pasó tu revisión y el agente sigue coherente | Encadena en la misma conversación. |
| La conversación ya está muy larga (muchas idas y vueltas, el agente repite o confunde cosas) | Cierra y abre conversación nueva para el siguiente lote. |
| El siguiente lote es de otra capa con tareas de validación de por medio (ej. "Validar integración") | Cierra: la tarea de validación va sola, y el lote nuevo arranca limpio después. |

**La regla "Cierras la conversación, abres otra" del paso 4 es el camino seguro por defecto;** el encadenamiento es la optimización cuando todo va bien. Ante la duda, cierra — una recarga de contexto es barata comparada con un lote ejecutado por un agente confundido.

### Por qué el lote no gasta más por leer completo

"Leer los documentos completos gasta mucho" es cierto solo si lo haces en cada tarea. En un lote, el costo de lectura se paga una vez y se divide entre las tareas: spec completa para 6 tareas = ~9k tokens por tarea, contra ~56k por tarea si abres conversación por cada una. Además el prompt caching mantiene el contexto barato — Claude cachea lo ya leído y reutilizarlo cuesta ~10% del precio normal; el temporizador de la caché (~5 min) se reinicia con cada interacción, así que trabajando de corrido se mantiene activa horas. Si expira por inactividad, el costo es una recarga puntual, sin perder contexto ni calidad.

**En una frase:** contexto completo, pagado una vez por lote. Nunca "contexto recortado para ahorrar" — eso es lo que genera código inferido e incorrecto.

### Qué tareas juntar en un lote

En modo vertical (el default), tu `tasks.md` viene en **rebanadas verticales**: cada Slice es un lote natural — cargas el contexto una vez y ejecutas las tareas de ese Slice. En modo `layered`, cada capa es el lote natural:

| Lote | Capa | Por qué agrupa bien |
|--|--|--|
| Setup | Andamiaje (monorepo, tsconfig, lint, test runners) | Cero lógica de negocio, cero riesgo |
| Data Model | Tipos / esquemas / constantes | Se construyen unos sobre otros, sin efectos externos |
| Data Access | Repositorios / capa de sesión + sus tests | Tests se auto-validan dentro del lote |
| Business Logic | Servicios, clientes, validadores | El más grande — pártelo por tamaño (clientes / validadores / servicios), no por riesgo |
| API / Routes | Endpoints + tests de integración | Comparten el mismo contrato de §4 |
| UI | Componentes / vistas | Comparten el shell y la capa de transporte |
| E2E | Specs de Playwright | Comparten el harness |

**Regla simple:** un lote = un Slice (modo vertical, el default) o una capa (modo `layered`). No mezcles features ni capas distintas en un mismo lote. Si un Slice o una capa es enorme (como Business Logic), pártela en pedazos por tamaño (clientes / validadores / servicios), no la hagas toda de un jalón.

(La tabla de arriba describe el caso `layered`. En modo vertical el lote es el Slice: agrupas sus tareas —que ya cruzan varias capas— en la misma conversación.)

### Qué tareas NUNCA van en lote (van solas)

- Tareas de validación de integración (las que dicen "Validar integración tareas X–Y", "Verificar regresión"). Son puntos de control donde **TÚ** decides si el bloque anterior quedó bien antes de seguir.
- Tareas con decisión humana pendiente (una errata abierta, un ADR que aún no apruebas, un campo cuya forma se fijó "por decisión humana").
- **(Mantenimiento)** Las tareas de Regression Shield (blindaje) y la No-Regression Validation final. El blindaje va antes del código nuevo por diseño; la validación final es el gate más importante del feature. Ninguna se lotea con tareas de modificación.

### Si solo necesitas UNA tarea suelta

A veces solo quieres una tarea (retomar algo, un arreglo puntual). Ahí sí abres una conversación para esa sola tarea. Puedes acotar la lectura a lo que la tarea cita, pero con la salvaguarda de corrección incluida — la lectura acotada jamás autoriza a inferir:

```
Ejecuta la tarea 3 de docs/tasks.md.

Lectura acotada (no leas los tres documentos completos):
- Lee la tarea 3 completa en docs/tasks.md.
- De docs/requirements.md: lee los Requirements COMPLETOS a los que pertenecen
  los criterios del footer "_Requirements:_" (el requirement entero con su
  User Story, no solo la línea del criterio).
- De docs/design.md: lee completas las secciones que la tarea cite con §.
- Lee las erratas que la tarea mencione (sección "Erratas" de tasks.md).

Regla de corrección: si con eso algo queda ambiguo o sin especificar,
NO lo infieras — amplía la lectura al documento completo o pregúntame.

Ejecuta solo la tarea 3 y dime si cumple su criterio de hecho. NO marques [x].
```

Es razonable para **UNA tarea.** Pero si vas a hacer varias, **el lote siempre gana** en costo y en corrección.

### Cómo está construida una tarea (referencia, NO lo escribes en el prompt)

Esta tabla es solo para que entiendas qué significan los símbolos que verás dentro de una tarea. No tienes que escribir nada de esto en tu prompt — el agente lo interpreta solo. Léela una vez y olvídala.

Cada tarea del `tasks.md` está construida siempre con las mismas piezas. Esta es una tarea real del proyecto, anotada pieza por pieza:

```
- [ ] 3. Definir tipos de dominio y enums en backend/src/types        ← el NÚMERO va en tu prompt
  - Crear ActorInput... según §3 del design.                         ← § = sección del design a leer
  - ...consumidos por los contratos internos de §4...                ← otra sección del design
  - ...derivada de DashboardArtifact + ActorInput — ver errata 4.    ← errata: léela al final del archivo
  - Crear los tipos auxiliares... (tareas 3, 4)                       ← depende de esas tareas (ya hechas)
  - Criterio de hecho: tipos compilan; el enum SectionId tiene...    ← cómo sabes que terminó bien
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2_                     ← criterios EARS: el agente los busca SOLO
```

Las 6 piezas y qué hace cada una:

| Pieza | Aspecto | Para qué sirve |
|--|--|--|
| Número (3) | `- [ ] 3.` | Lo **ÚNICO** que tú escribes en el prompt. |
| Sub-pasos | viñetas con archivos a crear | Lo que el agente ejecuta. Tú no haces nada. |
| §N | "según §3", "§4", "§6.1" | Apunta a una sección del `design.md`. El agente lee solo esa. |
| "errata N" | "ver errata 4", "NOTA DE ERRATA" | Hay decisiones ya tomadas en la sección ## Erratas detectadas en artefactos upstream (al final del `tasks.md`). El agente debe respetarlas. |
| "(tareas X, Y)" | "(tareas 3, 4)" | Dependencias: esas tareas deben estar hechas antes. Por eso se ejecutan en orden. |
| _Requirements:_ | el footer | Los criterios EARS que el agente busca solo en `requirements.md`. Tú no los copias. |

Dos detalles del footer que verás y son normales:

- `_Requirements: NFR 5.1, NFR 5.2_` → el prefijo NFR significa "requerimiento no funcional" (rendimiento, seguridad, etc.). El agente los busca igual, en la sección de NFR del `requirements.md`.
- `_Requirements: -_` → esa tarea no traza a ningún requerimiento (típico en Setup y Documentación). Es normal: el agente se guía por los sub-pasos y el criterio de hecho.

El **"Criterio de hecho" es TU herramienta de aprobación.** Cuando el agente termina, no le creas porque sí: relees esa línea y verificas que se cumple (corre los tests, revisa que compile, lo que diga). Solo entonces marcas `[x]`.

### El error que NUNCA debes cometer

❌ **"Lee `tasks.md` y ejecuta TODO".**

Rompe siempre, sin excepción:

- El agente pierde el hilo a la mitad → toma decisiones que se contradicen entre tareas.
- Los errores se van encadenando sin que nadie los revise.
- Si algo sale mal, no puedes deshacer solo una parte: se ensucia todo.
- Marca tareas como "hechas" con código que ni siquiera funciona.

**¿Cuál es la diferencia con un lote?** Un lote son pocas tareas de un mismo Slice (o de una misma capa en `layered`) que **TÚ revisas** al cerrar la conversación. "Ejecuta todo" son las 48 de corrido sin que nadie revise nada. Lo primero ahorra tokens y es seguro; lo segundo te explota en la cara.

**Regla de oro:** lote por rebanada vertical (o por capa en `layered`), revisión por lote. Junta las tareas de un mismo Slice en una conversación; revisa el resultado antes de marcar `[x]`. Si dudas si dos tareas van juntas, pregúntate: **"¿necesito ver el resultado de la primera antes de que empiece la segunda?"** Si la respuesta es sí, van en conversaciones separadas.

### Cuándo terminaste el feature

**Nuevo / reingeniería** — cuando se cumplen **LAS TRES condiciones:**

- Todas las tareas en `tasks.md` están en `[x]`.
- Todos los tests pasan.
- La tabla de Traceability del `design.md` está cubierta end-to-end.

**Mantenimiento** — cuando se cumplen **LAS CINCO condiciones:**

- Todas las tareas en `tasks.md` están en `[x]`.
- La suite completa de tests del repo pasa (no solo los nuevos del feature).
- Cada invariante del `requirements.md` se verificó manualmente y sigue cumpliéndose.
- La tabla de Traceability cubre criterios EARS del delta **E** invariantes preservadas.
- La tarea final Verificar regresión (sección No-Regression Validation) está en `[x]`.

**Sin No-Regression Validation, NO se cierra el feature.** Es no negociable.

### Consideraciones específicas de mantenimiento durante ejecución

- **Antes de empezar la tarea 1 del Regression Shield:** confirma que el repo está limpio (sin cambios sin commit) y que la suite completa de tests del repo pasa en verde. Si no, detente — el sistema está roto independientemente del feature.

- **Las tareas Blindar van antes de las tareas de modificación** de su módulo. Esto es por diseño. No las saltes "para ir más rápido".

- **Después de cada tarea de Modificar:** corre los tests del módulo modificado (no toda la suite todavía, solo los del módulo) y verifica que los tests de blindaje correspondientes siguen pasando. Solo entonces marca `[x]`.

- **Las tareas de Integration son aisladas.** Una por sesión, como cualquier otra. NO las agrupes en "voy a hacer todas las integraciones de un jalón".

- **La tarea final Verificar regresión** es la más importante de todo el feature. Tómate el tiempo:
  - Corre **TODA** la suite del repo (ej. `mvn test`, `npm test`, `pytest`, según el stack).
  - Para cada invariante de `requirements.md`, verifica manualmente que el comportamiento referenciado sigue siendo idéntico.
  - Si algo falla, **no marques `[x]`.** Detente, investiga, repara. Solo cierras cuando todo está verde.

---

## 7. Glosario

### Conceptos generales

- **SDD** (Spec-Driven Development): metodología donde las specs son el artefacto primario y el código se genera a partir de ellas.
- **EARS** (Easy Approach to Requirements Syntax): notación formal para escribir criterios de aceptación. Usa palabras clave fijas: THE SYSTEM SHALL, WHEN, WHILE, WHERE, IF/THEN.
- **User Story** (Historia de Usuario): descripción corta de una necesidad en formato "Como [rol], quiero [acción], para [objetivo]".
- **Acceptance Criteria** (Criterios de Aceptación): condiciones testeables que definen "está hecho". En SDD se escriben en EARS.
- **ADR** (Architecture Decision Record): registro corto de una decisión técnica con su contexto, consecuencias positivas y negativas.
- **Quality Gate:** punto de revisión humana obligatoria entre fases. No es opcional.
- **Trazabilidad:** capacidad de rastrear cada línea de código → tarea → componente del design → criterio EARS → historia de usuario.
- **Subagente:** instancia de Claude con system prompt propio, herramientas propias, identidad propia. Cada uno hace un trabajo específico.
- **Skill:** archivo `SKILL.md` con reglas y procedimientos que un subagente consulta. Es la "constitución" compartida.
- **CONSTITUTION.md:** archivo opcional con principios inmutables de un proyecto (stack obligatorio, patrones, vetos).
- **Vibe-coding:** pedirle código a la IA conversacionalmente sin estructura. Funciona para prototipos, rompe para producción.

### Casos de uso (pipelines)

- **Nuevo (greenfield):** proyecto desde cero. No hay código previo. Pipeline con `analista-entrevistas` → `disenador-arquitecto` → `descompositor-tareas`.
- **Reingeniería (brownfield-rewrite):** sistema legacy existente que se va a reescribir o modernizar arquitectura completa. Pipeline con `arqueologo-codigo` → `disenador-arquitecto` → `descompositor-tareas`.
- **Mantenimiento:** sistema en producción al que se le agrega un feature nuevo sin romper lo que ya funciona. Stack y arquitectura están dados. Pipeline con `analista-feature-mantenimiento` → `disenador-delta-mantenimiento` → `descompositor-riesgo-mantenimiento`.

### Conceptos específicos de mantenimiento

- **Delta:** el conjunto de cambios que un feature de mantenimiento introduce. Los artefactos del pipeline de mantenimiento describen solo el delta, no el sistema completo.
- **Surface of Contact:** tabla en el `requirements.md` de mantenimiento que lista exhaustivamente los módulos, archivos, endpoints, tablas que el feature toca, lee, modifica o explícitamente NO toca. Cada fila con nivel de riesgo (alto / medio / bajo).
- **Invariantes Preservadas:** lista numerada (I.1, I.2, ...) de comportamientos del sistema existente que **NO deben cambiar** tras el feature. Cada una con referencia al código fuente (`<!-- source: archivo:líneas -->`) y un test (existente o de blindaje) que la valida.
- **Sustrato** (de mantenimiento): los tres archivos `docs/CLAUDE.md`, `docs/BIG_PICTURE.md` y `docs/REGLAS_DE_NEGOCIO.md` que documentan el sistema existente. Generados por las skills auxiliares `onboarding` y `reglas-negocio` (incluidas en `.claude/skills/`). Recomendados pero no obligatorios.
- **Intent.md:** archivo de entrada del pipeline de mantenimiento. Lo escribe el humano describiendo el feature en lenguaje de negocio. Vive en `docs/features/<slug>/intent.md`.
- **Regression Shield:** primera sección del `tasks.md` de mantenimiento. Tareas de blindaje (verbo Blindar) que escriben tests de regresión sobre código existente que el feature va a tocar. Se ejecutan **ANTES** de cualquier modificación.
- **No-Regression Validation:** última sección obligatoria del `tasks.md` de mantenimiento. Tarea de verbo Verificar regresión que corre suite completa + verifica cada invariante manualmente antes de cerrar el feature.
- **Trazabilidad doble:** cada tarea del `tasks.md` de mantenimiento lleva footer `_Requirements: X.Y_ | _Invariants: I.A_`, conectando tanto criterios EARS del delta como invariantes preservadas.
- **Blindar:** verbo nuevo de tareas en pipeline de mantenimiento. Significa "escribir un test de regresión sobre código existente para asegurar que su comportamiento actual se preserve durante el feature".
- **Coexistencia:** estrategia de cómo el delta convive con flujos existentes sin alterarlos. Documentada en sección 6 del `design.md` delta cuando hay puntos de Surface of Contact con riesgo medio/alto.
- **Válvula de retorno** (mantenimiento): cuando el design propone tocar algo fuera de Surface of Contact, volver al analista para actualizar el requirements antes de seguir.

### Skills auxiliares del framework (usadas como sustrato del pipeline de mantenimiento)

- **onboarding** (skill): protocolo de reconocimiento para proyectos heredados. Genera `CLAUDE.md` (guía del repo) y `BIG_PICTURE.md` (radiografía arquitectónica). Recomendada antes del primer feature de mantenimiento sobre un sistema. Vive en `.claude/skills/onboarding/`.
- **reglas-negocio** (skill): extrae roles, permisos, flujos de estados, validaciones, mapa funcional del código existente. Genera `docs/REGLAS_DE_NEGOCIO.md`. Recomendada antes del primer feature de mantenimiento. Vive en `.claude/skills/reglas-negocio/`.

Aunque son de stark, son agnósticas al pipeline SDD per se — sirven para analizar cualquier repo, no solo proyectos que usen SDD. El pipeline de mantenimiento las usa porque su output es exactamente el sustrato que el agente `analista-feature-mantenimiento` necesita.

---

## Cierre

Para el camino feliz lineal, usa [`QUICKSTART.md`](QUICKSTART.md). Si algo se trabó, [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md). Para el "por qué" detrás de cada decisión, [`PRINCIPIOS.md`](PRINCIPIOS.md) y [`DECISIONES.md`](DECISIONES.md).

Recuerda: una fase a la vez, una tarea por sesión, tú apruebas.
