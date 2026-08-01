#!/usr/bin/env python3
"""Auto-verificación de stark — el Regression Shield del propio framework.

Valida todo lo verificable por máquina en el repo:
  1. Frontmatters YAML de agentes, skills y comandos (parsean; name = archivo;
     skills declaradas existen; argument-hint es string).
  2. Fences de código balanceados en todos los .md.
  3. Links internos de markdown resuelven (archivo y ancla).
  4. Nombres de agentes/skills/comandos citados en prosa existen en disco.
  5. Los scripts Python del framework (sello.py incluido) compilan.

Uso: python3 scripts/verificar.py   →   exit 0 = verde.
"""
import ast
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Falta pyyaml: pip install pyyaml")
    sys.exit(2)

RAIZ = Path(__file__).resolve().parent.parent
ERRORES = []


def error(msg):
    ERRORES.append(msg)


def archivos_md():
    return [p for p in RAIZ.rglob("*.md") if ".git" not in p.parts]


def verifica_frontmatter():
    agentes = sorted((RAIZ / ".claude/agents").glob("*.md"))
    skills = sorted((RAIZ / ".claude/skills").glob("*/SKILL.md"))
    comandos = sorted((RAIZ / ".claude/commands").glob("*.md"))
    skills_en_disco = {p.parent.name for p in skills}

    for p in agentes + skills + comandos:
        rel = p.relative_to(RAIZ)
        texto = p.read_text(encoding="utf-8")
        if not texto.startswith("---"):
            error(f"{rel}: sin frontmatter YAML")
            continue
        try:
            fm = yaml.safe_load(texto.split("---")[1])
        except yaml.YAMLError as e:
            error(f"{rel}: YAML inválido — {str(e).splitlines()[0]}")
            continue
        if not isinstance(fm, dict) or "description" not in fm:
            error(f"{rel}: frontmatter sin description")
            continue
        hint = fm.get("argument-hint")
        if hint is not None and not isinstance(hint, str):
            error(f"{rel}: argument-hint parsea como {type(hint).__name__} — va entre comillas")
        if p in agentes:
            if fm.get("name") != p.stem:
                error(f"{rel}: name '{fm.get('name')}' no coincide con el archivo '{p.stem}'")
            for s in fm.get("skills") or []:
                if s not in skills_en_disco:
                    error(f"{rel}: skill declarada '{s}' no existe en .claude/skills/")


def verifica_fences():
    for p in archivos_md():
        n3 = n4 = 0
        for linea in p.read_text(encoding="utf-8").splitlines():
            if linea.startswith("````"):
                n4 += 1
            elif linea.startswith("```"):
                n3 += 1
        if n3 % 2 or n4 % 2:
            error(f"{p.relative_to(RAIZ)}: fences sin pareja (```={n3}, ````={n4})")


def slug(titulo):
    # Estilo GitHub: minúsculas, fuera puntuación, cada espacio → guión.
    t = re.sub(r"[^\w\s-]", "", titulo.strip().lower())
    return t.replace(" ", "-")


def anclas_de(path):
    anclas = set()
    en_fence = False
    for linea in path.read_text(encoding="utf-8").splitlines():
        if linea.startswith("```"):
            en_fence = not en_fence
            continue
        m = re.match(r"#{1,6}\s+(.*)", linea)
        if m and not en_fence:
            anclas.add(slug(m.group(1)))
    return anclas


def verifica_links():
    for p in archivos_md():
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", p.read_text(encoding="utf-8")):
            destino = m.group(1)
            if destino.startswith(("http://", "https://", "mailto:")):
                continue
            ruta, _, ancla = destino.partition("#")
            objetivo = (p.parent / ruta).resolve() if ruta else p
            if ruta and not objetivo.exists():
                error(f"{p.relative_to(RAIZ)}: link roto → {destino}")
                continue
            if ancla and objetivo.suffix == ".md" and ancla not in anclas_de(objetivo):
                error(f"{p.relative_to(RAIZ)}: ancla inexistente → {destino}")


def verifica_nombres():
    validos = (
        {p.stem for p in (RAIZ / ".claude/agents").glob("*.md")}
        | {p.parent.name for p in (RAIZ / ".claude/skills").glob("*/SKILL.md")}
        | {p.stem for p in (RAIZ / ".claude/commands").glob("*.md")}
        | {"stark-lote"}  # prefijo de los tags RDD (sello.py), no es comando
    )
    patron = re.compile(
        r"\b((?:analista|arqueologo|disenador|descompositor|prototipador|sdd|stark)-[a-z-]+)"
    )
    for p in archivos_md():
        for m in patron.finditer(p.read_text(encoding="utf-8")):
            token = m.group(1).rstrip("-")
            # Tolera nombres partidos en diagramas ASCII: solo un token que es
            # PREFIJO de un nombre válido (texto truncado por el diagrama).
            # La dirección inversa NO se tolera: 'sdd-design-typo' es error.
            if token in validos:
                continue
            if any(v.startswith(token) for v in validos):
                continue
            error(f"{p.relative_to(RAIZ)}: nombre citado inexistente → '{token}'")


def verifica_scripts():
    for p in list((RAIZ / ".claude/scripts").glob("*.py")) + list((RAIZ / "scripts").glob("*.py")):
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except SyntaxError as e:
            error(f"{p.relative_to(RAIZ)}: no compila — línea {e.lineno}: {e.msg}")


def main():
    verifica_frontmatter()
    verifica_fences()
    verifica_links()
    verifica_nombres()
    verifica_scripts()
    if ERRORES:
        print(f"❌ verificar.py: {len(ERRORES)} problema(s)")
        for e in ERRORES:
            print(f"  - {e}")
        sys.exit(1)
    print("✅ stark verificado: frontmatters, fences, links, nombres y scripts en orden.")


if __name__ == "__main__":
    main()
