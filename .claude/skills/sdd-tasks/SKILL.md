---
name: sdd-tasks
description: Use this skill whenever generating, validating, or editing a tasks.md file for Spec-Driven Development. Defines task anatomy (checkbox, sequential number, action verb, sub-steps, references, EARS traceability footer), the two grouping structures per delivery_strategy (vertical/default — Walking Skeleton + feature slices demonstrable end-to-end; layered — by architectural layer, only for infra/migration/refactor without UI), the four operational rules, useful patterns (spike, preventive refactor, validation tasks, optional tasks), execution discipline (one task per agent session), and the mandatory validation checklist. Trigger whenever the task involves transforming an approved design.md into tasks.md, or when reviewing an existing tasks.md.
---

# SDD Tasks — Constitución

Este skill es la fuente de verdad para producir `docs/tasks.md` en cualquier proyecto que use este framework. El subagente `descompositor-tareas` consulta este archivo. Cualquier `tasks.md` producido debe cumplir TODAS las reglas de aquí.

## 1. Propósito del tasks.md

Es la **descomposición ejecutable** del `design.md` en unidades atómicas que el agente codificador procesa una por una.

- **NO** es un Gantt.
- **NO** es un plan de proyecto con fechas.
- **NO** es una lista de épicas.
- **NO** es una bitácora de avance.

**SÍ** es una secuencia ordenada de tareas pequeñas, autocontenidas, verificables, atadas a criterios EARS del requirements.md.

**Diferencia con backlog ágil**: backlog prioriza por valor de negocio y se ejecuta en sprints. Tasks.md prioriza por **dependencias técnicas y orden de construcción**, y se ejecuta linealmente.

## 2. Anatomía obligatoria de una tarea

Cada tarea en `tasks.md` SIEMPRE tiene esta estructura:

```markdown
- [ ] N. [Verbo acción] [objeto concreto]
  - [Sub-paso 1: archivos a tocar / patrón a aplicar]
  - [Sub-paso 2]
  - [Sub-paso 3]
  - Criterio de hecho: [cómo se sabe que terminó]
  - _Requirements: X.Y, X.Z_
```

### Elementos por elemento

#### Checkbox `- [ ]`

- Obligatorio al inicio.
- Estado legible por el agente entre sesiones.
- `[ ]` pendiente, `[x]` completado.

#### Número secuencial `N.`

- Las tareas se ejecutan en orden.
- El número marca secuencia obligatoria.
- Paralelizables se marcan `3a`, `3b` (mismo número base, sufijo letra).

#### Verbo de acción

- Concreto y acotado. Lista permitida:
  - `Implementar` — código nuevo
  - `Crear` — archivo/recurso nuevo
  - `Modificar` — código existente
  - `Agregar` — extensión a algo existente
  - `Refactorizar` — reorganizar sin cambiar comportamiento
  - `Configurar` — setup de herramienta/dependencia
  - `Validar` — verificación cruzada
  - `Documentar` — escritura de docs
- ❌ Prohibidos: "Trabajar en", "Hacer", "Investigar" (excepto en spikes formales)

#### Sub-pasos

- El "cómo" mínimo.
- Bullets concretos: qué archivos tocar, qué patrón aplicar, qué referencias usar.
- NO es pseudocódigo. NO es implementación.
- Referencia explícitamente lo que ya existe (ej. "usar middleware existente `auth.ts`") para evitar reinvención.

#### Criterio de hecho

- Línea explícita que dice cómo se verifica completitud.
- Ejemplos: "el endpoint retorna 201 en caso éxito y 400 en caso inválido", "los tests `test_create_*` pasan", "lint clean".
- Sin esto, el agente marca `[x]` con código que no funciona.

#### Footer de trazabilidad

- Formato exacto: `_Requirements: X.Y, X.Z_`
- Lista los criterios EARS del `requirements.md` que esta tarea cumple.
- Tareas de setup pueden tener `_Requirements: -_` (no atan a EARS específico).
- Sin trazabilidad, no hay manera de saber si terminaste el feature o solo parte.

