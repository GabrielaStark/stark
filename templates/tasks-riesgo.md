<!--
TEMPLATE: tasks.md de mantenimiento — esqueleto de referencia.
FUENTE ÚNICA de estructura, anatomía y checklist: .claude/skills/sdd-tasks-risk/SKILL.md
Este artefacto lo GENERA el agente descompositor-riesgo-mantenimiento desde el skill.
Orden por riesgo de regresión; footer doble _Requirements: X.Y_ | _Invariants: I.A_.
-->

# Tasks: [Nombre del feature]

> Estado: PENDIENTE  <!-- al aprobar, el gate corre sello.py: estampa "Aprobado por..." aquí y genera el receipt (sha256) en docs/.stark/receipts/ -->

## Regression Shield
<!-- Al cerrar cada lote aprobado, /stark-build lo sella con un annotated tag
     (sello.py sellar-lote --invariantes): la autoridad es el tag sobre el commit
     validado, no una línea aquí. El hook pre-push bloquea commits sin sellar. -->

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
