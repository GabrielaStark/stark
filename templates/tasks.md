<!--
TEMPLATE: tasks.md — esqueleto de referencia.
FUENTE ÚNICA de estructura, anatomía de tarea y checklist: .claude/skills/sdd-tasks/SKILL.md
Este artefacto lo GENERA el agente descompositor-tareas desde el skill.
delivery_strategy vertical (default): Walking Skeleton + Slices; layered: por capa (solo justificado).
-->

# Tasks: [Nombre del feature o sistema]

> Estado: PENDIENTE  <!-- al aprobar, el gate corre sello.py: estampa "Aprobado por..." aquí y genera el receipt (sha256) en docs/.stark/receipts/ -->

## 0. Walking Skeleton
<!-- Al cerrar cada lote aprobado, /stark-build lo sella con un annotated tag
     (sello.py sellar-lote): la autoridad es el tag sobre el commit validado,
     no una línea aquí. El hook pre-push bloquea el push de commits sin sellar. -->

- [ ] 1. [Verbo] [objeto concreto]
  - [Sub-pasos: archivos a tocar / patrón a aplicar]
  - Criterio de hecho: [cómo se sabe que terminó]
  - _Requirements: -_

## Slice 1: [feature de mayor valor/riesgo]

- [ ] N. [Verbo] [objeto]   (datos → lógica → API → UI + tests, en ese orden)
  - ...
  - _Requirements: X.Y_

## Slice 2: [siguiente feature]

## Documentation
