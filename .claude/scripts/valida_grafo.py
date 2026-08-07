#!/usr/bin/env python3
"""valida_grafo.py — valida el mapa estructural docs/.stark/grafo.json contra el disco.

El mapa lo escribe un LLM (skill onboarding, Fase 3). Este script atrapa lo
verificable por máquina SIN parsear código — por eso es agnóstico al lenguaje:

  1. El JSON carga, trae version soportada, commit y la forma esperada.
  2. Toda ruta citada existe en disco (módulos, archivos, aristas, entradas).
  3. Los rangos de líneas de las entidades caben en su archivo (las líneas
     del mapa son aproximadas: se tolera 15% de holgura, no más).
  4. Las aristas traen evidencia no vacía y confianza válida (vista|inferida).
  5. Avisos, no errores: commit del mapa ≠ HEAD actual (mapa desactualizado),
     total de líneas declarado desviado >25% del real, arista que cita un
     archivo no declarado en modulos.

El mapa orienta, no jura: este script garantiza que las rutas y rangos citados
existen, no que la semántica del mapa sea correcta — eso lo juzga el humano.

Uso: python3 .claude/scripts/valida_grafo.py [ruta-al-grafo] [--raiz DIR]
     (defaults: raíz = toplevel de git o cwd; grafo = docs/.stark/grafo.json)
Exit: 0 = válido (con o sin avisos) · 1 = errores · 2 = no se pudo cargar.
Sin dependencias de pip.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CONFIANZAS = {"vista", "inferida"}
RANGO = re.compile(r"^~?\s*(\d+)\s*(?:-\s*(\d+))?$")
HOLGURA = 1.15  # las líneas del mapa son aproximadas
DESVIO = 0.25   # aviso si el total declarado se aleja más que esto del real

ERRORES = []
AVISOS = []
_cache_lineas = {}


def error(msg):
    ERRORES.append(msg)


def aviso(msg):
    AVISOS.append(msg)


def lineas_reales(path):
    if path not in _cache_lineas:
        try:
            texto = path.read_text(encoding="utf-8", errors="replace")
            _cache_lineas[path] = len(texto.splitlines())
        except OSError:
            _cache_lineas[path] = None
    return _cache_lineas[path]


def git_head(raiz):
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=raiz,
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    except OSError:
        return None


def raiz_default():
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    except OSError:
        pass
    return Path.cwd()


def parsea_args(argv):
    ruta_grafo = raiz = None
    i = 0
    while i < len(argv):
        if argv[i] == "--raiz":
            if i + 1 >= len(argv):
                print("Falta el valor de --raiz")
                sys.exit(2)
            raiz = Path(argv[i + 1])
            i += 2
        elif argv[i].startswith("-"):
            print(f"Opción desconocida: {argv[i]} (uso: [ruta-al-grafo] [--raiz DIR])")
            sys.exit(2)
        elif ruta_grafo is None:
            ruta_grafo = Path(argv[i])
            i += 1
        else:
            print(f"Argumento de más: {argv[i]}")
            sys.exit(2)
    return ruta_grafo, raiz


def valida_version_y_commit(grafo, raiz):
    if grafo.get("version") != 1:
        error(f"version {grafo.get('version')!r} no soportada (esperaba 1)")
    commit = grafo.get("commit")
    if not isinstance(commit, str) or not commit.strip():
        error("falta commit — el mapa debe anclar a qué revisión del código corresponde")
        return
    head = git_head(raiz)
    if head and not (head.startswith(commit) or commit.startswith(head)):
        aviso(f"mapa desactualizado: commit del grafo {commit[:12]} ≠ HEAD actual "
              f"{head[:12]} — refresca con la Fase 3 de onboarding")


def valida_modulos(grafo, raiz):
    declarados = set()
    n_archivos = n_entidades = 0
    modulos = grafo.get("modulos")
    if not isinstance(modulos, list):
        error("falta la lista modulos")
        return declarados, 0, 0
    if not modulos:
        aviso("modulos está vacío — un mapa sin módulos no orienta a nadie")
    for m in modulos:
        ruta_m = m.get("ruta", "")
        if ruta_m and ruta_m != "." and not (raiz / ruta_m).exists():
            error(f"módulo '{ruta_m}' no existe en disco")
        for a in m.get("archivos", []):
            ruta_a = a.get("ruta", "")
            path_a = raiz / ruta_a
            if not ruta_a or not path_a.is_file():
                error(f"archivo '{ruta_a}' citado en módulo '{ruta_m}' no existe")
                continue
            declarados.add(ruta_a)
            n_archivos += 1
            reales = lineas_reales(path_a)
            decl = a.get("lineas")
            if reales and isinstance(decl, int) and decl > 0:
                if abs(decl - reales) / reales > DESVIO:
                    aviso(f"'{ruta_a}': lineas declaradas {decl} vs reales {reales} "
                          f"— mapa desviado, considera refrescarlo")
            for e in a.get("entidades", []):
                n_entidades += 1
                nombre = e.get("nombre")
                if not nombre:
                    error(f"'{ruta_a}': entidad sin nombre")
                    continue
                rango = e.get("lineas")
                if rango is None:
                    continue  # entidad sin líneas: permitido, el mapa orienta
                m_rango = RANGO.match(str(rango).strip())
                if not m_rango:
                    error(f"'{ruta_a}' → {nombre}: lineas '{rango}' no tiene forma '~inicio-fin'")
                    continue
                ini = int(m_rango.group(1))
                fin = int(m_rango.group(2) or ini)
                if fin < ini:
                    error(f"'{ruta_a}' → {nombre}: rango invertido ({rango})")
                elif reales and (ini > reales * HOLGURA or fin > reales * HOLGURA):
                    error(f"'{ruta_a}' → {nombre}: rango {rango} fuera del archivo "
                          f"({reales} líneas reales)")
    return declarados, n_archivos, n_entidades


def valida_aristas(grafo, raiz, declarados):
    aristas = grafo.get("aristas", [])
    if not isinstance(aristas, list):
        error("aristas debe ser una lista")
        return 0
    for ar in aristas:
        etiqueta = f"arista {ar.get('de', '?')} → {ar.get('a', '?')}"
        for lado in ("de", "a"):
            ruta = ar.get(lado, "")
            if not ruta or not (raiz / ruta).is_file():
                error(f"{etiqueta}: '{lado}' apunta a '{ruta}' que no existe en disco")
            elif ruta not in declarados:
                aviso(f"{etiqueta}: '{ruta}' no está declarado en modulos")
        if ar.get("confianza") not in CONFIANZAS:
            error(f"{etiqueta}: confianza {ar.get('confianza')!r} inválida (vista|inferida)")
        evidencia = ar.get("evidencia")
        if not isinstance(evidencia, str) or not evidencia.strip():
            error(f"{etiqueta}: sin evidencia — cita el import/llamada textual (vista) "
                  f"o la razón de la inferencia (inferida)")
    return len(aristas)


def valida_entradas_y_listas(grafo, raiz):
    for ruta in grafo.get("entradas", []):
        if not isinstance(ruta, str) or not (raiz / ruta).is_file():
            error(f"entrada '{ruta}' no existe en disco")
    for campo in ("excluido", "sin_mapear"):
        valores = grafo.get(campo, [])
        if not isinstance(valores, list) or any(not isinstance(v, str) for v in valores):
            error(f"{campo} debe ser una lista de strings")


def main():
    ruta_grafo, raiz = parsea_args(sys.argv[1:])
    raiz = (raiz or raiz_default()).resolve()
    ruta_grafo = ruta_grafo or raiz / "docs/.stark/grafo.json"
    try:
        grafo = json.loads(Path(ruta_grafo).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"No existe {ruta_grafo}. ¿Corriste la Fase 3 de onboarding?")
        sys.exit(2)
    except (json.JSONDecodeError, OSError) as e:
        print(f"No pude cargar {ruta_grafo}: {e}")
        sys.exit(2)
    if not isinstance(grafo, dict):
        print(f"{ruta_grafo} no es un objeto JSON")
        sys.exit(2)

    valida_version_y_commit(grafo, raiz)
    declarados, n_archivos, n_entidades = valida_modulos(grafo, raiz)
    n_aristas = valida_aristas(grafo, raiz, declarados)
    valida_entradas_y_listas(grafo, raiz)

    for a in AVISOS:
        print(f"⚠️  {a}")
    if ERRORES:
        print(f"❌ valida_grafo: {len(ERRORES)} problema(s)")
        for e in ERRORES:
            print(f"  - {e}")
        sys.exit(1)
    extra = f" ({len(AVISOS)} aviso(s))" if AVISOS else ""
    print(f"✅ grafo.json válido: {len(grafo.get('modulos', []))} módulo(s), "
          f"{n_archivos} archivo(s), {n_entidades} entidad(es), {n_aristas} arista(s).{extra}")


if __name__ == "__main__":
    main()
