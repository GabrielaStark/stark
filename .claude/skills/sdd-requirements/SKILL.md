---
name: sdd-requirements
description: Use this skill whenever generating, validating, or editing a requirements.md file for Spec-Driven Development. Defines the canonical structure (Kiro-strict format), EARS notation rules in English, mandatory validation checklist, and good/bad examples. Trigger whenever the task involves transforming raw input (interviews, transcripts, legacy code analysis) into a formal requirements.md, or when reviewing an existing requirements.md for compliance.
---

# SDD Requirements — Constitución

Este skill es la fuente de verdad para producir `requirements.md` en este repo. Ambos subagentes (`sintetizador-levantamiento` y `arqueologo-codigo`) consultan este archivo. Cualquier `requirements.md` producido debe cumplir TODAS las reglas de aquí.

## 1. Propósito del requirements.md

Es el contrato formal entre el levantamiento y el resto del pipeline SDD (`design.md` → `tasks.md` → código). Su lector primario es un LLM que generará el `design.md` downstream. Su lector secundario es el humano que valida.

Regla de oro: **si otro desarrollador (humano o agente) que no estuvo en el levantamiento no puede entender qué construir leyendo solo este archivo, NO está listo**.

## 2. Estructura obligatoria (Kiro-strict)

El archivo SIEMPRE tiene esta estructura, en este orden:

```markdown
# Requirements: [Nombre del feature o sistema]

## Introduction

[Párrafo descriptivo: qué es el sistema/feature, qué problema resuelve,
quién lo usa. Máximo 5-7 líneas. Cero implementación, cero arquitectura.]

## Requirements

### Requirement 1

**User Story:** Como [rol], quiero [acción/capacidad], para [objetivo de negocio].

#### Acceptance Criteria

1. WHEN [trigger] THE SYSTEM SHALL [response]
2. IF [unwanted condition] THEN THE SYSTEM SHALL [response]
3. WHILE [state] THE SYSTEM SHALL [response]

### Requirement 2

**User Story:** Como [rol], quiero [acción/capacidad], para [objetivo de negocio].

#### Acceptance Criteria

1. ...

[... más requirements ...]

## Non-Functional Requirements

[Solo si aplica: performance, seguridad, accesibilidad, compatibilidad.
También en formato EARS.]

## Out of Scope

[Lista explícita de lo que NO se va a hacer. Esto es tan importante
como lo que sí. Evita scope creep y suposiciones del LLM downstream.]

## Glossary

[Solo si el dominio tiene términos no obvios. Definiciones breves.]
```

### Reglas estructurales

- **User Story SIEMPRE en español**, formato exacto: `Como X, quiero Y, para Z`. Nunca abreviar, nunca omitir el "para Z" (sin objetivo de negocio, el LLM optimiza para correctitud funcional pero pierde sentido).
- **Acceptance Criteria SIEMPRE en inglés**, formato EARS estricto (ver sección 3).
- **Numeración**: Requirements numerados como `### Requirement N`. Criterios dentro de cada requirement numerados con `1.`, `2.`, etc.
- **Mínimo 1 criterio EARS por Requirement**. Si solo hay user story sin criterios, NO está completo.
- **Cada Requirement aborda UNA capacidad coherente**. Si un Requirement tiene 12 criterios de cosas distintas, pártelo en varios.

## 3. Sintaxis EARS (los 5 patrones)

### 3.1 Ubicua (siempre activa, sin keyword)

```
THE SYSTEM SHALL <response>
```

Ejemplo:

```
THE SYSTEM SHALL persist all calculations with UTC timestamps.
```

Uso: requerimientos invariantes que aplican siempre.

### 3.2 Event-driven (WHEN)

```
WHEN <trigger> THE SYSTEM SHALL <response>
```

Ejemplo:

```
WHEN the user clicks "Calcular ISR" THE SYSTEM SHALL compute the
tax amount based on current input values and display the result.
```

Uso: respuesta a una acción o evento puntual.

### 3.3 State-driven (WHILE)

```
WHILE <state> THE SYSTEM SHALL <response>
```

Ejemplo:

```
WHILE a calculation is in progress THE SYSTEM SHALL disable the
"Calcular" button to prevent duplicate submissions.
```

Uso: comportamiento mientras dura una condición.

### 3.4 Optional feature (WHERE)

```
WHERE <feature is present> THE SYSTEM SHALL <response>
```

Ejemplo:

```
WHERE the export-to-PDF module is enabled THE SYSTEM SHALL render
a "Exportar PDF" button on the results panel.
```

Uso: comportamiento condicional a presencia de un feature/módulo.

### 3.5 Unwanted behavior (IF/THEN)

```
IF <unwanted condition> THEN THE SYSTEM SHALL <response>
```

Ejemplo:

```
IF a required input field is empty when "Calcular" is pressed
THEN THE SYSTEM SHALL block the calculation and highlight the
missing field in red.
```

Uso: manejo de errores, validaciones, casos borde.

### 3.6 Complex (combinaciones)

```
WHILE <state>, WHEN <trigger> THE SYSTEM SHALL <response>
```

Ejemplo:

```
WHILE the user is authenticated, WHEN the session token expires
THE SYSTEM SHALL prompt for re-authentication without losing
unsaved input.
```

Uso: cuando un comportamiento requiere precondición de estado Y trigger de evento.

## 4. Reglas de oro

### Lo que SÍ

