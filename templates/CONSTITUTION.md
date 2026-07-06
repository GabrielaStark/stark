<!--
TEMPLATE: CONSTITUTION.md
Framework: stark (Spec-Driven Development)

Cópialo a la RAÍZ del repo como `CONSTITUTION.md` y llénalo. Es opcional pero
recomendado: sin él, el diseñador te pregunta el stack en cada proyecto y el
agente codificador no tiene estándares de código que obedecer.

Omite las secciones que no apliquen (Principio 4: nada "por completitud").
-->

# CONSTITUTION — [Nombre del proyecto]

> Decisiones **inmutables** de este proyecto. Complementa a `docs/documentacion/PRINCIPIOS.md`:
> los Principios son la filosofía universal de stark y no se editan por proyecto;
> esta constitución los aterriza en decisiones concretas de ESTE proyecto.
> Jerarquía: **PRINCIPIOS > CONSTITUTION > artefactos (requirements/design/tasks) > código.**

## Reglas de blindaje (no editar esta sección)

1. **Solo el humano edita este archivo.** Ningún agente lo modifica, nunca.
2. Todo agente que lo encuentre lo trata como **restricción dura**: no pregunta lo que ya está decidido aquí y no propone alternativas a lo vetado.
3. Si un requirement, design, tarea o código necesita contradecir algo de aquí, el agente **se DETIENE** y lo reporta como **alerta crítica**. La contradicción se resuelve editando este archivo (el humano) o cambiando el artefacto — nunca ignorándola en silencio.
4. Esta constitución no puede contradecir `PRINCIPIOS.md`. Si lo hace, ganan los Principios y el agente lo alerta.
5. Cada cambio se registra en §8 con fecha y motivo.

## Ámbito según caso de uso

| Caso de uso | Qué aporta este archivo |
|---|---|
| **Nuevo** | Fija stack y decisiones ANTES del design: `disenador-arquitecto` las usa sin preguntar. |
| **Reingeniería** | Igual que nuevo — aquí se fija el stack del sistema **reescrito** (lo que hacía el legacy no obliga). |
| **Mantenimiento** | El stack y la arquitectura **heredados NO van aquí** — viven en `docs/BIG_PICTURE.md` (skill `onboarding`) y son inmutables por definición del pipeline. Aquí van las reglas del cliente/proyecto que ningún delta puede violar: vetos, estándares de código, umbrales de calidad. |
| **Prototipo** | Solo la clave `prototype_deploy` (§7). |

## 1. Stack obligatorio

<!-- Solo construcción (nuevo/reingeniería). En mantenimiento, omite esta
sección y deja la línea de referencia al sustrato. Versiones concretas:
"PostgreSQL 15", no "una base de datos". -->

| Capa | Tecnología | Versión | Nota |
|---|---|---|---|
| Lenguaje | [ej. TypeScript] | [5.x] | |
| Backend | [ej. Fastify] | [4.x] | |
| Frontend | [ej. React] | [18.x] | |
| Base de datos | [ej. PostgreSQL] | [15] | |
| [otra capa] | | | |

<!-- Mantenimiento: -->
<!-- Stack heredado: ver `docs/BIG_PICTURE.md`. No se redecide. -->

## 2. Patrones obligatorios

<!-- Solo patrones que son REGLA, no preferencia. Cada uno con dónde aplica. -->

- **[Patrón]** — [dónde aplica] — [por qué es regla]
- Ej: Repository pattern en todo acceso a datos — ningún SQL fuera de `repositories/`.
- Ej: Errores tipados como enum, integrados a un catálogo único — nunca strings libres.

## 3. Librerías vetadas

| Vetada | Motivo | Alternativa obligatoria |
|---|---|---|
| [ej. moment.js] | [abandonada, pesada] | [date-fns o Temporal] |

## 4. Estándares de código

<!-- Lo que "correcto y eficiente" significa en ESTE proyecto. El agente
codificador aplica esto en CADA tarea de build; /stark-review lo caza en
el diff. Reglas verificables, no deseos ("código limpio" no es una regla). -->

- **Naming**: [convención — ej. inglés en código, español en textos de UI; camelCase funciones, PascalCase tipos]
- **Errores**: [ej. nunca `catch` vacío; todo error se tipifica y se loguea o se propaga — nunca ambos]
- **Validación**: en cliente Y servidor; el servidor es la verdad.
- **Eficiencia**: [reglas concretas del dominio — ej. queries sin N+1, paginación obligatoria en listados, índices para todo WHERE recurrente]
- **Comentarios**: solo restricciones que el código no puede expresar. Nada de comentarios que narran la línea siguiente.
- **[Otra regla del proyecto]**

## 5. Umbrales de calidad (medibles — se verifican al cerrar cada lote)

| Umbral | Valor | Cómo se verifica |
|---|---|---|
| Tests de lógica de negocio | [ej. ≥80% coverage] | [`npm run coverage`] |
| Lint | 0 errores | [`npm run lint`] |
| [Performance del dominio] | [ej. respuesta <200ms p95] | [cómo] |

## 6. Seguridad (endurecimientos específicos del proyecto)

<!-- El Principio 2 ya obliga lo básico. Aquí solo lo específico de este
dominio: qué datos son sensibles y cómo se tratan. -->

- Secretos: solo env vars / [gestor]. Nunca en código, logs ni fixtures.
- Datos sensibles del dominio: [cuáles — ej. RFC, salarios] → [cómo se protegen — ej. nunca en logs, cifrados en reposo]
- [Otra regla]

## 7. Despliegue

- Plataforma: [ej. Railway / VPS / on-prem del cliente]
- `prototype_deploy: [railway|netlify|vercel|cloudflare|github-pages|manual]`

## 8. Registro de cambios

<!-- Una constitución que cambia sin registro no es constitución. -->

| Fecha | Cambio | Motivo | Autorizó |
|---|---|---|---|
| [YYYY-MM-DD] | Versión inicial | — | [nombre] |
