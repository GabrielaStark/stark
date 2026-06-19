---
description: Fase 5 · Descompone el design en tareas ejecutables. Vertical slices (construcción) o por riesgo (mantenimiento).
argument-hint: [slug-feature en mantenimiento]
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras.

Pre-condición: el design debe estar aprobado por el humano. Si no lo está, detente y pídelo.

Enruta según el caso de uso:

- **NUEVO / REINGENIERÍA** → Use the descompositor-tareas subagent to produce `docs/tasks.md`. Estructura en rebanadas verticales: `## 0. Walking Skeleton` seguido de `## Slice N`, salvo que el design declare `delivery_strategy: layered`.

- **MANTENIMIENTO** → Use the descompositor-riesgo-mantenimiento subagent to produce `docs/features/$ARGUMENTS/tasks.md`. Ordena por riesgo de regresión: Regression Shield primero, No-Regression Validation al final.

Al terminar, recuerda al humano que tasks.md requiere su aprobación antes de pasar a la fase 6 (build).
