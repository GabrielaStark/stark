---
name: sdd-tasks-risk
description: Use this skill whenever generating, validating, or editing a tasks.md file for the SDD MAINTENANCE pipeline (adding a feature to a production system). Defines task anatomy (checkbox, sequential number, action verb, sub-steps, references, EARS + invariant traceability footer), the canonical risk-ordered structure (Regression Shield FIRST → Data Delta → Backend Delta → Frontend Delta → Integration → E2E → No-Regression Validation), the five operational rules, useful patterns (spike, regression test creation, integration tasks, optional tasks), execution discipline (one task per agent session), and the mandatory validation checklist. Trigger whenever the task involves transforming an approved delta design.md into a tasks.md for maintenance. NOT for greenfield or brownfield-rewrite — use sdd-tasks for those.
---

# SDD Tasks Risk — Constitución

Este skill es la fuente de verdad para producir `docs/features/<feature>/tasks.md` en el pipeline de **mantenimiento** del framework stark. El subagente `descompositor-riesgo-mantenimiento` consulta este archivo. Cualquier `tasks.md` producido en este pipeline debe cumplir TODAS las reglas de aquí.

## 1. Propósito del tasks.md de mantenimiento

Es la **descomposición ejecutable** del `design.md` delta en unidades atómicas que el agente codificador procesa una por una, **ordenadas por riesgo de regresión** (no por capa arquitectónica).

- **NO** es un Gantt.
- **NO** es un plan de proyecto con fechas.
- **NO** es una lista de épicas.

**SÍ** es una secuencia ordenada de tareas pequeñas, autocontenidas, verificables, atadas a criterios EARS del delta **y** a invariantes preservadas del sistema.

**Diferencia crítica vs `sdd-tasks` (construcción):**

- El orden NO es por capa arquitectónica (Setup → Data Model → ... → UI). En mantenimiento eso es irrelevante: el Setup ya existe, el Data Model ya existe, etc.
- El orden **es por riesgo**: primero blindar lo existente con tests, luego construir el delta de menor a mayor superficie de contacto, terminar con validación de no-regresión.
- Cada tarea atada a invariantes además de criterios EARS.

## 2. Anatomía obligatoria de una tarea

Cada tarea en `tasks.md` SIEMPRE tiene esta estructura:

```markdown
- [ ] N. [Verbo acción] [objeto concreto]
  - [Sub-paso 1: archivos a tocar / patrón a aplicar]
  - [Sub-paso 2]
  - [Sub-paso 3]
  - Criterio de hecho: [cómo se sabe que terminó]
  - _Requirements: X.Y, X.Z_ | _Invariants: I.A, I.B_
```

### Elementos por elemento

#### Checkbox `- [ ]` y número secuencial `N.`

- Idénticos a `sdd-tasks`. Tareas se ejecutan en orden numérico.
- Paralelizables: sufijo letra (`3a`, `3b`).

#### Verbo de acción

- Concreto y acotado. Lista permitida (extiende sdd-tasks):
  - `Implementar` — código nuevo
  - `Crear` — archivo/recurso nuevo
  - `Modificar` — código existente
  - `Agregar` — extensión a algo existente
  - `Refactorizar` — reorganizar sin cambiar comportamiento
  - `Configurar` — setup de dependencia nueva
  - `Validar` — verificación cruzada
  - `Documentar` — escritura de docs
  - **`Blindar`** — escribir tests de regresión sobre código existente que se va a tocar (nuevo verbo, exclusivo de mantenimiento)
  - **`Verificar regresión`** — ejecutar suite completa y validar invariantes (nuevo verbo)

- ❌ Prohibidos: "Trabajar en", "Hacer", "Investigar" (excepto en spikes formales).

#### Sub-pasos

- El "cómo" mínimo.
- Bullets concretos: qué archivos tocar, qué patrón aplicar.
- Referencia explícita a componentes existentes que se usan (sin reinventar).
- Para tareas de `Modificar`, indicar explícitamente QUÉ se modifica Y QUÉ no.

