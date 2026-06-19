---
name: sdd-prototype
description: Use this skill whenever generating, validating, or editing the docs/prototype/ artifact for the SDD optional prototyping phase. Defines the canonical folder structure, banner rules, fake-data rules, server.js + basic auth template, DEPLOY.md format with multi-platform support (Railway default), validation-log-vN.md format, iteration policy, and the mandatory validation checklist. Trigger whenever the task involves transforming an approved requirements.md (plus optional context/branding) into a deployable interactive mockup, or when reviewing an existing docs/prototype/ for compliance.
---

# SDD Prototype — Constitución

Este skill es la fuente de verdad para producir `docs/prototype/` en cualquier proyecto que use este framework. El subagente `prototipador-visual` consulta este archivo. Cualquier prototipo producido debe cumplir TODAS las reglas de aquí.

Las decisiones de diseño detrás de estas reglas viven en `docs/documentacion/DECISIONES.md` (Parte A — Prototipo). Si una regla aquí choca con ese doc, ese doc manda y este skill se actualiza.

## 1. Propósito del docs/prototype/

Es un **mockup interactivo de alta fidelidad** desplegable en una URL real, usado para validación temprana con el cliente antes de cementar `design.md`. NO es código de producción. NO es prototipo funcional (no guarda datos, no integra backend). SÍ es un visual clickable que permite al cliente "vivir" el flujo y detectar requisitos faltantes.

Regla de oro: **si alguien podría confundirlo con el sistema final, falló como prototipo**. El banner permanente, los datos falsos obvios y el visual deliberadamente "estilizado pero no terminado" existen para esto.

## 2. Estructura obligatoria de la carpeta

```
docs/prototype/
├── index.html                    ← OUTPUT pantalla principal
├── pantallas/                    ← OUTPUT pantallas adicionales (si aplica)
│   ├── <nombre>.html
│   └── ...
├── assets/                       ← OUTPUT imágenes, iconos, logos (o placeholders)
│   └── ...
├── context/                      ← INPUT del dev (puede estar parcialmente vacío)
│   ├── branding.md               ← colores, tipografía, tono (opcional)
│   ├── logos/                    ← assets de marca (opcional)
│   └── referencias/              ← screenshots inspiracionales (opcional)
├── server.js                     ← OUTPUT (default Railway; varía por plataforma)
├── package.json                  ← OUTPUT (default Railway)
├── validation-log-v1.md          ← INPUT del dev tras mostrar v1 al cliente
├── validation-log-v2.md          ← INPUT del dev tras mostrar v2 (si existe)
├── ...
└── DEPLOY.md                     ← OUTPUT instrucciones de despliegue
```

### Reglas estructurales

- `context/` siempre existe, aunque alguna subcarpeta esté vacía. Si no existe, el agente lo crea con un `.gitkeep`.
- `index.html` es **obligatorio**. Pantallas adicionales viven en `pantallas/`.
- `server.js` + `package.json` solo aplican para despliegues que requieren servidor (Railway default, Netlify con basic auth, etc.). Para GitHub Pages / Cloudflare Pages estático, no se generan.
- `validation-log-vN.md` se versiona por iteración. NO se sobrescribe. La iteración N+1 lee `validation-log-vN.md` como input.
- `DEPLOY.md` siempre existe desde la iteración 1.

## 3. Reglas del index.html y pantallas

### 3.1 Banner permanente

Toda pantalla HTML debe incluir un banner fijo en la parte superior, no removible, con texto similar a:

```html
<div style="position:fixed;top:0;left:0;right:0;background:#fbbf24;color:#000;
            padding:8px 16px;font-family:system-ui;font-size:14px;
            font-weight:600;text-align:center;z-index:9999;
            border-bottom:2px solid #d97706;">
  MOCKUP NO FUNCIONAL — solo para validación de requisitos.
  Ningún botón guarda datos reales.
</div>
```

Reglas del banner:

- Color de fondo amarillo/ámbar (alto contraste, imposible de ignorar).
- `position: fixed` para que esté en TODAS las pantallas.
- Padding-top correspondiente en el `<body>` para que no tape contenido.
- Texto en español, conciso, sin diplomacia.

### 3.2 Datos visibles

