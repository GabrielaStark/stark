---
description: Fase 3 · Prototipo visual para validar la UI con el cliente. Standalone o como fase del flujo.
argument-hint: "[slug-feature en mantenimiento]"
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras: especifica todo, construye lo mínimo; cada línea gana su lugar.

El prototipo es transversal y opcional, pero ciudadano de primera (Fase 3). Detecta en cuál de los dos modos operas:

- **STANDALONE** — el prototipo ES el encargo. Arranca de un requirements ligero (o lo que el cliente describa) y entrega un mockup desplegable para validar la idea.
- **FASE 3 DEL FLUJO** — vienes tras un requirements aprobado. Valida la UI con el cliente ANTES de pasar a diseño.

Enruta al subagente: Use the prototipador-visual subagent to produce the deployable mockup.

Destino del artefacto:
- Nuevo / reingeniería → `docs/prototype/`
- Mantenimiento → `docs/features/$ARGUMENTS/prototype/`

Itera con el cliente vía `validation-log`: cada ronda de feedback se registra y se incorpora.

Gate estructural: si el feedback es estructural (nueva entidad, actor o flujo), NO lo absorbas en HTML. Vuelve a `/stark-requirements` y deja que el cambio fluya por las fases. El prototipo refleja la UI; no inventa el modelo.