#### Criterio de hecho

- Línea explícita que dice cómo se verifica completitud.
- Para tareas de `Blindar`: "test pasa contra el código actual sin cambios + cubre invariante I.X".
- Para tareas de `Modificar`: "el comportamiento nuevo funciona Y los tests de blindaje siguen pasando".
- Para tareas de `Verificar regresión`: "suite completa pasa + todas las invariantes verificadas".

#### Footer de trazabilidad doble

- Formato exacto: `_Requirements: X.Y, X.Z_ | _Invariants: I.A, I.B_`
- `_Requirements:_` lista los criterios EARS del delta que la tarea cumple. Puede ser `-` si la tarea es de blindaje pura o de validación.
- `_Invariants:_` lista las invariantes que la tarea afecta o blinda. Puede ser `-` si la tarea no toca código existente.
- **Mínimo uno de los dos debe tener referencia.** Si ambos son `-`, la tarea no se justifica.

## 3. Las 5 reglas operacionales

### Regla 1: Una tarea = una sesión del agente

- Heurística: 1-3 archivos tocados, 50-200 líneas. Idéntica a sdd-tasks.

### Regla 2: Orden por RIESGO de regresión, NO por capa

- **Primero**: blindar lo existente con tests (sección `## Regression Shield`).
- **Después**: implementar el delta de menor a mayor superficie de contacto.
- **Al final**: validar no-regresión (sección `## No-Regression Validation`).

Secuencia canónica:
1. Regression Shield (blindar invariantes sin tests existentes)
2. Spike (opcional, si hay incertidumbre técnica del delta)
3. Data Model Delta (migraciones nuevas, compatibles hacia atrás)
4. Backend Delta (servicios, repos, lógica nueva)
5. API Delta (endpoints nuevos o extensiones)
6. Frontend Delta (UI nueva o extensiones)
7. Integration (puntos donde el delta se conecta con flujos existentes — tareas chicas y aisladas)
8. E2E del feature (flujo completo del delta + coexistencia con lo existente)
9. No-Regression Validation (suite completa + invariantes)
10. Documentation (actualizar docs afectadas)

### Regla 3: Tests existentes deben pasar ANTES de empezar a modificar

- La tarea 1 del Regression Shield (o equivalente) es: ejecutar suite completa de tests del módulo a tocar.
- Si NO pasan limpiamente antes de tocar nada, **detenerse** y avisar al humano. El sistema está roto independientemente del feature; resolver eso primero.

### Regla 4: Criterio explícito de "hecho" en cada tarea

- Compila + lint clean + tests específicos pasan + criterio EARS verificable + invariantes referenciadas siguen pasando.

### Regla 5: Tests del delta como tareas independientes, NO como sub-pasos

- Mismo principio que `sdd-tasks` Regla 4.
- Tests de regresión para blindaje son tareas con verbo `Blindar` en la sección Regression Shield.
- Tests del feature nuevo son tareas con verbo `Implementar tests para...` en su capa correspondiente.

## 4. Estructura del archivo