## 3. Las 4 reglas operacionales

### Regla 1: Una tarea = una sesión del agente

- Heurística: 1-3 archivos tocados, 50-200 líneas de código.
- Si una tarea no se termina en una conversación con el agente codificador, está demasiado grande. Partirla.
- Tareas gigantes ("implementar el módulo completo") garantizan pérdida de contexto e inconsistencia.

### Regla 2: Orden por dependencias técnicas, NO por valor

- Primero lo que otras tareas necesitan, no lo más importante para el cliente.
- El **agrupamiento** de las tareas depende de `delivery_strategy` (ver Sección 4). En ambos modos las dependencias técnicas DENTRO de cada grupo se respetan igual: datos → lógica → API → UI.

**Modo vertical (default)** — agrupado por slices de feature:

1. Walking Skeleton: fundación mínima desplegable (scaffolding, config, un hilo pasante end-to-end trivial). NO mete features completas.
2. Slice N: una feature completa que cruza TODAS las capas (datos → lógica → API → UI + sus tests), un slice por feature, ordenados por valor/riesgo de negocio. Cada slice cierra demostrable de punta a punta.

**Modo layered (solo infraestructura/migración/refactor sin UI)** — agrupado por capa:

1. Setup y configuración (estructura, dependencias, configs)
2. Modelo de datos (schemas, migraciones, tipos)
3. Capa de acceso a datos (repositorios, queries)
4. Lógica de negocio (servicios, casos de uso)
5. Capa de API o interfaz (endpoints, handlers)
6. UI / cliente
7. Tests E2E integradores
8. Documentación de uso

### Regla 3: Criterio explícito de "hecho" en cada tarea

- Compila + lint clean + tests específicos pasan + criterio EARS verificable.
- Sin esto, completitud es subjetiva y el agente marca `[x]` prematuramente.

### Regla 4: Tests como tareas independientes, NO como sub-pasos

**MAL**:

```markdown
- [ ] 3. Implementar endpoint POST /api/expedientes
  - ...
  - Escribir tests
```

**BIEN**:

```markdown
- [ ] 3. Implementar endpoint POST /api/expedientes
  - ...
  - _Requirements: 1.1, 1.2_

- [ ] 4. Tests de integración para POST /api/expedientes
  - Caso éxito: payload válido + autenticado → 201
  - Caso error: campo faltante → 400 con error tipado
  - Caso error: sin sesión → 403
  - _Requirements: 1.1, 1.2_
```

Tests como sub-paso son lo primero que el agente recorta cuando va apurado. Como tarea independiente, son no negociables.

## 4. Estructura del archivo

El agrupamiento de headers depende de `delivery_strategy`. El **default es `vertical`**.

### Modo vertical (default): headers por slice de feature

```markdown
# Tasks: [Nombre del feature o sistema]

## 0. Walking Skeleton

- [ ] 1. [Scaffolding + config + un hilo pasante end-to-end trivial]
  - Fundación mínima desplegable: el sistema arranca, se despliega y atraviesa todas las capas con un end-to-end mínimo real.
  - Solo lo imprescindible para que exista algo desplegable. NO mete features completas.
  - _Requirements: -_

## Slice 1: [nombre de la feature]

- [ ] 2. [Crear schema y migración de ...]   (datos)
  - _Requirements: X.Y_

- [ ] 3. [Implementar lógica de ...]   (lógica)
  - _Requirements: X.Y_

- [ ] 4. [Implementar endpoint ...]   (API)
  - _Requirements: X.Y_

- [ ] 5. [Implementar pantalla ...]   (UI)
  - _Requirements: X.Y_

- [ ] 6. Tests del slice "[nombre]"   (tests independientes)
  - _Requirements: X.Y_

- [ ] 7. Criterio de hecho del slice: el sistema corre y la feature [X] es demostrable de punta a punta.
  - _Requirements: X.Y, X.Z_

## Slice 2: [siguiente feature]

- [ ] N. ...   (un slice por feature, ordenados por valor/riesgo de negocio)
```

