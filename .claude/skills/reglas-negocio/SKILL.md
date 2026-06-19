---
description: "Extrae y documenta las reglas de negocio de un proyecto existente: roles, permisos, flujos de estados, validaciones y mapa funcional. Genera docs/REGLAS_DE_NEGOCIO.md."
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*), Bash(ls:*), Task, Write
---

# Reglas de Negocio — Protocolo de Extracción

## Contexto

Este proyecto ya tiene `CLAUDE.md` y/o `BIG_PICTURE.md` con la visión técnica. Ahora necesito entender **qué hace el sistema a nivel funcional**: quién usa qué, con qué permisos, bajo qué reglas, y con qué restricciones. Esto es para que un programador de mantenimiento pueda tocar funcionalidad sin romper lógica de negocio que no conoce.

## Prerrequisitos

- El proyecto ya fue explorado técnicamente (idealmente con `/onboarding`)
- Se conoce el stack, la estructura de carpetas y los puntos de entrada

## Instrucciones

### Fase 1: Identificar Roles y Permisos

1. Busca **enums, constantes o tablas** que definan roles de usuario (buscar: `role`, `rol`, `ROLE_`, `UserRole`, `permission`, `authority`, `grant`)
2. Busca **guards, middlewares o filtros** de autorización (buscar: `guard`, `authorize`, `PreAuthorize`, `hasRole`, `canActivate`, `middleware`)
3. Busca **menús o navegación** que se filtren por rol (buscar: `roles:`, `menu`, `sidebar`, `nav`, `isAdmin`, `isUser`)
4. Lee los archivos encontrados **completos** — no asumas por el nombre
5. Documenta por cada rol:
   - ID y nombre interno
   - Qué ve en la UI (menú, rutas accesibles)
   - Qué puede hacer (crear, editar, aprobar, eliminar)
   - Qué NO puede hacer (restricciones explícitas)
   - Dónde se implementa la restricción (archivo y mecanismo)

### Fase 2: Identificar Flujos de Estados

1. Busca **enums de estado** o tablas de estados (buscar: `status`, `estado`, `state`, `workflow`, `BORRADOR`, `DRAFT`, `PENDING`, `APPROVED`)
2. Busca **use cases, servicios o controladores** que cambien estados (buscar: `updateStatus`, `transition`, `cambiar`, `approve`, `reject`, `send`)
3. Busca **validaciones** previas a cambios de estado (buscar: `validate`, `validar`, `check`, `assert`, `throw`, excepciones de negocio)
4. Lee los archivos encontrados **completos**
5. Documenta:
   - Lista de estados posibles con IDs y nombres
   - Diagrama de transiciones (qué estado puede pasar a cuál)
   - Quién puede ejecutar cada transición (por rol)
   - Qué validaciones se aplican en cada transición
   - Si hay cambios en cascada (un cambio que propaga a entidades hijas)
   - Si hay notificaciones (email, push, etc.) asociadas a transiciones

### Fase 3: Identificar Validaciones de Negocio

1. Busca **validaciones de campos obligatorios** antes de operaciones clave (buscar: `@Valid`, `required`, `obligatorio`, `isEmpty`, `isBlank`, `throw`)
2. Busca **restricciones de dependencia** entre entidades (buscar: `debe estar`, `requiere`, `no se puede`, `antes de`, `prerequisite`)
3. Busca **control de acceso temporal** — períodos, ventanas de tiempo, expiración (buscar: `periodo`, `period`, `fecha`, `expir`, `vigente`, `activo`, `window`)
4. Documenta:
   - Campos obligatorios por operación (crear, enviar, aprobar)
   - Dependencias entre entidades (ej: "no se puede crear X si Y no está en estado Z")
   - Restricciones temporales (períodos de captura, accesos manuales)

### Fase 4: Mapear Funcionalidades a Código

Para cada funcionalidad identificada, documenta una tabla con:

| Funcionalidad | Frontend (archivo) | Backend (archivo) |
|---------------|--------------------|--------------------|
| Nombre de la funcionalidad | Componente/página/servicio | Controller → UseCase |

Esto permite que un programador de mantenimiento encuentre en menos de 30 segundos **dónde tocar** para cualquier cambio funcional.

### Fase 5: Generar `docs/REGLAS_DE_NEGOCIO.md`

Crea el archivo `docs/REGLAS_DE_NEGOCIO.md` (o la carpeta de docs que ya exista en el proyecto) con la siguiente estructura:

```markdown
# Reglas de Negocio — [Nombre del Proyecto]

> Documento de referencia para mantenimiento. Describe roles, funcionalidades,
> flujos de estados, validaciones y ubicación de cada pieza en el código.
>
> Última actualización: [fecha]

## 1. Roles del Sistema
<!-- Tabla con ID, nombre, propósito -->
<!-- Dónde se definen (frontend, backend, BD) -->

## 2. Funcionalidades por Rol
<!-- Para cada rol: qué ve, qué puede hacer, qué NO puede hacer -->
<!-- Tabla de archivos clave por funcionalidad -->

## 3. Tipos de Entidades Principales
<!-- Las entidades centrales del negocio y su jerarquía -->
<!-- Si aplica: tipos de reportes, tipos de productos, etc. -->

## 4. Estados y Transiciones
<!-- Los N estados posibles -->
<!-- Diagrama de transiciones (Mermaid preferido) -->
<!-- Reglas de transición: quién, cuándo, con qué validación -->
<!-- Cambios en cascada -->
<!-- Notificaciones asociadas -->

## 5. Validaciones de Negocio
<!-- Campos obligatorios por operación -->
<!-- Dependencias entre entidades -->
<!-- Restricciones temporales -->

## 6. Observaciones y Feedback
<!-- Si existe un mecanismo de revisión/rechazo/corrección, documentar el flujo -->

## 7. Auditoría
<!-- Si existe registro automático de acciones, documentar qué se registra y dónde -->

## 8. Autenticación y Sesión
<!-- Mecanismo (JWT, session, OAuth), duración, almacenamiento -->
<!-- Flujo resumido de login -->

## 9. Mapa de Archivos
<!-- Tabla tipo "si necesito cambiar X, toco estos archivos" -->
<!-- Agrupado por área funcional -->

## 10. Endpoints API — Referencia Rápida
<!-- Tabla con método, ruta, controller, rol requerido -->
```

**Nota:** Las secciones son una guía. Si el proyecto no tiene estados, ni roles, ni auditoría — no inventes secciones vacías. Documenta solo lo que existe. Si una sección no aplica, omítela.

## Reglas

- **Lee el código, no asumas.** Los nombres de archivo mienten a veces. Un `authGuard` podría solo verificar token sin validar rol.
- **Documenta la implementación real, no la intención.** Si el código dice que un endpoint es público aunque "debería" estar protegido, documenta lo que ES, no lo que debería ser. Marca la discrepancia como hallazgo.
- **Busca en ambas capas.** Una regla puede estar en el backend (use case), en el frontend (computed signal), o en ambos. Documenta dónde se implementa realmente.
- **Sé específico con archivos.** No digas "en el módulo de reportes" — di `reports/pages/amsyd/amsyd.ts` línea tal.
- **Prioriza lo que rompe.** Si cambias una validación de estado y no sabías que había cambio en cascada, rompiste 5 entidades. Esas dependencias ocultas son las más importantes de documentar.
- **Si algo falta, dilo.** Si no hay validación de rol en el backend, si no hay guards por rol en el frontend, si no hay tests para las transiciones de estado — eso es un hallazgo crítico.
- **Los diagramas en Mermaid son preferidos** sobre ASCII cuando sea posible.
- **Responde siempre en español.**