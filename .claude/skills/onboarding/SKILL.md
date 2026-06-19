---
description: "Protocolo de reconocimiento para proyectos heredados o de mantenimiento. Genera CLAUDE.md y BIG_PICTURE.md con análisis completo del estado actual del proyecto."
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(ls:*)
---

# Reconocimiento de Proyecto — Protocolo de Onboarding

## Contexto

Este es un proyecto existente que voy a mantener. **No lo construí yo.** Necesito entender el estado actual antes de hacer cambios. Analiza el proyecto completo como si fueras un ingeniero senior que acaba de heredar este código.

## Instrucciones

### Fase 1: Exploración

1. Recorre **toda** la estructura de carpetas del proyecto
2. Identifica el stack tecnológico (lenguajes, frameworks, bases de datos, herramientas de build)
3. Lee los archivos de configuración clave: `package.json`, `pom.xml`, `build.gradle`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `.env.example`, CI/CD configs, etc.
4. Identifica puntos de entrada principales (main, index, app, bootstrap)
5. Revisa si existen tests y qué tipo (unitarios, integración, E2E)
6. Busca documentación existente (README, docs/, wiki, comentarios relevantes)

### Fase 2: Genera `CLAUDE.md`

Crea el archivo `CLAUDE.md` en la raíz del proyecto con las siguientes secciones:

```markdown
# CLAUDE.md — [Nombre del Proyecto]

## Stack Tecnológico
<!-- Lenguajes, frameworks, librerías principales, versiones detectadas -->

## Estructura del Proyecto
<!-- Árbol de carpetas explicado. No solo listar: explicar qué hace cada carpeta principal -->

## Comandos Esenciales
<!-- Cómo instalar dependencias, compilar, correr, testear, lint, build para producción -->

## Dependencias Principales
<!-- Las dependencias más importantes y para qué se usan. No listar todas, solo las que importan -->

## Convenciones de Código
<!-- Patrones detectados: naming, estructura de archivos, manejo de errores, estilo de imports, arquitectura -->

## Configuración del Entorno
<!-- Variables de entorno necesarias, archivos de config, requisitos del sistema -->
```

### Fase 3: Genera `BIG_PICTURE.md`

Crea el archivo `BIG_PICTURE.md` en la raíz del proyecto con las siguientes secciones:

```markdown
# BIG_PICTURE.md — [Nombre del Proyecto]

## Diagrama de Arquitectura
<!-- Diagrama en texto (ASCII o Mermaid) mostrando componentes principales y cómo se conectan -->

## Flujo de Datos
<!-- Cómo fluye la información: desde la entrada del usuario hasta la base de datos y de vuelta -->

## Puntos de Entrada
<!-- Archivos y funciones donde arranca la ejecución. Rutas principales si es web. -->

## Módulos y Responsabilidades
<!-- Cada módulo/paquete principal: qué hace, de qué depende, quién lo consume -->

## Estado de Tests
<!-- Cobertura actual, tipos de test encontrados, qué está testeado y qué no -->

## Deuda Técnica y Riesgos
<!-- Dependencias desactualizadas, código duplicado, patrones inconsistentes, vulnerabilidades potenciales, TODOs/FIXMEs encontrados, archivos sin tests -->

## Observaciones del Ingeniero
<!-- Tu criterio profesional: qué te preocupa, qué está bien hecho, por dónde empezarías a mejorar -->
```

## Reglas

- **No asumas nada.** Lee los archivos antes de concluir.
- **Sé específico.** No digas "usa una base de datos" — di "PostgreSQL 15 vía Prisma ORM".
- **Señala riesgos reales.** Si hay dependencias con CVEs conocidos, archivos de 500+ líneas sin tests, o patrones que huelen mal, dilo directo.
- **Si algo no existe, dilo.** Si no hay tests, no hay docs, no hay CI — eso es un hallazgo, no algo que omitir.
- **Los diagramas en Mermaid son preferidos** sobre ASCII cuando sea posible.
