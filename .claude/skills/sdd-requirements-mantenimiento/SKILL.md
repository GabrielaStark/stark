---
name: sdd-requirements-mantenimiento
description: Use this skill whenever generating, validating, or editing a requirements.md file for the SDD MAINTENANCE pipeline (adding a feature to a production system without breaking it). Defines the canonical structure (Contexto, Surface of Contact, Invariantes Preservadas, Requirements del delta), EARS notation rules (English, SHALL only, same as sdd-requirements), and the mandatory validation checklist. Trigger whenever the task involves transforming a feature intent.md + production code into a delta-scoped requirements.md for maintenance. NOT for greenfield or brownfield-rewrite — use sdd-requirements for those.
---

# SDD Requirements Mantenimiento — Constitución

Este skill es la fuente de verdad para producir `docs/features/<feature>/requirements.md` en el pipeline de **mantenimiento** del framework stark. El subagente `analista-feature-mantenimiento` consulta este archivo. Cualquier `requirements.md` producido en este pipeline debe cumplir TODAS las reglas de aquí.

## 1. Propósito del requirements.md de mantenimiento

Es el contrato formal entre el levantamiento del **feature nuevo** y el resto del pipeline de mantenimiento (`design.md` delta → `tasks.md` por riesgo → código). Su lector primario es un LLM downstream que producirá el `design.md` delta. Su lector secundario es el humano que valida.

**Diferencia crítica vs `sdd-requirements` (pipelines de construcción):**

- Este documento describe SOLO el delta (lo que se añade), no el sistema completo.
- Documenta explícitamente la **superficie de contacto** con el sistema existente.
- Documenta explícitamente las **invariantes preservadas** — comportamiento actual que NO debe cambiar.
- Asume que el sistema ya existe en producción y NO se va a reescribir.

Regla de oro: **si un desarrollador que nunca tocó este código pudiera implementar el feature leyendo solo este archivo (más el CLAUDE.md / BIG_PICTURE.md / REGLAS_DE_NEGOCIO.md del repo) SIN romper lo existente, está listo.**

## 2. Estructura obligatoria

El archivo SIEMPRE tiene esta estructura, en este orden:

```markdown
# Requirements: [Nombre del feature]

> Feature de mantenimiento sobre el sistema `<nombre-sistema>`. Este documento describe **el delta**, no el sistema completo.

## Contexto

[Párrafo descriptivo:
- Qué feature se va a agregar
- Por qué (problema que resuelve / decisión de negocio que lo motiva)
- Quién lo pidió (stakeholder)
- En qué módulo/área del sistema vive
Máximo 7-10 líneas. Cero implementación, cero arquitectura nueva.]

## Surface of Contact

[Tabla obligatoria. Lista exhaustiva de los módulos, archivos, endpoints,
tablas y servicios que el feature **toca** o **lee**. Sin esto, el agente
de design no sabe dónde aterriza el feature.]

| Elemento del sistema | Tipo | Qué se hace | Riesgo |
|---|---|---|---|
| `src/users/UserService.java` | Servicio existente | Modificar para agregar método X | medio |
| `users` (tabla) | Schema existente | Agregar columna Y | medio |
| `POST /api/users` | Endpoint existente | Sin cambios (solo lectura) | bajo |
| `src/notifications/` | Módulo existente | Agregar dependencia desde X | alto |
| `src/reports/` | Módulo existente | NO se toca | — |

Niveles de riesgo:
- **alto**: punto de coexistencia con flujo crítico, alta probabilidad de regresión
- **medio**: modificación localizada con tests existentes que cubren
- **bajo**: lectura o consumo sin modificar

## Invariantes Preservadas

[Lista numerada de comportamientos existentes que el feature NO debe cambiar.
Cada invariante con referencia al código que la implementa hoy. Estas son
las garantías de "no romper nada".]

1. **I.1** — Los usuarios con rol `ADMIN` mantienen acceso a todos los endpoints actuales sin modificación.
   <!-- source: src/auth/RoleGuard.java:42-58 -->
2. **I.2** — El cálculo de ISR existente no cambia sus resultados para entradas idénticas.
   <!-- source: src/tax/IsrCalculator.java:120-180; tests: TaxCalculatorTest.testIsrStandardCases -->
3. **I.3** — El endpoint `POST /api/users` sigue retornando 201 con el mismo payload que hoy.
   <!-- source: src/users/UserController.java:34-67 -->

[...]

## Requirements (del delta)

### Requirement 1

**User Story:** Como [rol], quiero [acción/capacidad nueva], para [objetivo de negocio].

#### Acceptance Criteria

1. WHEN [trigger] THE SYSTEM SHALL [response]
2. IF [unwanted condition] THEN THE SYSTEM SHALL [response]

### Requirement 2

**User Story:** Como [rol], quiero [acción/capacidad nueva], para [objetivo de negocio].

#### Acceptance Criteria

1. ...

[... más Requirements del delta ...]

## Non-Functional Requirements (del delta)

[Solo si el feature introduce restricciones nuevas: performance, seguridad,
accesibilidad, compatibilidad. EARS estándar.]

## Tests Existentes a Preservar

[Lista de tests existentes que cubren los módulos tocados. El pipeline de
tasks va a usar esta lista para construir el "regression shield" antes
de empezar a modificar código. Si un módulo de alto riesgo NO tiene tests,
documentarlo aquí explícitamente — ese gap se cubre en tasks.]

| Test existente | Cubre | ¿Existe? |
|---|---|---|
| `UserServiceTest.testCreateUser` | UserService.createUser | Sí |
| `TaxCalculatorTest.testIsrStandardCases` | I.2 (cálculo ISR) | Sí |
| (sin test para `NotificationDispatcher`) | módulo a tocar | **NO — gap a cubrir** |

## Out of Scope (del feature)

[Lista explícita de lo que NO se va a hacer en este feature. Tan importante
como lo que sí. Evita scope creep dentro del mantenimiento.]

## Open Questions

[Cosas no resueltas al momento del cierre del requirements. Vacío idealmente.]

## Glossary

[Solo si el dominio tiene términos no obvios o jerga del cliente.]
```

