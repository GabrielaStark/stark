---
description: Fase 2 · Levanta los requirements (specs). Enruta al analista correcto según el caso de uso.
argument-hint: [slug-feature en mantenimiento]
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras antes de actuar.

Determina el caso de uso y enruta:

- NUEVO → Use the analista-entrevistas subagent to produce `docs/requirements.md`.
- REINGENIERÍA → Use the arqueologo-codigo subagent to produce `docs/requirements.md`.
- MANTENIMIENTO → Use the analista-feature-mantenimiento subagent to produce `docs/features/$ARGUMENTS/requirements.md`, con delta, Surface of Contact e Invariantes Preservadas.

Gate humano: nada avanza a la siguiente fase sin aprobación explícita del requirements producido.
