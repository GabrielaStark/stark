# Intent: [Nombre del feature]

> Template para el input del pipeline de mantenimiento.
> Cópiate este archivo a `docs/features/<slug-del-feature>/intent.md` y llénalo.
> El agente `analista-feature-mantenimiento` lo lee como punto de partida.

## Qué queremos

[Descripción del feature en lenguaje de negocio.
Qué capacidad se le quiere agregar al sistema. 3-8 líneas.
Evita lenguaje técnico — escribe como se lo explicarías al stakeholder.]

## Por qué

[Justificación / problema que resuelve.
¿Qué pasa hoy que motivó el pedido?
¿Qué se gana al implementarlo?]

## Quién pidió

[Nombre del stakeholder + rol.
Si es un pedido del cliente: nombre del cliente + área.
Si es deuda técnica: indicar "interno" + razón.]

## En qué área del sistema vive (intuición inicial)

[Tu mejor adivinanza sobre dónde aterriza el feature.
No tiene que ser preciso — el agente lo va a refinar al leer el código.
Ej: "Módulo de reportes", "Sección de auth", "API REST", etc.]

## Out of scope explícito

[Cosas que el stakeholder podría asumir pero NO van a estar en este feature.
Importante para alinear expectativas y evitar scope creep.

Ej:
- No incluye exportación a Excel (solo PDF)
- No incluye notificación por email
- No cambia los reportes existentes en pantalla
]

## Pistas técnicas conocidas (opcional)

[Si ya sabes que el feature va a tocar ciertos archivos o módulos, anótalos.
Si conoces alguna restricción técnica relevante, ponla aquí.
Si NO sabes nada técnico todavía, deja vacío — el agente lo descubre.

Ej:
- Probablemente toca `src/reports/`
- Existe una librería de PDFs ya integrada (`openpdf`)
- El cliente requiere fuente Arial 11pt
- Debe respetar permisos por rol existentes
]

## Stakeholder técnico

[Quién aprueba el feature por la parte técnica.
Quién puede resolver dudas sobre "¿esto es invariante o se puede cambiar?".]

## Fecha de pedido / urgencia

[Cuándo se pidió. Si hay deadline, ponerlo aquí.
No es una fecha "comprometida con el agente" — es contexto.]

---

## Notas adicionales

[Espacio libre para cualquier otro contexto que aporte:
- Conversaciones relevantes con el cliente
- Referencias a otros features parecidos en el sistema
- Trade-offs ya discutidos
- Decisiones previas que afectan este feature
]
