---
description: Fase 4 · Diseño técnico. Enruta a arquitecto (nuevo/reingeniería) o delta (mantenimiento).
argument-hint: "[slug-feature en mantenimiento]"
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras antes de actuar.

Pre-condición: el requirements de esta fase debe estar aprobado. Verifícalo: `python3 .claude/scripts/sello.py verificar-doc <ruta-del-requirements>` — comprueba que el contenido actual coincide (sha256) con la versión aprobada. Si falla (receipt ausente, o el documento cambió después de aprobarse), detente: se re-aprueba y re-sella antes de seguir. Si el requirements vigente fue LIGERO (modo prototipo), tampoco basta: complétalo a full con `/stark-requirements`, re-apruébalo y re-séllalo antes de diseñar — una spec deliberadamente incompleta no pasa a construcción.

Enruta según el caso de uso:

- NUEVO / REINGENIERÍA → Use the disenador-arquitecto subagent to produce `docs/design.md`.
- MANTENIMIENTO → Use the disenador-delta-mantenimiento subagent to produce `docs/features/$ARGUMENTS/design.md`, diseñando solo el delta sobre la arquitectura heredada e inmutable.

El campo `delivery_strategy` del Overview del design (`vertical` por defecto | `layered`) gobierna cómo se descompondrá en la Fase 5; déjalo explícito. Aplica solo a construcción (nuevo/reingeniería): en mantenimiento el orden es siempre por riesgo de regresión y el design delta no lo declara.

Gate humano: nada avanza a la Fase 5 sin aprobación explícita del design producido. Al recibirla, sella el documento: `python3 .claude/scripts/sello.py sellar-doc <ruta-del-design> --por "<nombre>"` — estampa el header y genera el receipt (sha256) en `docs/.stark/receipts/`; commitea ambos. Sin receipt válido, el documento no cuenta como aprobado.