- Nombres: usar **claramente ficticios** ("Cliente Demo", "Juan Pérez Ejemplo", "Empresa XYZ S.A.").
- Números: usar valores obvios (`$1,234.56`, `100`, `1,000`). NO usar cifras que parezcan reales del cliente.
- Fechas: relativas y simples (`hoy`, `ayer`, `01/01/2025`).
- Emails: `usuario@ejemplo.com`, no dominios reales.
- Logos del cliente real solo si el cliente los proveyó en `context/logos/`. Si no, placeholder `[LOGO]` en cuadro gris.

### 3.3 Navegación e interactividad

- Clicks pueden cambiar de pantalla (`window.location.href = 'pantallas/X.html'`) — esto es interacción válida.
- Clicks pueden alternar visibilidad de elementos en la misma pantalla (mostrar/ocultar modales, expandir secciones).
- Clicks **NO pueden** ejecutar lógica de negocio simulada compleja. Si el cliente presiona "Calcular ISR", el resultado puede ser un valor estático o "$1,234.56", NO un cálculo real.
- Formularios pueden tener validación visual básica (campo rojo si está vacío), pero **NO envían datos a ningún backend**.
- Si una interacción requiere lógica real para validarse, eso es señal de cambio estructural: detener y consultar al humano.

### 3.4 Stack visual

- HTML5 + Tailwind CSS por CDN (NO build, NO npm install para el HTML).
- Tipografía: `system-ui` o tipografía declarada en `context/branding.md` (vía Google Fonts CDN si aplica).
- Iconos: Lucide via CDN, Heroicons inline SVG, o emojis cuando funcione.
- JS: vanilla o Alpine.js por CDN para interacciones reactivas mínimas.

Prohibido: React, Vue, Svelte, Next, cualquier framework con build. Si se cuela, viola la disciplina del framework (ver A-D3 y A-D13 en DECISIONES.md).

## 4. Reglas del server.js (despliegue default Railway)

Cuando la plataforma de despliegue es Railway (o cualquiera que sirva Node), el agente genera un `server.js` mínimo:

```js
const express = require('express');
const basicAuth = require('express-basic-auth');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(basicAuth({
  users: { [process.env.AUTH_USER || 'cliente']: process.env.AUTH_PASS || 'cambiame' },
  challenge: true,
  realm: 'Prototipo'
}));

app.use(express.static(__dirname));

app.listen(PORT, () => {
  console.log(`Prototipo sirviendo en puerto ${PORT}`);
});
```

Y `package.json`:

```json
{
  "name": "prototype",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "express-basic-auth": "^1.2.1"
  }
}
```

### Reglas del server

- Credenciales SIEMPRE por env vars (`AUTH_USER`, `AUTH_PASS`). Defaults solo para no romper en local.
- Sirve la carpeta donde reside `server.js` (es decir, `docs/prototype/`).
- Sin lógica adicional. NO endpoints, NO API, NO base de datos.
- Sin variables sensibles hardcodeadas en código. Si aparece una, FALLO.

## 5. Reglas del DEPLOY.md

`DEPLOY.md` siempre tiene esta estructura:

```markdown
# Despliegue del prototipo

> Plataforma elegida: **<nombre>** (cambiable en cualquier iteración futura).

## Setup (una sola vez)

[Pasos numerados para configurar la plataforma elegida la primera vez.]

## Redeploy (cada iteración)

[Pasos numerados para publicar una nueva versión del prototipo.]

## Cambiar de plataforma

Si quieres cambiar de plataforma, declara la nueva en `CONSTITUTION.md` con
la clave `prototype_deploy: <nombre>` o avísale al agente en la próxima invocación.

## Alternativas soportadas

| Plataforma | Auth privado | Setup | Notas |
|---|---|---|---|
| Railway (default) | Basic auth via server.js | Dashboard one-time | Recomendado para sensible |
| Netlify | Drag & drop o git connect | Cuenta gratis | Basic auth solo en plan pago |
| Vercel | Git connect | Cuenta gratis | Password protection en Pro |
| Cloudflare Pages | Cloudflare Access | Dashboard | Free tier generoso |
| GitHub Pages | Público por defecto | Settings → Pages | NO para info sensible |
| Manual | Lo que el dev decida | — | Agente entrega solo los archivos |

## Credenciales para el cliente

URL: [se llena después del primer deploy]
Usuario: [valor de AUTH_USER]
Contraseña: [valor de AUTH_PASS — NUNCA commitear en este archivo]
```