```markdown
# Tasks: [Nombre del feature]

> Feature de mantenimiento sobre `<nombre-sistema>`. Orden por riesgo de regresión.

## Regression Shield

[Tareas de blindaje: tests de regresión sobre componentes existentes
que el delta va a tocar. Estas tareas se ejecutan ANTES de cualquier
modificación al código de producción. Se derivan de la tabla
"Tests Existentes a Preservar" del requirements + de la tabla
"Invariantes preservadas" del design.]

- [ ] 1. Verificar que la suite existente pasa contra `[módulos afectados]`
  - Ejecutar `[comando de tests del módulo]`
  - Si falla, detener y reportar al humano
  - Criterio de hecho: todos los tests existentes pasan en verde sin tocar nada
  - _Requirements: -_ | _Invariants: -_ (tarea estructural de gate)

- [ ] 2. Blindar [invariante I.X] con test de regresión nuevo
  - Crear test en `[archivo_test]`
  - Cubrir el comportamiento descrito en I.X usando la fuente de código referenciada
  - Criterio de hecho: test pasa contra el código actual sin modificaciones
  - _Requirements: -_ | _Invariants: I.X_

- [ ] 3. Blindar [invariante I.Y] con test de regresión nuevo
  - ...
  - _Requirements: -_ | _Invariants: I.Y_

## Spike (opcional, si hay incertidumbre técnica)

- [ ] N. Spike: investigar [pregunta concreta]
  - Pregunta a responder: [una línea]
  - Output esperado: mini-ADR agregado a design.md sección 5
  - Timebox: [horas máximo]
  - _Requirements: -_ | _Invariants: -_

## Data Model Delta

[Solo si el delta toca el schema. Migraciones compatibles hacia atrás.]

- [ ] N. Crear migración [nombre]
  - Archivo: `[ruta_migración]`
  - ALTER TABLE ... compatible (DEFAULT explícito si NOT NULL)
  - Criterio de hecho: migración aplica limpiamente en BD de prueba + rollback funciona
  - _Requirements: X.Y_ | _Invariants: I.Z (compatibilidad hacia atrás)_

## Backend Delta

- [ ] N. Implementar [servicio/repo nuevo]
  - Archivos: ...
  - Patrón a aplicar: [el patrón existente del sistema, citado del design]
  - Criterio de hecho: unit tests del módulo nuevo pasan
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+1. Tests unit del [servicio nuevo]
  - Casos: ...
  - _Requirements: X.Y_ | _Invariants: -_

## API Delta

[Endpoints nuevos o extensiones a existentes.]

- [ ] N. Implementar endpoint [nuevo]
  - ...
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+1. Modificar endpoint [existente] para extender con [delta]
  - **Preservar comportamiento sin el query param/header nuevo (invariante I.A)**
  - Agregar rama para el caso nuevo
  - Criterio de hecho: tests existentes pasan Y tests nuevos del caso extendido pasan
  - _Requirements: X.Y_ | _Invariants: I.A_

- [ ] N+2. Tests de integración del endpoint
  - ...

## Frontend Delta

[Si aplica.]

- [ ] N. Implementar [componente UI nuevo]
- [ ] N+1. Tests del componente
- [ ] N+2. Integrar [componente] en [vista existente] sin alterar resto de la vista
  - _Invariants: I.B (resto de la vista renderiza igual)_

## Integration

[Puntos de coexistencia con flujos existentes. Cada uno es una tarea aislada
de alto riesgo. NO mezclar varios puntos de integración en una sola tarea.]

- [ ] N. Integrar [delta] con [flujo existente]
  - Punto de inserción: [archivo:línea o describir]
  - Garantía: el flujo existente sin la rama nueva se ejecuta idéntico
  - Criterio de hecho: tests del flujo existente siguen pasando + caso nuevo cubierto
  - _Requirements: X.Y_ | _Invariants: I.C_

## Integration Tests (E2E del feature)

- [ ] N. Tests E2E del flujo completo "[nombre del feature]"
  - Caso éxito: payload válido → 201
  - Caso error: payload inválido → 400 con error tipado
  - Caso edge: [específico del feature]
  - Caso coexistencia: flujo existente sin tocar el feature sigue funcionando
  - _Requirements: X.Y, X.Z, ..._ | _Invariants: I.A, I.C_

## No-Regression Validation

[Tarea final obligatoria antes de cerrar el feature. Verifica que ninguna
invariante se rompió.]

- [ ] N. Verificar regresión: suite completa + invariantes
  - Ejecutar TODA la suite de tests del repo
  - Verificar manualmente cada invariante de `requirements.md`
  - Para cada invariante: ¿el test sigue pasando? ¿el comportamiento es idéntico?
  - Si hay alguna invariante violada, **detener cierre** y reportar
  - Criterio de hecho: 100% de tests pasan + cada invariante verificada
  - _Requirements: -_ | _Invariants: I.1, I.2, ..., I.N (todas)_

## Documentation

- [ ] N. Actualizar `docs/BIG_PICTURE.md` si la arquitectura del sistema cambió
  - Si el delta agregó componentes/módulos nuevos visibles, reflejarlo
  - Si no hubo cambio de alto nivel, marcar como N/A y omitir
  - _Requirements: -_ | _Invariants: -_

- [ ] N+1. Actualizar `docs/REGLAS_DE_NEGOCIO.md` si el delta introdujo regla nueva
  - Agregar la regla con referencia al código nuevo
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+2. Actualizar README del módulo afectado
  - _Requirements: -_ | _Invariants: -_
```