### Reglas estructurales

- **User Story SIEMPRE en español**, formato exacto: `Como X, quiero Y, para Z`.
- **Acceptance Criteria SIEMPRE en inglés**, formato EARS estricto (ver sección 3).
- **Surface of Contact es obligatoria.** Sin esta tabla, el design no puede acotar el delta. Si vacía, el feature no tiene justificación para estar en mantenimiento (¿es realmente un delta?).
- **Invariantes Preservadas es obligatoria.** Mínimo 1 invariante. Si no hay invariantes que preservar, probablemente es greenfield o brownfield-rewrite, no mantenimiento.
- **Cada invariante lleva referencia al código** con comentario HTML `<!-- source: archivo:líneas -->`. Sin la fuente, la invariante no es auditable.
- **Numeración**: Requirements `### Requirement N`, invariantes `**I.N**`, criterios `1., 2., 3.`.
- **Mínimo 1 criterio EARS por Requirement del delta.**

## 3. Sintaxis EARS

Las reglas son **idénticas** a `sdd-requirements`. Para no duplicar la constitución, este skill **hereda** los 5 patrones EARS y sus reglas de oro. Resumen:

- Solo `SHALL` como verbo modal. Cero `should`, `would`, `may`, `might`, `could`.
- Sujeto siempre `THE SYSTEM` (o subsistema nombrado).
- Patrones: ubicua (`THE SYSTEM SHALL`), event-driven (`WHEN`), state-driven (`WHILE`), optional (`WHERE`), unwanted (`IF/THEN`).
- Cada criterio es testeable y atómico (un solo comportamiento).
- Errores tipados como enum, no descritos.
- Cantidades concretas con unidad.

Ver `.claude/skills/sdd-requirements/SKILL.md` §3-4 para los detalles, ejemplos y reglas extendidas. Este skill las asume válidas.

## 4. Reglas específicas de mantenimiento

### 4.1 Sobre la Surface of Contact

- Lista TODO lo que el feature toca, lee o modifica. La omisión es el modo de falla #1 en mantenimiento.
- Si un elemento del sistema se identifica como "podría tocarse pero no estoy seguro", **incluirlo con riesgo alto** y validar con el humano. Mejor sobre-listar que subestimar.
- Si el feature requiere modificar más de 5 módulos existentes, considerar partirlo en sub-features (mismo principio que features grandes en construcción).
- Para cada fila con `Riesgo: alto`, el design.md debe tener una sección de mitigación explícita.

### 4.2 Sobre las Invariantes Preservadas