Reglas:

- **NUNCA** escribir credenciales reales en `DEPLOY.md`. Solo placeholders y referencias a env vars.
- La sección "Setup" debe estar adaptada a la plataforma elegida — no genérica.
- La sección "Redeploy" debe ser ejecutable por un humano sin investigación extra.

## 6. Reglas del validation-log-vN.md

Cada iteración del prototipo se acompaña de un archivo `validation-log-v{N}.md` con esta estructura:

```markdown
# Validation Log — Iteración v{N}

**Fecha de presentación al cliente**: YYYY-MM-DD
**URL desplegada**: <url>
**Status**: PENDIENTE | EN_REVISIÓN | APROBADO | REQUIERE_NUEVA_ITERACIÓN

## Feedback del cliente (transcrito por <nombre del dev>)

### Cambios cosméticos
- [ ] Cambiar color primario a azul corporativo (#0066CC)
- [ ] Logo va en esquina superior izquierda, no centrado
- [ ] ...

### Cambios estructurales (requieren actualizar requirements.md)
- [ ] Cliente mencionó que necesita login para supervisor (rol nuevo)
- [ ] ...

### Preguntas del cliente sin resolver
- [ ] ¿Se mostrará histórico de cálculos? (no estaba en requirements)
- [ ] ...

## Decisión

[ ] Aprobado para pasar a design.md
[ ] Iterar a v{N+1}
[ ] Volver a analista-entrevistas (cambios estructurales detectados)

## Notas adicionales

[Lo que el dev quiera dejar registrado: ambiente de la reunión,
nivel de receptividad, sugerencias del cliente que no son cambios pero
informan futuras decisiones, etc.]
```

Reglas:

- **El dev llena este archivo**, no el cliente. Transcripción honesta.
- **NUNCA** se sobrescribe entre iteraciones. La v2 lee la v1 como historia.
- **Aprobación final**: la última línea del último validation-log debe decir `Status: APROBADO` con fecha. Sin esa línea, `disenador-arquitecto` no debe arrancar.
- Cambios estructurales detectados disparan la **válvula de retorno al analista** — ver §8.

## 7. Política de iteración

### 7.1 Cada iteración es un commit separado

- Iteración 1: `git commit -m "prototype v1"`
- Iteración 2: `git commit -m "prototype v2"`
- ...
- Aprobación final: tag `prototype-approved-v{N}`

### 7.2 Cuándo iterar

El agente itera cuando recibe un `validation-log-v{N}.md` cuyo Status es `REQUIERE_NUEVA_ITERACIÓN` y los cambios son **cosméticos** (no estructurales).

### 7.3 Cuándo detenerse y devolver al humano

- Status del último log es `APROBADO` → fin del loop, listo para `disenador-arquitecto`.
- Cambios marcados como estructurales en el log → válvula de retorno (§8).
- El dev pide explícitamente detenerse para revisión humana intermedia.

### 7.4 Sanity check (informal)

Si la iteración actual es **v3 o superior** y el último log tiene **3 o más cambios estructurales acumulados** desde v1, el agente debe reportar:

> *"Iteración v{N} detectó cambios estructurales acumulados. Patrón: requirements.md posiblemente incompleto. Recomiendo pausar el loop y volver a `analista-entrevistas` para una pasada completa antes de continuar."*

No es una regla dura — es una alerta para que el humano decida.

## 8. Válvula de retorno al analista (cambios estructurales)

### 8.1 Qué cuenta como cambio estructural

Cualquiera de estas señales en el feedback del cliente:

- **Entidad nueva** no contemplada en `requirements.md` ("necesito que cada cliente tenga proyectos").
- **Actor/rol nuevo** ("debería poder loguearse el supervisor").
- **Flujo completo nuevo** ("antes de calcular debe pasar por aprobación").
- **Integración externa nueva** ("debe mandar correos automáticamente", "sincronizar con CRM").
- **Requisito no funcional duro nuevo** ("debe funcionar offline", "debe soportar 10K usuarios concurrentes").

### 8.2 Qué hace el agente