Los headers de sección son **por riesgo de regresión y secuencia de seguridad**, no por capa arquitectónica. Esto es lo que distingue este pipeline.

## 5. Patrones útiles específicos de mantenimiento

### Tareas de blindaje sin test existente

Cuando una invariante referencia un comportamiento que no tiene test:

```markdown
- [ ] N. Blindar I.X — comportamiento de `[componente]` sin test actual
  - Crear `[archivo_test]` con caso(s) que ejerciten el código referenciado en I.X
  - Usar el comportamiento ACTUAL como ground truth (no inventar lo que "debería hacer")
  - Si al escribir el test descubres comportamiento ambiguo, **detener** y consultar al humano
  - Criterio de hecho: test pasa contra el código sin modificaciones
  - _Requirements: -_ | _Invariants: I.X_
```

### Tareas de modificación con preservación explícita

Cuando se modifica código existente:

```markdown
- [ ] N. Modificar `ReportController.getReport` para soportar `?format=pdf`
  - Agregar rama: si `format == "pdf"` → invocar `pdfExporter.export(reportId)`
  - **Preservar**: comportamiento sin `format` o con `format=json` exactamente igual a hoy
  - Verificar: tests existentes `ReportControllerTest.*` siguen pasando
  - Criterio de hecho: tests viejos pasan + caso nuevo `format=pdf` cubierto
  - _Requirements: 1.1_ | _Invariants: I.1_
```

### Tareas de integración aisladas

Cada punto de coexistencia es una tarea propia, no se agrupan:

**MAL**:
```markdown
- [ ] N. Integrar feature con sistema existente
  - Conectar con auth
  - Conectar con notifications
  - Conectar con audit
```

**BIEN**:
```markdown
- [ ] N. Integrar [delta] con auth (rol-based access)
  - Garantía: I.3 (autorización por rol no cambia)
  - _Invariants: I.3_

- [ ] N+1. Integrar [delta] con notifications
  - Garantía: I.5 (notificaciones existentes no cambian)
  - _Invariants: I.5_

- [ ] N+2. Integrar [delta] con audit log
  - Garantía: I.7 (eventos auditados existentes no cambian)
  - _Invariants: I.7_
```

### Tareas opcionales para MVP del feature

```markdown
- [ ] N. (opcional) Agregar caching de [recurso del feature]
  - Solo si la performance del feature en prod lo requiere
  - _Requirements: X.W (NFR de performance)_ | _Invariants: -_
```

## 6. Cómo se EJECUTA tasks.md de mantenimiento

### Patrón correcto

Idéntico a sdd-tasks: una tarea = una sesión = una revisión humana = un `[x]`.

Diferencias específicas de mantenimiento:

1. **Antes de empezar la tarea 1**: confirmar que el repo está en estado limpio + suite completa de tests pasa. Si no, detener.
2. **Después de cada tarea de Modificación**: ejecutar tests del módulo modificado **antes** de marcar `[x]`. Si rompió algo existente, no marcar.
3. **No saltar la sección No-Regression Validation**: aunque "todo se ve bien", ejecutar la tarea final completa antes de cerrar.