- Una invariante es una afirmación verificable del tipo *"el comportamiento X sigue siendo Y"*.
- Cada invariante debe poder traducirse a un test de regresión concreto.
- Cada invariante referencia código existente con `<!-- source: archivo:líneas -->`.
- Si una invariante referencia un comportamiento sin tests, **anotarlo explícitamente** en "Tests Existentes a Preservar" como gap.
- Invariantes ambiguas ("la app no se rompe") son inválidas. Si no se puede traducir a test, no es una invariante; es deseo.

### 4.3 Sobre los Requirements del delta

- Cada Requirement describe SOLO el comportamiento **nuevo** que el feature introduce.
- Si un Requirement modifica comportamiento existente, documentarlo así: *"WHEN X happens THE SYSTEM SHALL now do Y (previously did Z)"* y mover el comportamiento Z a una sección `## Behavior Replaced` (con referencia a código y motivación).
- Out of Scope es scope del FEATURE, no del sistema. Lista qué el feature decidió NO hacer aunque podría.

### 4.4 Sobre el stack

- **No hay sección de stack en este documento.** El stack está fijado por el sistema existente. Si el feature requiere una librería nueva, va al ADR del design.md, no aquí.
- Si el feature requiere una decisión de stack genuinamente nueva (ej. agregar Redis donde no había), eso es un riesgo del feature y debe documentarse en Surface of Contact con riesgo alto + nota.

## 5. Ejemplos comparados

### Ejemplo MAL

```markdown
## Requirements

### Requirement 1
**User Story:** Como admin, quiero exportar reportes a PDF.

#### Acceptance Criteria
1. The system should export PDFs.
2. Don't break anything.
```

Problemas:
- Sin Contexto, Surface of Contact ni Invariantes Preservadas.
- User Story sin "para Z".
- Criterio con `should` (no SHALL).
- Criterio 2 ("don't break anything") no es testeable y revela que no se identificaron invariantes.

### Ejemplo BIEN

```markdown
## Contexto

El cliente solicitó la capacidad de exportar reportes mensuales a PDF para
adjuntar a su sistema contable externo. Hoy los reportes solo se muestran
en pantalla (módulo `reports/`). El feature vive en `reports/export/`, un
módulo nuevo dentro del existente. Pedido por: Andrea (contadora líder).

## Surface of Contact

| Elemento | Tipo | Qué se hace | Riesgo |
|---|---|---|---|
| `src/reports/ReportService.java` | Servicio existente | Extender con método `exportToPdf` | medio |
| `src/reports/export/` | Módulo nuevo | Crear con PdfGenerator | bajo |
| `GET /api/reports/:id` | Endpoint existente | Agregar query param `?format=pdf` | medio |
| Pom.xml | Build config | Agregar dep `openpdf:1.3.34` | bajo |
| Módulo `auth/` | Existente | Lectura — `ReportExportService` requiere rol | bajo |

## Invariantes Preservadas

1. **I.1** — El endpoint `GET /api/reports/:id` sin `?format=pdf` sigue retornando JSON con el mismo shape de hoy.
   <!-- source: src/reports/ReportController.java:45-78 -->
2. **I.2** — Los reportes en pantalla (formato HTML) renderizan idénticos antes y después del feature.
   <!-- source: src/reports/ReportRenderer.java; tests: ReportRendererTest -->
3. **I.3** — La autorización por rol no cambia: solo `ADMIN` y `ACCOUNTANT` ven reportes.
   <!-- source: src/auth/RoleGuard.java:88-102 -->

## Requirements (del delta)

### Requirement 1

**User Story:** Como contador, quiero exportar un reporte mensual a PDF, para adjuntarlo al sistema contable externo del cliente sin tener que reformatear datos a mano.

#### Acceptance Criteria

1. WHEN the user requests `GET /api/reports/:id?format=pdf` THE SYSTEM SHALL return a PDF file with the same content the HTML report shows for the same `id`.
2. WHEN the PDF is generated THE SYSTEM SHALL include header (logo + period), tabular body, and footer (generated timestamp in UTC).
3. IF the requested report does not exist THEN THE SYSTEM SHALL return HTTP 404 with error `"REPORT_NOT_FOUND"`.
4. IF the user lacks role `ADMIN` or `ACCOUNTANT` THEN THE SYSTEM SHALL return HTTP 403 with error `"FORBIDDEN"`.
5. THE SYSTEM SHALL generate the PDF in under 2 seconds for reports up to 500 rows.
```

