---
description: Fase 4 · Diseño técnico. Enruta a arquitecto (nuevo/reingeniería) o delta (mantenimiento).
argument-hint: [slug-feature en mantenimiento]
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras antes de actuar.

Pre-condición: el requirements de esta fase debe estar aprobado por el humano. Si no lo está, detente y pídelo.

Enruta según el caso de uso:

- NUEVO / REINGENIERÍA → Use the disenador-arquitecto subagent to produce `docs/design.md`.
- MANTENIMIENTO → Use the disenador-delta-mantenimiento subagent to produce `docs/features/$ARGUMENTS/design.md`, diseñando solo el delta sobre la arquitectura heredada e inmutable.

El campo `delivery_strategy` del Overview del design (`vertical` por defecto | `layered`) gobierna cómo se descompondrá en la Fase 5; déjalo explícito.
