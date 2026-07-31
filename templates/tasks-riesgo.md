<!--
TEMPLATE: tasks.md de mantenimiento — esqueleto de referencia.
FUENTE ÚNICA de estructura, anatomía y checklist: .claude/skills/sdd-tasks-risk/SKILL.md
Este artefacto lo GENERA el agente descompositor-riesgo-mantenimiento desde el skill.
Orden por riesgo de regresión; footer doble _Requirements: X.Y_ | _Invariants: I.A_.
-->

# Tasks: [Nombre del feature]

> Aprobado por [nombre] — YYYY-MM-DD  <!-- sello: lo estampa el gate al aprobar; sin sello no está aprobado -->

## Regression Shield
<!-- Al cerrar cada lote aprobado, /stark-build estampa bajo su header:
     > Lote validado: commit <hash> — Tests: PASS — Invariantes: PASS — aprobado por [nombre] el YYYY-MM-DD -->

- [ ] 1. Verificar que la suite existente pasa contra los módulos afectados
- [ ] 2. Blindar I.1 — [invariante sin test]

## Spike (opcional)

## Data Model Delta

## Backend Delta

## API Delta

## Frontend Delta

## Integration

## Integration Tests (E2E del feature)

## Documentation

## No-Regression Validation

- [ ] N. Verificar regresión: suite completa + TODAS las invariantes (SIEMPRE la última)