Un slice cruza TODAS las capas de UNA feature (datos → lógica → API → UI + tests), respetando ese orden de dependencia DENTRO del slice, y cierra con el criterio: **el sistema corre y la feature [X] es demostrable de punta a punta.**

### Modo layered (solo infraestructura pura, migración o refactor sin UI): headers por capa

Solo legítimo cuando NO hay entrega vertical demostrable (sin UI). El `design.md` debe justificar por qué la entrega vertical no aplica.

```markdown
# Tasks: [Nombre del feature o sistema]

## Setup

- [ ] 1. [Configuración inicial del proyecto]
  - ...
  - _Requirements: -_

## Data Model

- [ ] 2. [Crear schema y migración de ...]
  - ...
  - _Requirements: X.Y_

## Data Access Layer

- [ ] N. ...

## Business Logic

- [ ] N. ...

## API / Interface

- [ ] N. ...

## UI / Client

- [ ] N. ...

## Integration Tests (E2E)

- [ ] N. Tests E2E del flujo completo "[nombre]"
  - ...
  - _Requirements: X.Y, X.Z, ..._

## Documentation

- [ ] N. ...
```

En modo vertical los headers son `## 0. Walking Skeleton` + `## Slice N` (cada slice cruza capas y cierra demostrable de punta a punta). En modo layered los headers son **por capa arquitectónica** (Setup → Data → ... → Docs). En AMBOS modos las dependencias técnicas se respetan y la trazabilidad EARS es idéntica: solo cambia el AGRUPAMIENTO, nunca la cobertura.

## 5. Patrones útiles

### Tareas spike (investigación)

Cuando hay incertidumbre técnica genuina. Formato:

```markdown
- [ ] N. Spike: investigar [pregunta concreta]
  - Pregunta a responder: [una línea, sin ambigüedad]
  - Output esperado: mini-ADR agregado a design.md
  - Timebox: [horas máximo]
  - _Requirements: -_
```

Las spikes NO entregan código de producción. Solo investigación + decisión.

### Tareas de refactor preventivo

Cuando una tarea futura va a tocar código existente que está sucio:

```markdown
- [ ] N. Refactor preventivo: limpiar [módulo X] antes de tarea N+M
  - Extraer [Y] a su propio módulo
  - Renombrar [Z] a [nombre claro]
  - Sin cambio de comportamiento (tests existentes siguen pasando)
  - _Requirements: -_
```

### Tareas de validación intermedia

Cada 4-5 tareas de implementación, una tarea explícita:

```markdown
- [ ] N. Validar integración tareas 1-5
  - Correr suite completa de tests hasta este punto
  - Verificar criterios EARS [X.Y, X.Z, ...] manualmente con caso de uso real
  - _Requirements: X.Y, X.Z_
```

Atrapa drift temprano.

### Tareas opcionales

Marcadas explícitamente para versión MVP:

```markdown
- [ ] N. (opcional) Agregar caching de [recurso]
  - ...
  - _Requirements: X.W_ (criterio de performance, no funcional)
```

Permite arrancar con MVP rápido y endurecer después.

## 6. Cómo se EJECUTA tasks.md

### Patrón correcto

1. Leer la siguiente tarea pendiente.
2. **Conversación nueva** con el agente codificador, contexto mínimo enfocado (la tarea + design relevante + requirements relevantes).
3. El agente ejecuta SOLO esa tarea.
4. **El humano revisa el resultado** (no el agente).
5. Iterar dentro de esa conversación hasta que esté bien.
6. Marcar `[x]`, cerrar conversación.
7. Conversación nueva para la siguiente tarea.

### Anti-patrón fatal

