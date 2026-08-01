---
description: Fase 3 · Prototipo visual para validar la UI con el cliente. Standalone o como fase del flujo.
argument-hint: "[slug-feature en mantenimiento]"
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras: especifica todo, construye lo mínimo; cada línea gana su lugar.

El prototipo es transversal y opcional, pero ciudadano de primera (Fase 3). Detecta en cuál de los dos modos operas:

- **STANDALONE** — el prototipo ES el encargo. Arranca del requirements ligero aprobado (si no existe, primero `/stark-requirements` en modo ligero — el prototipador no arranca sin requirements) y entrega un mockup desplegable para validar la idea.
- **FASE 3 DEL FLUJO** — vienes tras un requirements aprobado. Valida la UI con el cliente ANTES de pasar a diseño.

Pre-condición (ambos modos): el requirements del que partes debe estar aprobado y sellado. Verifícalo: `python3 .claude/scripts/sello.py verificar-doc <ruta-del-requirements>`. Si falla, detente: se aprueba y sella antes de prototipar.

Enruta al subagente: Use the prototipador-visual subagent to produce the deployable mockup.

Destino del artefacto:
- Nuevo / reingeniería → `docs/prototype/`
- Mantenimiento → `docs/features/$ARGUMENTS/prototype/`

Itera con el cliente vía `validation-log`: cada ronda de feedback se registra y se incorpora.

Gate estructural: si el feedback es estructural (nueva entidad, actor o flujo), NO lo absorbas en HTML. Vuelve a `/stark-requirements` y deja que el cambio fluya por las fases — el requirements corregido se re-aprueba con el humano y se re-sella con `sellar-doc ... --re-sellar` (el sello viejo quedó invalidado por el cambio, y eso es correcto). El prototipo refleja la UI; no inventa el modelo.