- **Solo `SHALL`**. Es el único verbo modal permitido.
- **Sujeto siempre `THE SYSTEM`** (o nombre específico del subsistema si está claramente delimitado, ej. `THE AUTH MODULE SHALL...`).
- **Respuestas testeables**: cada criterio debe poder traducirse a un test pasa/falla sin interpretación.
- **Errores tipados**: si el criterio menciona un error, nombrarlo (ej. `display "FIELD_REQUIRED" error`), no describirlo vagamente.
- **Cantidades concretas**: "responda en menos de 200ms", no "responda rápido".

### Lo que NO

- ❌ `should`, `would`, `may`, `might`, `could`. Cero. Si te encuentras escribiendo uno, refrasea con `SHALL`.
- ❌ Adjetivos vagos: "user-friendly", "intuitive", "fast", "robust". No son testeables.
- ❌ Implementación: "use a REST API", "store in PostgreSQL", "render with React". Eso va en `design.md`, NO aquí.
- ❌ Múltiples comportamientos en un solo criterio. Un criterio = una respuesta. Si dice "y además", pártelo.
- ❌ User Story sin "para Z" (el por qué). Es el campo que el LLM más usa para tomar decisiones de diseño.
- ❌ Requirements duplicados o solapados. Si dos criterios dicen casi lo mismo, fusiónalos o diferéncialos explícitamente.

## 5. Ejemplos comparados

### Ejemplo MAL

```markdown
### Requirement 3

**User Story:** Como usuario, quiero calcular impuestos.

#### Acceptance Criteria

1. El sistema debería calcular el ISR correctamente y rápido.
2. WHEN press button system calculates and shows result and saves it.
3. The system should be user-friendly.
```

Problemas:

- User Story sin objetivo de negocio ("para Z")
- Criterio 1 en español, con "debería" (no SHALL), con "rápido" (no testeable), con "correctamente" (vago)
- Criterio 2 mete 3 comportamientos en uno (calcular, mostrar, guardar)
- Criterio 3 no es testeable
- Falta `THE SYSTEM SHALL` formal

### Ejemplo BIEN

```markdown
### Requirement 3

**User Story:** Como contador, quiero calcular el ISR de un trabajador a partir de su salario mensual, para entregarle al patrón el monto exacto a retener según la tabla SAT vigente.

#### Acceptance Criteria

1. WHEN the user enters a monthly salary and clicks "Calcular ISR" THE SYSTEM SHALL compute the tax using the SAT tariff table for the current fiscal year.
2. WHEN the calculation completes THE SYSTEM SHALL display the ISR amount, the applicable bracket, and the marginal rate.
3. IF the monthly salary field is empty or non-numeric THEN THE SYSTEM SHALL block the calculation and display "SALARY_REQUIRED" or "SALARY_INVALID" respectively.
4. THE SYSTEM SHALL complete the calculation in under 200ms for inputs up to 1,000,000 MXN.
```

## 6. Checklist de auto-validación (OBLIGATORIO antes de cerrar)

Antes de declarar `requirements.md` terminado, ejecutar mentalmente cada uno de estos chequeos. Si CUALQUIERA falla, NO entregar — corregir y revalidar.

### Estructura

- [ ] Existe sección `## Introduction` con párrafo descriptivo (no implementación)
- [ ] Existe sección `## Requirements` con al menos un `### Requirement N`
- [ ] Existe sección `## Out of Scope` (puede estar vacía si aplica, pero la sección está)
- [ ] Numeración secuencial sin huecos (`Requirement 1, 2, 3...`)

### User Stories

- [ ] Cada Requirement tiene `**User Story:**` exactamente con ese formato
- [ ] Cada User Story está en español
- [ ] Cada User Story tiene los tres componentes: `Como X, quiero Y, para Z`
- [ ] Ningún "para Z" está vacío o es genérico ("para usarlo", "para que funcione")

### Acceptance Criteria

- [ ] Cada Requirement tiene `#### Acceptance Criteria` con al menos 1 criterio
- [ ] Todos los criterios están en inglés
- [ ] Todos los criterios usan exclusivamente `SHALL` (ningún `should`, `would`, `may`, `might`, `could`)
- [ ] Todos los criterios empiezan con uno de: `THE SYSTEM SHALL`, `WHEN`, `WHILE`, `WHERE`, `IF`
- [ ] Todos los criterios tienen sujeto `THE SYSTEM` (o subsistema nombrado)
- [ ] Ningún criterio mezcla múltiples comportamientos (señal: aparece " and " conectando acciones)
- [ ] Ningún criterio menciona implementación (REST, SQL, framework específico, librería específica)
- [ ] Ningún criterio usa adjetivos vagos no testeables ("fast", "easy", "intuitive", "user-friendly")
- [ ] Cantidades son específicas con unidad (no "rápido", sí "<200ms")
- [ ] Errores se nombran como código tipado, no se describen narrativamente

### Coherencia

- [ ] No hay Requirements duplicados ni solapados
- [ ] Cada Requirement aborda UNA capacidad coherente
- [ ] La sección Out of Scope es explícita sobre qué NO se hace

### Si hay confianza variable (modo arqueólogo)

- [ ] Criterios derivados de código tienen anotación `<!-- confidence: high|medium|low; source: archivo:línea -->`
- [ ] Huecos no resueltos están listados en sección final `## Open Questions`

## 7. Cuando el output NO está listo

Si después de la auto-validación queda CUALQUIER ítem sin marcar:

1. **NO entregues el requirements.md**.
2. Reporta al usuario humano qué ítems fallaron y qué información hace falta para resolverlos.
3. Itera hasta que el checklist completo esté satisfecho.

Mejor entregar un requirements.md incompleto con `## Open Questions` explícitas que un requirements.md que parece completo pero tiene huecos disfrazados.