### Anti-patrón fatal

Mismo que sdd-tasks: "ejecuta todo tasks.md" rompe garantizado. Además, en mantenimiento añade:

- ❌ Saltar el Regression Shield porque "no hay tiempo" → garantiza que descubras regresiones en producción.
- ❌ Marcar tareas como completas sin haber corrido los tests del módulo afectado.
- ❌ Modificar código existente sin haber escrito antes el test de blindaje correspondiente.

## 7. Anti-patrones que matan tasks.md de mantenimiento

- ❌ **Orden por capa arquitectónica**: en mantenimiento el orden es por riesgo, no por capa. Si tu tasks.md empieza con "Setup", está mal.
- ❌ **Saltar Regression Shield**: tareas de blindaje primero, sin excepción.
- ❌ **Tareas de integración agrupadas**: cada punto de coexistencia es una tarea propia.
- ❌ **Olvidar la trazabilidad doble**: cada tarea con `_Requirements:_` Y `_Invariants:_` (o explícitamente `-`).
- ❌ **Saltar No-Regression Validation**: la última tarea es obligatoria.
- ❌ **Tareas grandes** que mezclan modificación + creación: dividir por superficie de contacto.
- ❌ **Modificar código sin blindar primero**: el test de regresión va antes que la modificación.

## 8. Checklist de auto-validación (OBLIGATORIO antes de cerrar)

### Estructura

- [ ] El archivo está organizado por las 10 secciones canónicas (Regression Shield → ... → Documentation), en orden.
- [ ] Numeración secuencial sin huecos.
- [ ] Sección "Regression Shield" existe y tiene al menos 1 tarea (mínimo: verificar que la suite existente pasa).
- [ ] Sección "No-Regression Validation" existe y tiene la tarea final de verificación de invariantes.

### Por cada tarea

- [ ] Tiene checkbox `- [ ]` al inicio.
- [ ] Tiene verbo de acción concreto (incluye `Blindar` y `Verificar regresión` cuando aplique).
- [ ] Tiene al menos un sub-paso concreto.
- [ ] Tiene línea explícita de "Criterio de hecho".
- [ ] Tiene footer con `_Requirements:_` Y `_Invariants:_`.
- [ ] Al menos uno de los dos del footer tiene referencia (no ambos `-`).
- [ ] Es completable en una sesión (1-3 archivos, 50-200 líneas).

### Cobertura

- [ ] Cada criterio EARS del requirements.md del delta aparece referenciado en al menos una tarea de implementación.
- [ ] Cada invariante del requirements.md aparece referenciada en al menos una tarea (de Regression Shield o de modificación).
- [ ] Cada invariante sin test existente tiene su tarea de blindaje en Regression Shield.
- [ ] Cada fila de Surface of Contact con riesgo medio/alto tiene tarea(s) específica(s) que la tratan.

### Disciplina de mantenimiento

- [ ] Las tareas de blindaje (`Blindar`) van ANTES de las tareas de modificación del módulo correspondiente.
- [ ] Las tareas de `Modificar` declaran explícitamente qué preservar.
- [ ] Tareas de integración son aisladas (una por punto de coexistencia).
- [ ] La tarea final de No-Regression Validation está presente y verifica TODAS las invariantes.

### Tests

- [ ] Tests del delta son tareas INDEPENDIENTES, no sub-pasos.
- [ ] Tests de blindaje son tareas con verbo `Blindar`, en Regression Shield.
- [ ] Hay al menos una tarea de E2E del feature.

## 9. Cuando el output NO está listo

Si después de la auto-validación queda CUALQUIER ítem sin marcar:

1. **NO entregues el tasks.md**.
2. Reporta al humano qué ítems fallaron.
3. Itera hasta que el checklist esté satisfecho.

Tasks.md de mantenimiento mal hecho es la causa #1 de regresiones en producción. Una hora afinándolo ahorra una semana de hotfixes.