1. NO intenta resolverlo en HTML.
2. Anota el cambio en la sección "Cambios estructurales" del próximo `validation-log` (o lo confirma si el dev ya lo marcó así).
3. Reporta al humano: *"Detecté un cambio estructural: [descripción]. Esto requiere actualizar `requirements.md`. Recomiendo invocar `analista-entrevistas` antes de continuar la iteración."*
4. Espera instrucción explícita: (a) volver al analista, (b) ignorar ese feedback en esta iteración y continuar con el resto, (c) detenerse hasta nueva orden.

### 8.3 Qué hace el flujo después del retorno

1. El `analista-entrevistas` actualiza `requirements.md` añadiendo el Requirement nuevo con su User Story y EARS.
2. El humano valida el requirements actualizado (gate humano).
3. El humano vuelve a invocar al `prototipador-visual` para una nueva iteración con el contexto enriquecido.

## 9. Política de despliegue (referencia)

El agente NO ejecuta `git push` ni `railway up` por su cuenta. Genera los archivos y deja `DEPLOY.md` para que el humano despliegue manualmente.

**Excepción**: si el humano en una sesión específica dice *"haz push"* o equivalente explícito, el agente puede ejecutar `git add docs/prototype/ && git commit && git push` en esa invocación. NO asume permiso para futuras iteraciones.

Bajo ninguna circunstancia el agente:

- Modifica configuraciones de Railway/Netlify/Vercel desde CLI.
- Crea cuentas, proyectos o repositorios remotos.
- Toca ramas distintas a la activa.

## 10. Reglas de oro

### Lo que SÍ

- ✅ HTML estático + Tailwind CDN + JS vanilla/Alpine. Throwaway por diseño.
- ✅ Banner permanente "MOCKUP NO FUNCIONAL" en todas las pantallas.
- ✅ Datos visibles obviamente falsos.
- ✅ Basic auth por env vars cuando hay info sensible.
- ✅ `validation-log-vN.md` versionado por iteración, escrito por el dev.
- ✅ Commit separado por iteración, tag al aprobar.
- ✅ Devolver al analista cuando feedback es estructural.
- ✅ Placeholders genéricos si falta branding en iteración 1.

### Lo que NO

- ❌ Frameworks con build (React, Vue, Svelte, Next, etc.). Nunca.
- ❌ Backend real, base de datos real, autenticación real (más allá de basic auth del prototipo).
- ❌ Lógica de negocio simulada compleja. Cálculos = valores estáticos.
- ❌ Datos visibles que parezcan reales (nombres reales del cliente, cifras coherentes).
- ❌ Credenciales hardcoded en `server.js` o `DEPLOY.md`.
- ❌ Omitir el banner o hacerlo dismissible.
- ❌ Sobrescribir `validation-log` de iteraciones previas.
- ❌ Pre-decidir el stack del proyecto en el prototipo (HTML+Tailwind es para el prototipo, NO compromete `design.md`).
- ❌ Hacer push/deploy sin instrucción explícita del humano.
- ❌ Intentar absorber cambios estructurales en HTML en lugar de devolver al analista.
- ❌ Bloquearse en iteración 1 esperando branding completo.

## 11. Ejemplos comparados

### Banner MAL

```html
<p style="color:gray;font-size:10px;">Esto es un prototipo</p>
```

Problemas: pequeño, gris (bajo contraste), no fijo, fácil de pasar por alto. No protege contra "esto ya está listo".

### Banner BIEN

```html
<div style="position:fixed;top:0;left:0;right:0;background:#fbbf24;color:#000;
            padding:8px 16px;font-family:system-ui;font-size:14px;
            font-weight:600;text-align:center;z-index:9999;
            border-bottom:2px solid #d97706;">
  MOCKUP NO FUNCIONAL — solo para validación de requisitos.
  Ningún botón guarda datos reales.
</div>
```

### Datos MAL

```html
<td>María González Hernández</td>
<td>$487,329.45</td>
<td>maria.gonzalez@bbva.com.mx</td>
```

Problemas: nombre plausible, cifra demasiado específica, email de empresa real. Cliente puede asumir que es real.

### Datos BIEN

```html
<td>Cliente Demo 1</td>
<td>$1,234.56</td>
<td>cliente@ejemplo.com</td>
```

### Reacción a feedback estructural MAL

> Cliente dijo: *"y debería existir un rol de supervisor que apruebe los cálculos antes de mandarlos"*
>
> Agente: *crea una pantalla `pantallas/supervisor.html` con un login simulado*

