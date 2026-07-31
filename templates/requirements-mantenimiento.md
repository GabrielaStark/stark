<!--
TEMPLATE: requirements.md de mantenimiento — esqueleto de referencia.
FUENTE ÚNICA de estructura, reglas y checklist: .claude/skills/sdd-requirements-mantenimiento/SKILL.md
Este artefacto lo GENERA el agente analista-feature-mantenimiento desde el skill.
-->

# Requirements: [Nombre del feature]

> Feature de mantenimiento sobre `<nombre-sistema>`. Describe **el delta**, no el sistema completo.
> Ruta: [corta|completa] — justificación: [superficie tocada, criterios de DECISIONES.md B-D13]

> Estado: PENDIENTE  <!-- al aprobar, el gate corre sello.py: estampa "Aprobado por..." aquí y genera el receipt (sha256) en docs/.stark/receipts/ -->

## Contexto

## Surface of Contact

| Elemento del sistema | Tipo | Qué se hace | Riesgo |
|---|---|---|---|

## Invariantes Preservadas

1. **I.1** (`estado`) — [comportamiento en lenguaje testeable]. <!-- source: archivo:líneas -->

## Decisiones sobre hallazgos en-duda

| Hallazgo | Decisión | Quién decidió | Fecha |
|---|---|---|---|
<!-- Decisión ∈ {preservar por alcance, corregir dentro del cambio, diferir} -->

## Requirements (del delta)

## Non-Functional Requirements (del delta)

## Behavior Replaced

## Tests Existentes a Preservar

## Out of Scope (del feature)

## Open Questions

## Glossary

<!-- RUTA CORTA: este mismo archivo incorpora "## Encaje de diseño" y "## Tasks por riesgo".
     Ver skill sdd-requirements-mantenimiento §4.6 y DECISIONES.md B-D13 -->