Meter todo `tasks.md` al agente con "ejecuta todo". Rompe por:

- Pérdida de contexto a la mitad
- Decisiones inconsistentes entre tareas
- Propagación de errores sin revisión
- Imposibilidad de rollback granular

Una tarea = una sesión = una revisión humana = un `[x]`. Sin atajos.

## 7. Anti-patrones que matan tasks.md

- ❌ **Tareas demasiado grandes**: el agente "completa" pero pierde contexto a la mitad.
- ❌ **Tests como sub-pasos**: se recortan bajo presión.
- ❌ **Orden por valor en vez de dependencias**: UI antes que la lógica que la UI consume → bloqueo.
- ❌ **Tareas sin footer de trazabilidad**: no se puede auditar el cierre del feature.
- ❌ **Verbos vagos**: "Trabajar en X", "Hacer Y" → alcance abierto, completitud subjetiva.
- ❌ **Tareas redundantes "por completitud"**: el agente las mete y el humano no las poda. Resultado: pierdes horas en lo que no aporta.
- ❌ **Sin criterio de hecho**: el agente marca `[x]` con código que no funciona.

## 8. Checklist de auto-validación (OBLIGATORIO antes de cerrar)

### Estructura

- [ ] El agrupamiento corresponde a `delivery_strategy`:
  - **vertical (default)**: headers `## 0. Walking Skeleton` + `## Slice N`; cada slice cruza capas (datos → lógica → API → UI + tests) y cierra con "el sistema corre y la feature [X] es demostrable de punta a punta".
  - **layered**: headers por capa arquitectónica (Setup, Data Model, Data Access, Business Logic, API, UI, E2E, Docs), solo para infraestructura/migración/refactor sin UI, justificado en design.md.
- [ ] Numeración secuencial sin huecos.

### Por cada tarea

- [ ] Tiene checkbox `- [ ]` al inicio.
- [ ] Tiene verbo de acción concreto (Implementar/Crear/Modificar/etc.), NO vago.
- [ ] Tiene al menos un sub-paso concreto.
- [ ] Tiene línea explícita de "Criterio de hecho".
- [ ] Tiene footer `_Requirements: X.Y, ...` (puede ser `-` para setup).
- [ ] Es completable en una sesión (estimado: 1-3 archivos, 50-200 líneas).

### Orden y cobertura

- [ ] Las dependencias técnicas se respetan (datos → lógica → API → UI) — en modo vertical, DENTRO de cada slice; en modo layered, en todo el archivo.
- [ ] En modo vertical: existe el Walking Skeleton antes de cualquier slice, y cada slice cierra con su criterio "demostrable de punta a punta".
- [ ] La trazabilidad EARS es idéntica en ambos modos: solo cambió el agrupamiento, no la cobertura. Cada criterio EARS del requirements.md aparece referenciado en al menos una tarea.
- [ ] No hay criterios EARS huérfanos (sin tarea que los implemente).
- [ ] No hay tareas sin justificación en design.md o requirements.md.

### Tests

- [ ] Hay tareas de tests INDEPENDIENTES, no como sub-pasos.
- [ ] Hay al menos una tarea de tests E2E al final que cubre el flujo integrador.

### Disciplina

- [ ] Ninguna tarea menciona implementación detallada (eso queda para el agente codificador en su sesión).
- [ ] Tareas paralelizables están marcadas explícitamente (`3a`, `3b`).
- [ ] Tareas opcionales están marcadas `(opcional)`.

## 9. Cuando el output NO está listo

Si después de la auto-validación queda CUALQUIER ítem sin marcar:

1. **NO entregues el tasks.md**.
2. Reporta al humano qué ítems fallaron.
3. Itera hasta que el checklist esté satisfecho.

Tasks.md mal hecho es la causa #1 de fallas en ejecución SDD. Una hora afinándolo ahorra cinco horas de errores durante el desarrollo.