## 6. Checklist de auto-validación (OBLIGATORIO antes de cerrar)

Antes de declarar el `requirements.md` de mantenimiento terminado, ejecutar mentalmente cada chequeo. Si CUALQUIERA falla, NO entregar — corregir y revalidar.

### Estructura específica de mantenimiento

- [ ] Existe sección `## Contexto` con el "qué/por qué/quién/dónde vive".
- [ ] Existe sección `## Surface of Contact` con tabla rellena (mínimo 1 fila).
- [ ] Existe sección `## Invariantes Preservadas` con mínimo 1 invariante numerada `I.N`.
- [ ] Cada invariante tiene comentario `<!-- source: archivo:líneas -->`.
- [ ] Existe sección `## Tests Existentes a Preservar` con tabla rellena.
- [ ] Existe sección `## Requirements (del delta)` con al menos un `### Requirement N`.
- [ ] Existe sección `## Out of Scope (del feature)`.

### Reglas EARS (mismas que sdd-requirements)

- [ ] Cada Requirement tiene `**User Story:**` con `Como X, quiero Y, para Z` completa, en español.
- [ ] Cada Requirement tiene `#### Acceptance Criteria` con al menos 1 criterio.
- [ ] Todos los criterios en inglés.
- [ ] Solo `SHALL` (ningún `should`, `would`, `may`, `might`, `could`).
- [ ] Cada criterio empieza con `THE SYSTEM SHALL`, `WHEN`, `WHILE`, `WHERE` o `IF`.
- [ ] Ningún criterio mezcla múltiples comportamientos.
- [ ] Ningún criterio menciona implementación específica (REST, SQL, framework).
- [ ] Ningún criterio usa adjetivos vagos.
- [ ] Errores tipados como enum.
- [ ] Cantidades con unidad concreta.

### Coherencia con el sistema existente

- [ ] La Surface of Contact lista TODOS los elementos del sistema que el feature toca o lee.
- [ ] Cada fila de Surface of Contact con `Riesgo: alto` tiene rationale en una nota o se refleja en alguna invariante.
- [ ] Las invariantes son testeables (cada una se puede traducir a un test concreto).
- [ ] Si un módulo de alto riesgo no tiene tests existentes, está documentado como gap en "Tests Existentes a Preservar".
- [ ] No hay Requirements del delta que contradigan invariantes (ej. si I.2 dice "X no cambia", ningún Requirement nuevo cambia X).
- [ ] El feature **no implica reescribir** arquitectura existente (si lo implica, pipeline incorrecto — usar brownfield-rewrite).

### Coherencia del delta

- [ ] No hay Requirements duplicados ni solapados.
- [ ] Cada Requirement aborda UNA capacidad coherente del feature.
- [ ] La sección Out of Scope es explícita sobre qué el feature NO hace.

## 7. Cuando el output NO está listo

Si después de la auto-validación queda CUALQUIER ítem sin marcar:

1. **NO entregues el requirements.md**.
2. Reporta al usuario humano qué ítems fallaron y qué información hace falta.
3. Itera hasta que el checklist completo esté satisfecho.

Mejor entregar requirements.md con `## Open Questions` explícitas que uno que parece completo pero no documenta invariantes o superficie de contacto — eso garantiza romper producción.

## 8. Relación con los outputs de las skills `onboarding` y `reglas-negocio`

Si en el repo existen los artefactos:

- `docs/CLAUDE.md` (generado por skill `onboarding`)
- `docs/BIG_PICTURE.md` (generado por skill `onboarding`)
- `docs/REGLAS_DE_NEGOCIO.md` (generado por skill `reglas-negocio`)

El agente DEBE leerlos como sustrato antes de inferir Surface of Contact e Invariantes. Estos archivos no se duplican en el requirements.md — se **referencian** cuando aplique:

```markdown
1. **I.4** — Las reglas de validación de RFC documentadas en `docs/REGLAS_DE_NEGOCIO.md` §3.2 se preservan sin cambios.
   <!-- source: src/validators/RfcValidator.java; ver REGLAS_DE_NEGOCIO.md §3.2 -->
```

Si esos archivos NO existen, el agente debe avisar al humano y recomendar correrlos antes — pero puede continuar sin ellos, asumiendo el riesgo y documentándolo en Open Questions.