Problemas: el agente está absorbiendo un Requirement nuevo (rol supervisor) sin que pase por `requirements.md`. Trazabilidad rota.

### Reacción a feedback estructural BIEN

> Agente: *"Detecté que el cliente mencionó un rol nuevo (supervisor con poder de aprobación). Esto es un cambio estructural — implica al menos un actor nuevo y posiblemente un flujo de aprobación. No lo voy a resolver en HTML. Recomendación: invocar `analista-entrevistas` para añadir el Requirement de supervisor antes de iterar el prototipo. ¿Procedo a anotar esto en validation-log-v{N}.md como cambio estructural y me detengo?"*

## 12. Checklist de auto-validación (OBLIGATORIO antes de cerrar una iteración)

Antes de declarar una iteración del prototipo lista para mostrar al cliente, ejecutar mentalmente cada uno de estos chequeos. Si CUALQUIERA falla, NO entregar — corregir y revalidar.

### Estructura de carpeta

- [ ] Existe `docs/prototype/index.html`
- [ ] Existe `docs/prototype/context/` (aunque alguna subcarpeta esté vacía)
- [ ] Existe `docs/prototype/DEPLOY.md` con plataforma declarada
- [ ] Si plataforma requiere server, existen `server.js` y `package.json`
- [ ] Existe `docs/prototype/validation-log-v{N}.md` para esta iteración (vacío excepto header)

### HTML / Visual

- [ ] Todas las pantallas (`index.html` + `pantallas/*.html`) tienen el banner permanente
- [ ] Banner usa color de alto contraste, position fixed, no dismissible
- [ ] Todos los nombres visibles son obviamente ficticios
- [ ] Todos los números visibles son valores planos (1,234.56 / 100 / 1,000)
- [ ] Todos los emails usan dominios de ejemplo (`@ejemplo.com`)
- [ ] NO hay frameworks con build (no `import React`, no JSX, no .vue, no .svelte)
- [ ] Solo HTML + Tailwind CDN + vanilla/Alpine JS

### Interactividad

- [ ] Clicks que cambian pantallas funcionan (navegación)
- [ ] Formularios NO envían datos a backend real
- [ ] Cálculos visibles son valores estáticos, no lógica real
- [ ] Validaciones visuales (campo vacío) están permitidas pero no procesan datos

### Server / Auth (si aplica)

- [ ] `server.js` usa env vars para credenciales, sin hardcoded
- [ ] `package.json` solo declara `express` + `express-basic-auth`
- [ ] No hay endpoints, no hay APIs, no hay BD

### DEPLOY.md

- [ ] Sección "Setup (una sola vez)" presente y adaptada a la plataforma
- [ ] Sección "Redeploy (cada iteración)" ejecutable sin investigación extra
- [ ] Tabla de alternativas presente
- [ ] NO contiene credenciales reales, solo placeholders

### validation-log

- [ ] Header con fecha, URL placeholder, Status `PENDIENTE`
- [ ] Secciones cosméticos / estructurales / preguntas presentes (vacías esperando feedback)
- [ ] Sección Decisión presente con las 3 opciones

### Branding y contexto

- [ ] Si hay assets en `context/logos/`, se usaron en el HTML
- [ ] Si NO hay assets, se usan placeholders genéricos (cuadro gris `[LOGO]`)
- [ ] Si hay `context/branding.md`, sus colores/tipografía están reflejados
- [ ] Si NO hay branding declarado, se usa paleta neutra (grises + un acento)

### Disciplina

- [ ] El agente NO ejecutó `git push` ni `railway up` sin instrucción explícita
- [ ] El agente NO absorbió cambios estructurales en HTML (los anotó en validation-log)
- [ ] El agente NO pre-decidió el stack del proyecto (HTML+Tailwind es solo del prototipo)

## 13. Cuando el output NO está listo

Si después de la auto-validación queda CUALQUIER ítem sin marcar:

1. **NO entregues** la iteración.
2. Reporta al humano qué ítems fallaron y qué información hace falta para resolverlos.
3. Itera hasta que el checklist completo esté satisfecho.

Mejor entregar una iteración incompleta con anotaciones explícitas en el validation-log que una iteración que parece lista pero tiene huecos disfrazados (banner pequeño, datos plausibles, cálculos "casi reales", credenciales hardcoded).
