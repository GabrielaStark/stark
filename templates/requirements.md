<!--
TEMPLATE: requirements.md
Framework: stark (Spec-Driven Development)

Reglas absolutas:
- User Story siempre en español, formato: Como X, quiero Y, para Z
- Acceptance Criteria siempre en inglés con notación EARS estricta
- Solo SHALL (nunca should/would/may/might/could)
- Cada criterio = una sola respuesta del sistema
- Cero implementación (stack, librerías, frameworks van en design.md)

Antes de cerrar este archivo, ejecutar el checklist de auto-validación
definido en .claude/skills/sdd-requirements/SKILL.md
-->

# Requirements: [Nombre del feature o sistema]

## Introduction

<!--
Un párrafo descriptivo. Qué es el sistema/feature, qué problema resuelve,
quién lo usa. Máximo 5-7 líneas. Cero implementación, cero arquitectura.
-->

[Describir aquí el sistema o feature en términos de problema y usuarios.]

## Requirements

### Requirement 1

**User Story:** Como [rol], quiero [acción/capacidad], para [objetivo de negocio].

#### Acceptance Criteria

1. WHEN [trigger] THE SYSTEM SHALL [response]
2. IF [unwanted condition] THEN THE SYSTEM SHALL [response]
3. WHILE [state] THE SYSTEM SHALL [response]

<!--
Patrones EARS disponibles:
- Ubicua:   THE SYSTEM SHALL <response>
- Evento:   WHEN <trigger> THE SYSTEM SHALL <response>
- Estado:   WHILE <state> THE SYSTEM SHALL <response>
- Opcional: WHERE <feature is present> THE SYSTEM SHALL <response>
- Error:    IF <unwanted condition> THEN THE SYSTEM SHALL <response>
- Complejo: WHILE <state>, WHEN <trigger> THE SYSTEM SHALL <response>
-->

### Requirement 2

**User Story:** Como [rol], quiero [acción/capacidad], para [objetivo de negocio].

#### Acceptance Criteria

1. ...

<!-- Agregar tantos Requirements como capacidades coherentes tenga el sistema. -->

## Non-Functional Requirements

<!--
Solo si aplica. Performance, seguridad, accesibilidad, compatibilidad.
También en formato EARS.

Ejemplo:
- THE SYSTEM SHALL respond to user input in under 200ms for inputs up to 1MB.
- THE SYSTEM SHALL support Spanish (es-MX) as the primary UI language.
- WHERE the user disables JavaScript THE SYSTEM SHALL display a graceful
  degradation message.
-->

[Listar requerimientos no funcionales si aplican, en formato EARS.]

## Out of Scope

<!--
Lista explícita de lo que NO se va a hacer. Tan importante como lo que sí.
Evita scope creep y suposiciones del LLM downstream.

Ejemplo:
- Sincronización multi-dispositivo (planificada para v2).
- Integración con SAT en tiempo real (se usa tabla local con actualización manual).
- Soporte para inglés (UI será solo en español).
-->

- [Item fuera de alcance 1]
- [Item fuera de alcance 2]

## Glossary

<!--
Solo si el dominio tiene términos no obvios. Definiciones breves.

Ejemplo:
- **ISR**: Impuesto Sobre la Renta. Tributo federal mexicano sobre ingresos.
- **Tabla SAT**: Tabla oficial de tarifas publicada por el SAT (Servicio de
  Administración Tributaria) para cálculo de ISR.
-->

- **[Término]**: [definición]

<!--
Si este es un requirements producido por el arqueologo-codigo, agregar también:

## Detected Anomalies
[Comportamientos detectados clasificados como probables bugs.]

## Open Questions
[Preguntas que quedaron sin resolver.]

## Coverage Map
[Tabla módulo legacy → Requirement(s) que lo cubre.]
-->
