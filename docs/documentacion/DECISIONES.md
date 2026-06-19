# Decisiones de diseño de stark

> ADR que congela las decisiones de diseño detrás de dos piezas de stark: la **fase opcional de prototipado visual** (entre `requirements.md` y `design.md`) y el **caso de uso de mantenimiento** (agregar features a sistemas en producción sin romper lo que ya funciona). Esta es la fuente de verdad sobre el **porqué** de los agentes y skills involucrados (`prototipador-visual` / `sdd-prototype`; `analista-feature-mantenimiento`, `disenador-delta-mantenimiento`, `descompositor-riesgo-mantenimiento` y sus skills). Si los artefactos divergen de este doc, este doc manda hasta que se actualice.

---

## Índice unificado

### Parte A: Fase de Prototipo

- [A1. Propósito](#a1-propósito)
- [A2. Posición en el pipeline](#a2-posición-en-el-pipeline)
- [A3. Decisiones congeladas](#a3-decisiones-congeladas)
- [A4. Estructura del artefacto `docs/prototype/`](#a4-estructura-del-artefacto-docsprototype)
- [A5. Política de despliegue](#a5-política-de-despliegue)
- [A6. Loop iterativo con el cliente](#a6-loop-iterativo-con-el-cliente)
- [A7. Válvula de retorno al analista](#a7-válvula-de-retorno-al-analista)
- [A8. Anti-patrones](#a8-anti-patrones)
- [A9. Cierre (Prototipo)](#a9-cierre-prototipo)

### Parte B: Caso de uso Mantenimiento

- [B1. Propósito](#b1-propósito)
- [B2. Posición en el ecosistema de pipelines de stark](#b2-posición-en-el-ecosistema-de-pipelines-de-stark)
- [B3. Cuándo aplicar este caso de uso (árbol de decisión)](#b3-cuándo-aplicar-este-caso-de-uso-árbol-de-decisión)
- [B4. Decisiones congeladas](#b4-decisiones-congeladas)
- [B5. Estructura del artefacto `docs/features/<feature>/`](#b5-estructura-del-artefacto-docsfeaturesfeature)
- [B6. El sustrato: CLAUDE.md, BIG_PICTURE.md, REGLAS_DE_NEGOCIO.md](#b6-el-sustrato-claudemd-big_picturemd-reglas_de_negociomd)
- [B7. Las tres garantías de no-regresión](#b7-las-tres-garantías-de-no-regresión)
- [B8. Comparación con los otros pipelines](#b8-comparación-con-los-otros-pipelines)
- [B9. Anti-patrones](#b9-anti-patrones)
- [B10. Cierre (Mantenimiento)](#b10-cierre-mantenimiento)

---

# Parte A: Fase de Prototipo

> Decisiones congeladas de la fase opcional de prototipado visual entre `requirements.md` y `design.md`. Fuente de verdad sobre el **porqué** del agente `prototipador-visual` y el skill `sdd-prototype`.

## A1. Propósito

`requirements.md` es texto. El cliente lee texto y asiente. Después ve la UI y dice "no, así no". Esa brecha entre texto aprobado y mental model real es **el problema que esta fase resuelve**.

La fase de prototipo introduce un **mockup interactivo de alta fidelidad** entre `requirements.md` aprobado y `design.md`, desplegado en una URL real que se le muestra al cliente. El cliente valida o pide ajustes; los cambios se reflejan **primero en `requirements.md`** y luego en una nueva iteración del prototipo. Cuando el cliente está convencido, el pipeline continúa hacia `design.md`.

**Lo que la fase NO es**:

- No es código de producción
- No es la decisión de stack (eso sigue siendo de `design.md`)
- No es un wireframe baja-fidelidad (Figma a mano, boxes y líneas)
- No es un prototipo funcional con backend real (los botones no guardan datos)

**Lo que la fase SÍ es**:

- Validación temprana del **qué visual** y del **flujo** con el cliente
- Mecanismo para detectar requisitos faltantes antes de cementarlos en diseño
- Artefacto throwaway, versionado, reemplazable

---

## A2. Posición en el pipeline

```
inputs/ o analysis/
        ↓
[analista | arqueologo] → docs/requirements.md → [gate humano]
        ↓
        ↓  ← ─ ─ ─ válvula de retorno ─ ─ ─ ┐
        ↓                                    │
[prototipador-visual] (opcional)             │
   ↓                                         │
   loop: prototipo ⇄ validation-log ─ ─ ─ ─ ┘
   ↓ (puede actualizar requirements.md)
   ↓
   docs/prototype/ desplegado → [gate cliente: aprobación]
        ↓
[disenador-arquitecto] → docs/design.md → [gate humano]
        ↓
[descompositor-tareas] → docs/tasks.md  → [gate humano]
        ↓
   tarea por sesión → código + tests
```

**Opcionalidad**: la fase se ejecuta solo si el proyecto tiene UI relevante. Backend puro, CLIs y librerías la saltan sin culpa.

**Gate adicional**: el cliente aprueba la versión final del prototipo antes de pasar a `design.md`. Es un gate humano más, no un gate técnico — sigue la disciplina del framework.

---

## A3. Decisiones congeladas

Cada decisión en formato breve: **Decisión · Por qué · Consecuencias negativas aceptadas**.

### A-D1. Fase opcional, no obligatoria

- **Decisión**: la fase se invoca explícitamente cuando el proyecto tiene UI relevante. No se ejecuta automáticamente al cerrar `requirements.md`.
- **Por qué**: no todos los proyectos son UI-driven. Forzar prototipo en un servicio backend infla el pipeline sin valor.
- **Consecuencia aceptada**: requiere criterio humano para decidir si invocarla. No hay flag automático.

### A-D2. Agente separado, no sub-paso del analista

- **Decisión**: `prototipador-visual` es un agente nuevo en `.claude/agents/`, con su propio skill `sdd-prototype`.
- **Por qué**: las responsabilidades son distintas. El analista consolida texto; el prototipador genera HTML. Mezclarlas viola el principio de "un agente, un trabajo bien definido".
- **Consecuencia aceptada**: un archivo más en `.claude/agents/` y uno más en `.claude/skills/`.

### A-D3. Stack del prototipo: HTML estático + Tailwind CDN

- **Decisión**: HTML + Tailwind por CDN + JS vanilla o Alpine.js para interacciones mínimas. Sin build, sin frameworks, sin dependencias instaladas.
- **Por qué**: (1) throwaway por naturaleza — nadie confunde HTML con CDN con código de producción; (2) stack-agnóstico — no contamina la decisión de framework que se toma en `design.md`; (3) cero fricción de setup.
- **Consecuencia aceptada**: techo visual más bajo que v0/Lovable/Figma. Para validación de flujo alcanza; para portafolio de diseñador, no.

### A-D4. Despliegue default: Railway

- **Decisión**: Railway como plataforma default. Server mínimo de Node con `express` + `express-basic-auth` sirviendo la carpeta estática. Credenciales por env vars (`AUTH_USER`, `AUTH_PASS`).
- **Por qué**: el dev ya conoce y usa Railway. Basic auth resuelve privacidad de prototipos con info sensible. Setup en dashboard una vez, redeploy automático con `git push`.
- **Consecuencia aceptada**: dependencia de cuenta Railway. Se mitiga ofreciendo alternativas (ver A5).

### A-D5. Despliegue configurable

- **Decisión**: Railway es default pero el dev puede elegir Netlify, Vercel, Cloudflare Pages, GitHub Pages o despliegue manual. La elección se declara en `CONSTITUTION.md` (si existe) o el agente la pregunta una vez.
- **Por qué**: el framework es de uso genérico. Imponer Railway sería rígido y elimina valor para devs que ya tienen su stack de despliegue.
- **Consecuencia aceptada**: el agente debe mantener instrucciones de `DEPLOY.md` para ~5 plataformas. Manejable.

### A-D6. El agente NO hace push ni deploy

- **Decisión**: el agente genera los archivos y un `DEPLOY.md` con instrucciones, pero **nunca hace `git add`, `git commit`, `git push` ni `railway up`** por su cuenta. El humano despliega manualmente.
- **Por qué**: consistente con la filosofía de gates humanos del framework. Mantiene el control de qué se publica al cliente en manos del humano.
- **Excepción explícita**: si el humano le pide *"haz push"* en una sesión, el agente puede hacerlo en esa invocación específica.
- **Consecuencia aceptada**: un paso manual extra por iteración. Es barato y mantiene la disciplina.

### A-D7. Banner permanente "MOCKUP NO FUNCIONAL"

- **Decisión**: todo prototipo incluye un banner fijo, visible en todas las pantallas, con texto similar a *"MOCKUP NO FUNCIONAL — solo para validación de requisitos. Ningún botón guarda datos reales."*. Datos en pantalla son obviamente falsos (Lorem, "Cliente Demo", etc.).
- **Por qué**: evita el síndrome "esto ya está casi listo" del cliente. Salvaguarda barata contra que el prototipo se vuelva spec de facto.
- **Consecuencia aceptada**: estética degradada por el banner. Cliente serio entiende; ese es el punto.

### A-D8. Cambios cosméticos vs cambios estructurales

- **Decisión**: el prototipador puede iterar libremente sobre cambios cosméticos. Si detecta que el feedback del cliente implica un **cambio estructural** (nueva entidad, nuevo actor, nuevo flujo completo, requisito faltante), se detiene y devuelve al `analista-entrevistas`. Ver A7.
- **Por qué**: si el prototipo intenta "absorber" requisitos nuevos sin actualizar `requirements.md`, rompe la trazabilidad EARS — corazón del framework.
- **Consecuencia aceptada**: latencia mayor en algunos casos (volver al analista antes de continuar el loop). Es el precio de no contaminar la fuente de verdad.

### A-D9. `validation-log` lo llena el dev, no el cliente

- **Decisión**: el archivo `validation-log-vN.md` lo escribe el dev del framework con transcripción/notas de las observaciones del cliente. No se asume que el cliente edite Markdown ni que tenga acceso a GitHub.
- **Por qué**: el 90% de los clientes no usan git. Pretender lo contrario es planificar para falla.
- **Consecuencia aceptada**: paso manual de transcripción por iteración. Aceptable.

### A-D10. Loop iterativo con commit por iteración

- **Decisión**: cada iteración del prototipo es un commit separado (`prototype v1`, `v2`, `v3`) con su propio `validation-log-v1.md`, `v2.md`, etc.
- **Por qué**: historial real de qué cambió y por qué entre iteraciones. Útil cuando el cliente dice "pero esto antes estaba así".
- **Consecuencia aceptada**: más commits en el repo. Trivial.

### A-D11. Sin branding → placeholders genéricos

- **Decisión**: si en la iteración 1 no hay branding/logos disponibles, el agente genera con placeholders genéricos (colores neutros, tipografía system, logo `[LOGO]` en cuadro gris). Lo anota en `validation-log-v1.md`.
- **Por qué**: bloquearse en la iteración 1 esperando assets visuales es contraproducente. La iteración 1 es de estructura y flujo, no de pulido visual.
- **Consecuencia aceptada**: primera versión visualmente cruda. El loop se encarga.

### A-D12. Terminología: "mockup interactivo" / "maqueta clickable"

- **Decisión**: el agente y todos los artefactos usan los términos **mockup interactivo** o **maqueta clickable**. NUNCA "prototipo funcional".
- **Por qué**: precisión técnica. Un prototipo funcional implica backend real y lógica funcional, que no es lo que producimos. Mockup interactivo = visual de alta fidelidad con clicks que cambian pantallas pero sin lógica de negocio real.
- **Consecuencia aceptada**: hay que educar a clientes que esperan "prototipo" en el sentido genérico. El banner lo deja claro.

### A-D13. El prototipo NO decide el stack final

- **Decisión**: el HTML+Tailwind del prototipo es throwaway. `design.md` decide el stack real (React, Vue, Svelte, HTMX, Astro, etc.) sin estar atado al lenguaje del prototipo.
- **Por qué**: la decisión de stack vive en `design.md` con sus ADRs. Pre-comprometerla en el prototipo viola la disciplina del framework.
- **Consecuencia aceptada**: posible fricción social si el cliente ve el HTML y asume "esto será React". El agente debe ser explícito en el `DEPLOY.md` y en la presentación: "el visual final puede diferir; lo que se valida es el flujo, no el código".

---

## A4. Estructura del artefacto `docs/prototype/`

```
docs/prototype/
├── index.html                    # mockup principal, banner permanente
├── pantallas/                    # otras pantallas si el flujo lo requiere
│   ├── login.html
│   ├── dashboard.html
│   └── ...
├── assets/                       # imágenes, logos (placeholders si no hay branding)
│   └── ...
├── context/                      # INPUT: brief de branding, notas del cliente
│   ├── branding.md               # colores, tipografía, tono (puede estar vacío)
│   ├── logos/                    # archivos de marca si existen
│   └── referencias/              # screenshots inspiracionales si existen
├── server.js                     # express + basic auth (default: Railway)
├── package.json                  # "start": "node server.js"
├── validation-log-v1.md          # observaciones del cliente sobre v1
├── validation-log-v2.md          # observaciones sobre v2 (si existe)
├── ...
└── DEPLOY.md                     # instrucciones de despliegue (default Railway + alternativas)
```

**Reglas**:

- `context/` es **input**: lo llena el dev antes de invocar al agente con material que tenga.
- `validation-log-vN.md` es **input al agente para la iteración N+1**: lo llena el dev tras mostrar la versión N al cliente.
- Todo lo demás es **output** del agente.

---

## A5. Política de despliegue

### Default: Railway

**Setup (una sola vez, en dashboard de Railway)**:

1. Crear proyecto, conectar repo de GitHub
2. Root directory: `docs/prototype/`
3. Variables de entorno: `AUTH_USER`, `AUTH_PASS`
4. Rama a vigilar (default: la rama activa del proyecto)

**Redeploy (cada iteración)**:

1. `git add docs/prototype/`
2. `git commit -m "prototype vN"`
3. `git push`
4. Railway detecta y redespliega automáticamente

### Alternativas soportadas (el agente las documenta en `DEPLOY.md`)

| Plataforma | Auth privado | Setup | Notas |
|---|---|---|---|
| **Railway** (default) | Basic auth via `server.js` | Dashboard one-time | Recomendado para sensible |
| **Netlify** | Drag & drop o git connect | Cuenta gratis | Basic auth solo en plan pago |
| **Vercel** | Git connect | Cuenta gratis | Password protection en Pro |
| **Cloudflare Pages** | Cloudflare Access | Dashboard | Free tier generoso |
| **GitHub Pages** | Público por defecto | Settings → Pages | NO para info sensible |
| **Manual** | Lo que el dev decida | — | Agente entrega solo los archivos |

### Cómo se decide la plataforma

- Si existe `CONSTITUTION.md` con `prototype_deploy: <plataforma>` → se usa esa.
- Si no, el agente pregunta una vez en la iteración 1. La elección se anota en `DEPLOY.md` para futuras iteraciones.

---

## A6. Loop iterativo con el cliente

### Flujo de una iteración

1. **Iteración N**: el agente genera/actualiza `docs/prototype/` (incluyendo HTML, assets, `DEPLOY.md`).
2. El humano despliega manualmente (`git push` o `railway up` según plataforma).
3. El humano muestra al cliente la URL desplegada.
4. El cliente da feedback (verbal, Slack, Loom, lo que sea).
5. El humano transcribe feedback en `docs/prototype/validation-log-v{N}.md`.
6. El humano invoca al agente: *"itera al prototipo con base en validation-log-v{N}.md"*.
7. El agente clasifica el feedback (cosmético vs estructural — ver A7) y genera iteración N+1.

### Cuándo cerrar el loop

El loop se cierra cuando el cliente aprueba explícitamente. El humano marca la aprobación así:

- Commit final con tag tipo `prototype-approved-v{N}`
- Última línea en el `validation-log-v{N}.md`: `Status: APROBADO por cliente el YYYY-MM-DD`

Sin esa señal explícita, `disenador-arquitecto` no debe arrancar.

### Sanity check informal

Si en la iteración **3 o 4** el cliente sigue pidiendo cambios estructurales (no cosméticos), eso es señal de que `requirements.md` estaba incompleto o mal levantado. El agente debe sugerir explícitamente al humano: *"Iteración N detectó M cambios estructurales acumulados. Recomendación: volver al analista-entrevistas antes de continuar el loop."*

No es una regla dura — es un alerta que el humano evalúa.

---

## A7. Válvula de retorno al analista

Cuando el feedback del cliente revela algo que **no es un cambio de UI sino un requisito faltante**, el flujo se detiene y vuelve al analista.

### Señales de "esto es estructural, no cosmético"

- Cliente menciona una **entidad nueva** ("ah, y necesito que cada cliente tenga proyectos asociados") — entidad no estaba en `requirements.md`.
- Cliente menciona un **actor nuevo** ("y debería poder loguearse el supervisor también") — actor no estaba contemplado.
- Cliente menciona un **flujo completo nuevo** ("y antes de calcular debe pasar por aprobación de jefe") — flujo no estaba.
- Cliente menciona una **integración con sistema externo** ("y esto debe mandar correos automáticamente"/"...sincronizar con CRM").
- Cliente menciona un **requisito no funcional duro nuevo** ("y debe funcionar offline").

### Qué hace el agente en estos casos

1. Se detiene. NO intenta resolverlo en HTML.
2. Reporta al humano: *"Detecté un cambio estructural en el feedback: [descripción]. Esto no se resuelve en el prototipo, requiere actualizar `requirements.md`. Recomiendo invocar `analista-entrevistas` para añadir el Requirement correspondiente antes de continuar la iteración."*
3. Espera instrucción explícita del humano: (a) volver al analista, o (b) ignorar ese feedback en esta iteración y continuar con el resto.

### Qué hace el `analista-entrevistas` cuando recibe la válvula

El analista debe contemplar este caso de uso secundario: recibir feedback estructural desde el prototipador y actualizar `requirements.md` añadiendo el Requirement nuevo (con su User Story y EARS). Ver actualización en `.claude/agents/analista-entrevistas.md`.

Después de actualizar `requirements.md`, el humano vuelve a invocar al prototipador para la siguiente iteración con el contexto enriquecido.

---

## A8. Anti-patrones

### Del agente

- ❌ Generar código de producción "ya que estamos" (componentes React reales, hooks, estado complejo).
- ❌ Hacer push o deploy sin instrucción explícita.
- ❌ Omitir el banner "MOCKUP NO FUNCIONAL".
- ❌ Inventar datos que parezcan reales (nombres de clientes reales, números coherentes que confundan).
- ❌ Intentar resolver un cambio estructural en HTML en lugar de devolver al analista.
- ❌ Decidir el stack del proyecto en el prototipo (pre-comprometer React/Vue/etc.).
- ❌ Bloquearse en iteración 1 esperando branding.

### Del humano usando el framework

- ❌ Saltarse el gate de aprobación del cliente y arrancar `disenador-arquitecto` con prototipo "casi aprobado".
- ❌ Editar el HTML a mano entre iteraciones (el HTML debe regenerarse desde el agente, no mantenerse a mano).
- ❌ Usar el prototipo como spec en lugar de actualizar `requirements.md` cuando hay cambios reales.
- ❌ Desplegar a GitHub Pages prototipos con info sensible del cliente.
- ❌ Iterar más de 4-5 veces sin replantearse si el problema está en `requirements.md`.

### Del cliente (mitigaciones)

El cliente puede caer en patrones que el agente y el banner mitigan, pero el humano debe estar atento:

- Cliente trata el prototipo como "el sistema casi listo" → el banner lo desinfla, recordar verbalmente que es validación.
- Cliente quiere especificar todo vía screenshots del HTML en lugar de pedir cambios a `requirements.md` → el dev traduce screenshots a cambios formales antes de iterar.

---

## A9. Cierre (Prototipo)

Esta fase es una herramienta poderosa para validación temprana, pero solo funciona si se respeta su rol: **es validación visual del qué, no decisión técnica del cómo, ni reemplazo de `requirements.md` o `design.md`**. Si la fase se convierte en "diseñar la app via HTML", se rompió la disciplina del framework.

La frase que el dev debe poder decirle al cliente cuando vea el prototipo:

> *"Esto que ves es para que valides el flujo y el contenido. El sistema final va a verse parecido pero no idéntico, y va a tener funcionalidad real detrás. Si algo te hace ruido aquí, dímelo ahora — es 100 veces más barato cambiarlo ahora que después."*

---

# Parte B: Caso de uso Mantenimiento

> Decisiones congeladas del caso de uso de mantenimiento de stark (agregar features a sistemas en producción sin romper lo que ya funciona). Fuente de verdad sobre el **porqué** de los agentes `analista-feature-mantenimiento`, `disenador-delta-mantenimiento`, `descompositor-riesgo-mantenimiento` y sus skills correspondientes.

## B1. Propósito

`analista-entrevistas` y `arqueologo-codigo` cubren proyectos donde se **construye o se reconstruye** un sistema. stark asumía entrar al inicio del ciclo de vida.

Pero la realidad de la mayoría de los proyectos en producción es **mantenimiento**: agregar features a un sistema que ya funciona, sin romperlo. Eso es un escenario distinto:

- La arquitectura está dada — no se diseña, se respeta.
- El stack está dado — no se elige, se hereda.
- Hay reglas de negocio implementadas que no pueden romperse — son **invariantes**, no requisitos a redocumentar.
- El cambio es **un delta**, no un sistema completo — los artefactos deben acotarse a eso.

Este caso de uso introduce **tres agentes nuevos + tres skills nuevos** que viven dentro del mismo stark pero operan bajo reglas adaptadas. El resultado: un feature agregado con la misma disciplina formal que stark aplica a greenfield, pero **sin sobrediseñar** y **sin tocar lo que ya funciona**.

**Lo que el caso de uso NO es:**

- No es una alternativa a `arqueologo-codigo` para reescritura — sigue habiendo reingeniería (brownfield-rewrite) cuando el plan es rehacer el sistema.
- No es un atajo "metan el feature como puedan" — mantiene rigor de specs, EARS y gates humanos.
- No es excusa para ignorar el sistema existente — exige documentarlo antes (skills `onboarding` y `reglas-negocio`).

**Lo que el caso de uso SÍ es:**

- Disciplina stark acotada al delta del feature.
- Documentación explícita de la **superficie de contacto** con el código existente.
- Documentación explícita de las **invariantes preservadas** del sistema.
- Tasks ordenadas por riesgo de regresión, con blindaje (tests de regresión) ANTES de tocar código.
- Gate final de no-regresión obligatorio antes de cerrar.

---

## B2. Posición en el ecosistema de pipelines de stark

stark tiene **tres pipelines paralelos**, todos viven en el mismo template y comparten skills agnósticas (formato EARS) pero tienen agentes y artefactos propios:

```
                              ┌─────────────────┐
                              │      stark      │
                              │  (un solo repo) │
                              └────────┬────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
    ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
    │  NUEVO           │     │ REINGENIERÍA     │     │  MANTENIMIENTO   │
    │  (greenfield)    │     │ (brownfield-     │     │                  │
    │                  │     │  rewrite)        │     │                  │
    │ analista-        │     │ arqueologo-      │     │ analista-feature │
    │ entrevistas      │     │ codigo           │     │ -mantenimiento   │
    │       ↓          │     │       ↓          │     │       ↓          │
    │ requirements.md  │     │ requirements.md  │     │ requirements.md  │
    │ (sistema nuevo)  │     │ (sistema reescr) │     │ (delta feature)  │
    │       ↓          │     │       ↓          │     │       ↓          │
    │ (prototipo       │     │ (prototipo       │     │ (prototipo       │
    │  opcional)       │     │  opcional)       │     │  opcional —      │
    │       ↓          │     │       ↓          │     │  ver B4.D6)      │
    │ disenador-       │     │ disenador-       │     │       ↓          │
    │ arquitecto       │     │ arquitecto       │     │ disenador-delta- │
    │       ↓          │     │       ↓          │     │ mantenimiento    │
    │ design.md        │     │ design.md        │     │       ↓          │
    │ (full)           │     │ (full)           │     │ design.md (delta)│
    │       ↓          │     │       ↓          │     │       ↓          │
    │ descompositor-   │     │ descompositor-   │     │ descompositor-   │
    │ tareas           │     │ tareas           │     │ riesgo-          │
    │       ↓          │     │       ↓          │     │ mantenimiento    │
    │ tasks.md         │     │ tasks.md         │     │       ↓          │
    │ (capas)          │     │ (capas)          │     │ tasks.md (riesgo)│
    └──────────────────┘     └──────────────────┘     └──────────────────┘
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       ▼
                         [tarea por sesión + código]
```

**El template es el mismo.** Cuando clonas stark, traes los **8 agentes y 7 skills**. El pipeline correcto se identifica por:

1. Convención de carpetas distintas: `docs/inputs/` (nuevo), `docs/analysis/` (reingeniería), `docs/features/<X>/` (mantenimiento).
2. Naming convention: agentes de mantenimiento llevan sufijo `-mantenimiento`.
3. Árbol de decisión en `REFERENCIA.md` § Fase 0.

**Los porteros estrictos en cada agente** son lo que evita confusión cruzada: si invocas el agente equivocado en el repo equivocado, no encuentra sus pre-condiciones y se detiene avisando.

---

## B3. Cuándo aplicar este caso de uso (árbol de decisión)

```
                    ¿Tienes un sistema en
                       producción HOY?
                              │
                ┌─────────────┴─────────────┐
                │                           │
              NO ── tienes solo idea       SÍ
                    o legacy roto           │
                    sin querer mantener     │
                            ↓               │
                  NUEVO                     │
                  (analista-entrevistas)    │
                            ┐               │
                                            │
                              ¿Lo vas a reescribir
                              completo / modernizar
                                arquitectura?
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                            SÍ                          NO
                              │                           │
                              ↓                           ↓
                  REINGENIERÍA                     MANTENIMIENTO
                  (arqueologo-codigo)              (este caso de uso)
                                                    │
                                                    ↓
                                            ¿Cuántos features
                                              vas a agregar?
                                                    │
                                            ┌───────┴───────┐
                                          UNO              VARIOS
                                            │                 │
                                            ↓                 ↓
                                    1 feature/        Una carpeta
                                    docs/features/    docs/features/
                                                      por feature
```

Reglas de oro para no equivocarse:

- **El sistema funciona en producción + agregas algo nuevo sin romper = mantenimiento.**
- **El sistema funciona pero vas a rehacer arquitectura = reingeniería (brownfield-rewrite).**
- **No hay sistema o está siendo descartado completo = nuevo (greenfield).**

Si dudas: lee `REFERENCIA.md` §1.

---

## B4. Decisiones congeladas

Cada decisión en formato breve: **Decisión · Por qué · Consecuencias negativas aceptadas**.

### B-D1. Pipeline hermano, no extensión de los existentes

- **Decisión**: el pipeline de mantenimiento vive como tercer flujo paralelo a nuevo (greenfield) y reingeniería (brownfield-rewrite), con agentes y skills propios.
- **Por qué**: hacer "mode-aware" los agentes existentes (analista, arqueologo, disenador, descompositor) introduce ramas condicionales que multiplican modos de falla. Los agentes lineales son más robustos.
- **Consecuencia aceptada**: duplicación controlada de algunos conceptos (ej. tabla de Traceability aparece en sdd-design y en sdd-design-delta con reglas distintas). La duplicación entre dos cosas estables es más barata que el acoplamiento entre dos cosas que cambian.

### B-D2. Tres agentes nuevos, no uno solo

- **Decisión**: el pipeline de mantenimiento usa tres agentes (`analista-feature-mantenimiento`, `disenador-delta-mantenimiento`, `descompositor-riesgo-mantenimiento`), uno por artefacto.
- **Por qué**: el patrón "un agente = un artefacto" es lo que da robustez al framework. Cada agente es portero estricto de un solo output.
- **Consecuencia aceptada**: el humano invoca tres veces en lugar de una. Vale la pena por los gates intermedios.

### B-D3. Artefactos en `docs/features/<feature>/`, no en `docs/` raíz

- **Decisión**: los artefactos del feature viven en `docs/features/<slug-del-feature>/{intent,requirements,design,tasks}.md`.
- **Por qué**: un sistema en producción tendrá múltiples features a lo largo del tiempo. Aplastar todo en `docs/requirements.md` raíz pierde historial; una carpeta por feature lo preserva.
- **Consecuencia aceptada**: los paths son más largos. La estructura del repo crece. Trade-off aceptable.

### B-D4. Surface of Contact + Invariantes Preservadas son obligatorias

- **Decisión**: el `requirements.md` de mantenimiento debe tener ambas secciones, no son opcionales.
- **Por qué**: omitirlas elimina la base para no-regresión. La probabilidad de romper algo en producción sin documentar contactos e invariantes es ~100%.
- **Consecuencia aceptada**: el requirements.md de mantenimiento es más largo que uno de proyecto nuevo del mismo tamaño de feature.

### B-D5. Tasks ordenadas por riesgo, no por capa

- **Decisión**: la estructura del `tasks.md` de mantenimiento empieza con `## Regression Shield` y termina con `## No-Regression Validation`, no con `## Setup` ni `## Documentation`.
- **Por qué**: en mantenimiento no hay Setup (el sistema ya está montado). Y la garantía de no romper viene de tests de regresión PRIMERO, no de validación al final.
- **Consecuencia aceptada**: el humano aprende dos estructuras de tasks.md distintas (sdd-tasks vs sdd-tasks-risk). El sufijo en los nombres y la documentación lo hacen explícito.

### B-D6. Fase de prototipo es opcional pero compatible con mantenimiento

- **Decisión**: `prototipador-visual` PUEDE usarse en el pipeline de mantenimiento si el feature introduce UI nueva que el cliente quiere validar antes.
- **Por qué**: la fase opcional de prototipo es transversal al framework — su input es un `requirements.md` aprobado, sea del pipeline que sea.
- **Consecuencia aceptada**: para features de mantenimiento sin UI o triviales, conviene saltarla. El humano decide. El skill `sdd-prototype` no requiere cambios.
- **Path**: si se usa, el prototipo vive en `docs/features/<feature>/prototype/`, no en `docs/prototype/` raíz (lo mantiene scoped al feature).

### B-D7. Sustrato recomendado pero no obligatorio

- **Decisión**: los agentes leen `docs/CLAUDE.md`, `docs/BIG_PICTURE.md`, `docs/REGLAS_DE_NEGOCIO.md` si existen, pero pueden continuar sin ellos.
- **Por qué**: forzar el sustrato bloquearía a equipos que descubren stark a mitad de un proyecto en producción.
- **Consecuencia aceptada**: sin sustrato, la calidad del análisis depende más de cuánto código el agente lee directamente. Se documenta el riesgo en Open Questions.

### B-D8. Trazabilidad doble en tasks: EARS + Invariantes

- **Decisión**: cada tarea del `tasks.md` de mantenimiento lleva footer `_Requirements: X.Y_ | _Invariants: I.A_`.
- **Por qué**: las invariantes son tan importantes como los EARS — necesitan trazabilidad propia para que el humano pueda auditar el blindaje y la no-regresión.
- **Consecuencia aceptada**: el footer es más largo. Compensa con auditabilidad.

### B-D9. Verbo `Blindar` y verbo `Verificar regresión` exclusivos de mantenimiento

- **Decisión**: el skill `sdd-tasks-risk` introduce dos verbos nuevos: `Blindar` (escribir test de regresión sobre código existente) y `Verificar regresión` (correr suite completa + verificar invariantes).
- **Por qué**: estos verbos no aparecen en construcción (donde no hay invariantes preexistentes). Tenerlos explícitos refuerza la disciplina del pipeline.
- **Consecuencia aceptada**: el listado de verbos permitidos es más largo en mantenimiento. Documentado en el skill.

### B-D10. Tasks de integración son aisladas, una por punto de coexistencia

- **Decisión**: cada fila de Surface of Contact con riesgo medio/alto genera **una tarea aislada** en la sección `## Integration` del tasks.md.
- **Por qué**: cuando integras un feature con un flujo existente, el riesgo es local. Agrupar varios puntos en una tarea grande mezcla riesgos y vuelve la revisión más difícil.
- **Consecuencia aceptada**: el tasks.md tiene más tareas. Cada una es chica y revisable.

---

## B5. Estructura del artefacto `docs/features/<feature>/`

```
docs/features/<slug-del-feature>/
├── intent.md                 ← INPUT humano (descripción del feature)
├── requirements.md           ← OUTPUT analista-feature-mantenimiento
├── design.md                 ← OUTPUT disenador-delta-mantenimiento
├── tasks.md                  ← OUTPUT descompositor-riesgo-mantenimiento
└── (prototype/)              ← OUTPUT opcional prototipador-visual si UI relevante
```

**Slug**: kebab-case, descriptivo, sin caracteres especiales. Ej: `exportar-reportes-pdf`, `notificaciones-push`, `auth-mfa`.

**Un feature = una carpeta = un ciclo stark acotado.** Si el feature es demasiado grande (más de ~25-30 tareas), se parte en sub-features cada uno con su carpeta.

---

## B6. El sustrato: CLAUDE.md, BIG_PICTURE.md, REGLAS_DE_NEGOCIO.md

Estos tres archivos viven en `docs/` raíz (no dentro de `features/`) porque aplican al sistema completo:

- **`docs/CLAUDE.md`** — guía del repo. Generada por la skill `onboarding` (incluida en `.claude/skills/onboarding/`). Contiene: cómo se levanta el ambiente, comandos de build/test, convenciones de naming, estructura de carpetas, dependencias clave. El agente de mantenimiento la usa para saber cómo correr los tests existentes.
- **`docs/BIG_PICTURE.md`** — radiografía arquitectónica. Generada también por `onboarding`. Contiene: capas, módulos, flujo de datos, integraciones externas, patrones usados. El agente de mantenimiento la usa para saber qué arquitectura es "lo heredado e inmutable".
- **`docs/REGLAS_DE_NEGOCIO.md`** — reglas de negocio explícitas. Generada por la skill `reglas-negocio` (incluida en `.claude/skills/reglas-negocio/`). Contiene: roles, permisos, flujos de estados, validaciones, mapa funcional. El agente de mantenimiento la usa para identificar invariantes con seguridad.

Si no existen, el agente puede continuar pero recomienda al humano correrlas primero. La calidad del análisis mejora ~10x con el sustrato.

**Estas dos skills SÍ son de stark** (`.claude/skills/onboarding/` y `.claude/skills/reglas-negocio/`), no son externas. Son skills auxiliares del pipeline de mantenimiento: agnósticas al pipeline stark per se (sirven para analizar cualquier repo), pero el pipeline de mantenimiento las usa como sustrato. Por eso van empaquetadas con el framework — para que cualquiera que clone el template las tenga listas sin instalación extra.

---

## B7. Las tres garantías de no-regresión

El pipeline está construido sobre tres garantías que se refuerzan mutuamente:

### Garantía 1: Fases 1-3 son read-only sobre el código de producción

`analista-feature-mantenimiento` y `disenador-delta-mantenimiento` solo leen código. Sus outputs son `.md`. Es **matemáticamente imposible romper producción durante análisis y diseño**.

### Garantía 2: Tests de blindaje ANTES de modificar código

La sección `## Regression Shield` del tasks.md ejecuta primero. Si una invariante no tiene test, se crea **antes** de tocar el módulo. La modificación posterior se valida contra ese blindaje.

### Garantía 3: Gate final de No-Regression Validation

La última tarea del tasks.md es obligatoria: correr toda la suite + verificar cada invariante manualmente. Si una invariante se rompió, el feature **no se cierra** hasta que se resuelva.

**Estas tres garantías combinadas hacen que el pipeline de mantenimiento sea genuinamente más seguro que codear el feature a mano**, no menos.

---

## B8. Comparación con los otros pipelines

| Aspecto | Nuevo (Greenfield) | Reingeniería (Brownfield-Rewrite) | Mantenimiento |
|---|---|---|---|
| Premisa | Construir desde cero | Reescribir legacy | Agregar feature sin romper |
| Input | Entrevistas, transcripciones | Análisis arqueológico + código legacy | Intent del feature + código en prod |
| Stack | Se decide en design | Se decide en design | **Heredado** del sistema existente |
| Arquitectura | Se diseña | Se diseña | **Heredada** — solo se diseña el delta |
| Scope del `requirements.md` | Sistema completo | Sistema completo (reescrito) | **Solo el delta** |
| Surface of Contact | N/A | N/A | **Obligatoria** |
| Invariantes Preservadas | N/A | N/A (sí "Anomalies") | **Obligatorias** |
| Orden de tasks | Por capa arquitectónica | Por capa arquitectónica | **Por riesgo de regresión** |
| Tests de regresión | N/A | N/A | **Tareas de blindaje obligatorias** |
| Validación final | Tests del feature | Tests del sistema reescrito | **Tests del feature + verificación de invariantes** |
| Tamaño típico del design.md | 300-800 líneas | 300-800 líneas | **200-600 líneas** (es solo delta) |
| Agentes | analista-entrevistas → disenador-arquitecto → descompositor-tareas | arqueologo-codigo → disenador-arquitecto → descompositor-tareas | **analista-feature-mantenimiento → disenador-delta-mantenimiento → descompositor-riesgo-mantenimiento** |
| Skills | sdd-requirements, sdd-design, sdd-tasks (+ sdd-prototype opcional) | mismas | **sdd-requirements-mantenimiento, sdd-design-delta, sdd-tasks-risk** (+ sdd-prototype opcional) |

---

## B9. Anti-patrones

### Conceptuales

- ❌ Usar este pipeline para reescribir partes del sistema "porque ya estamos aquí". Si el plan es reescritura, usar `arqueologo-codigo`. Mezclar pipelines rompe la disciplina del framework.
- ❌ Saltarse el sustrato (`onboarding` / `reglas-negocio`) porque "yo conozco el sistema". El conocimiento humano no se versiona; los archivos sí. Sin sustrato, futuros features pierden contexto.
- ❌ Tratar las invariantes como "deseo": "el sistema no se rompe". Una invariante es testeable, sin excepción.
- ❌ Permitir que el design.md proponga cambios fuera de Surface of Contact. Si lo hace, el alcance se rompió silenciosamente.
- ❌ Saltarse Regression Shield "porque tenemos prisa". Garantiza descubrir regresiones en producción.
- ❌ Saltarse No-Regression Validation "porque se ve bien". El gate final es no negociable.

### Operativos

- ❌ Modificar código existente sin escribir antes el test de blindaje.
- ❌ Marcar tarea de modificación como `[x]` sin haber corrido los tests del módulo modificado.
- ❌ Tareas de integración agrupadas (varias coexistencias en una tarea).
- ❌ Trazabilidad doble con ambos `-` en el footer (`_Requirements: -_ | _Invariants: -_`) — al menos uno debe tener referencia.
- ❌ Verbos vagos en tasks ("Trabajar en X", "Hacer Y"). Sigue siendo prohibido como en sdd-tasks.

### De gobernanza

- ❌ "Ejecuta todo `tasks.md`". Rompe garantizado, igual que en proyecto nuevo. Una tarea = una sesión = una revisión.
- ❌ Aprobar requirements sin haber leído Surface of Contact e Invariantes Preservadas. Esas dos secciones son **el contrato** del feature.
- ❌ Aprobar design sin verificar que no rediseña arquitectura. La auto-validación del agente puede equivocarse — la revisión humana es la última línea.

---

## B10. Cierre (Mantenimiento)

Este caso de uso cierra el hueco más grande que tenía stark: aplicar la disciplina de specs-primero a **mantenimiento de sistemas en producción**, no solo a construcción.

La filosofía: **lo que no se documenta como invariante, no se garantiza**. Si quieres no romper algo, anótalo, refencia el código, blíndalo con test. Lo demás es esperanza.

Para uso operativo paso a paso, ver [`REFERENCIA.md`](REFERENCIA.md) (Fase 2, variante mantenimiento).
Para fundamentos generales del framework, ver el [README](../../README.md).
