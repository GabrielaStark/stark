#!/usr/bin/env python3
"""test_valida_grafo.py — pruebas de valida_grafo.py.

Monta un proyecto temporal con archivos de tamaños conocidos y ejercita el
validador contra variantes del grafo.json: mapa válido, rutas inventadas,
rangos fuera del archivo, rangos invertidos, confianza inválida, evidencia
vacía, version no soportada, entradas fantasma, desvío de líneas (aviso),
JSON roto, mapa ausente y detección de mapa desactualizado vía git.

Requisitos: Python 3.9+ (git solo para los casos de staleness; sin pip).
Uso: python3 scripts/test_valida_grafo.py   →   exit 0 = todo verde.
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / ".claude/scripts/valida_grafo.py"
FALLOS = []


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def valida(proyecto):
    return run([sys.executable, str(SCRIPT), "--raiz", str(proyecto)], proyecto)


def caso(desc, resultado, exit_esperado, contiene=None, no_contiene=None):
    salida = resultado.stdout + resultado.stderr
    ok = resultado.returncode == exit_esperado
    if ok and contiene is not None:
        ok = contiene in salida
    if ok and no_contiene is not None:
        ok = no_contiene not in salida
    print(f"  {'✅' if ok else '❌'} {desc}")
    if not ok:
        FALLOS.append(f"{desc}\n    exit={resultado.returncode} (esperaba {exit_esperado})"
                      f"\n    salida: {salida.strip()}")


def archivo_de_n_lineas(path, n):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"linea {i}" for i in range(1, n + 1)) + "\n", encoding="utf-8")


def monta_proyecto(base):
    proyecto = base / "proyecto"
    (proyecto / "docs/.stark").mkdir(parents=True)
    archivo_de_n_lineas(proyecto / "src/facturacion/calculo.php", 200)
    archivo_de_n_lineas(proyecto / "src/clientes/repositorio.php", 50)
    archivo_de_n_lineas(proyecto / "public/index.php", 10)
    return proyecto


def grafo_base():
    return {
        "version": 1,
        "commit": "deadbeef",
        "entradas": ["public/index.php"],
        "excluido": ["vendor/ — dependencias"],
        "sin_mapear": [],
        "modulos": [
            {
                "ruta": "src/facturacion/",
                "proposito": "cálculo y emisión de facturas",
                "archivos": [
                    {
                        "ruta": "src/facturacion/calculo.php",
                        "lineas": 200,
                        "entidades": [
                            {"nombre": "calcularTotales", "tipo": "funcion", "lineas": "~120-180"}
                        ],
                    }
                ],
            },
            {
                "ruta": "src/clientes/",
                "proposito": "acceso a datos de clientes",
                "archivos": [
                    {"ruta": "src/clientes/repositorio.php", "lineas": 50, "entidades": []}
                ],
            },
        ],
        "aristas": [
            {
                "de": "src/facturacion/calculo.php",
                "a": "src/clientes/repositorio.php",
                "evidencia": "require_once '../clientes/repositorio.php' (L3)",
                "confianza": "vista",
            }
        ],
    }


def escribe_grafo(proyecto, grafo):
    ruta = proyecto / "docs/.stark/grafo.json"
    if isinstance(grafo, str):
        ruta.write_text(grafo, encoding="utf-8")
    else:
        ruta.write_text(json.dumps(grafo, ensure_ascii=False, indent=2), encoding="utf-8")


def variante(mutador):
    g = copy.deepcopy(grafo_base())
    mutador(g)
    return g


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        proyecto = monta_proyecto(base)

        print("Casos de aceptación:")
        escribe_grafo(proyecto, grafo_base())
        caso("mapa válido pasa", valida(proyecto), 0, contiene="✅")

        escribe_grafo(proyecto, variante(
            lambda g: g["modulos"][0]["archivos"][0].__setitem__("ruta", "src/facturacion/no_existe.php")))
        caso("archivo inventado truena", valida(proyecto), 1, contiene="no existe")

        escribe_grafo(proyecto, variante(
            lambda g: g["modulos"][0]["archivos"][0]["entidades"][0].__setitem__("lineas", "~500-600")))
        caso("rango fuera del archivo truena", valida(proyecto), 1, contiene="fuera del archivo")

        escribe_grafo(proyecto, variante(
            lambda g: g["modulos"][0]["archivos"][0]["entidades"][0].__setitem__("lineas", "180-120")))
        caso("rango invertido truena", valida(proyecto), 1, contiene="invertido")

        escribe_grafo(proyecto, variante(
            lambda g: g["modulos"][0]["archivos"][0]["entidades"][0].__setitem__("lineas", "por ahí del final")))
        caso("rango ilegible truena", valida(proyecto), 1, contiene="forma")

        escribe_grafo(proyecto, variante(
            lambda g: g["aristas"][0].__setitem__("confianza", "adivinada")))
        caso("confianza inválida truena", valida(proyecto), 1, contiene="inválida")

        escribe_grafo(proyecto, variante(
            lambda g: g["aristas"][0].__setitem__("evidencia", "  ")))
        caso("evidencia vacía truena", valida(proyecto), 1, contiene="sin evidencia")

        escribe_grafo(proyecto, variante(
            lambda g: g["aristas"][0].__setitem__("a", "src/clientes/fantasma.php")))
        caso("arista a archivo inexistente truena", valida(proyecto), 1, contiene="no existe")

        escribe_grafo(proyecto, variante(lambda g: g.__setitem__("version", 2)))
        caso("version no soportada truena", valida(proyecto), 1, contiene="no soportada")

        escribe_grafo(proyecto, variante(lambda g: g.__setitem__("commit", "")))
        caso("commit ausente truena", valida(proyecto), 1, contiene="commit")

        escribe_grafo(proyecto, variante(
            lambda g: g.__setitem__("entradas", ["public/nope.php"])))
        caso("entrada inexistente truena", valida(proyecto), 1, contiene="entrada")

        escribe_grafo(proyecto, variante(
            lambda g: g["modulos"][0]["archivos"][0].__setitem__("lineas", 400)))
        caso("líneas desviadas solo avisa", valida(proyecto), 0, contiene="desviado")

        escribe_grafo(proyecto, variante(
            lambda g: g["aristas"].append({"de": "src/facturacion/calculo.php",
                                           "a": "public/index.php",
                                           "evidencia": "include index (L1)",
                                           "confianza": "vista"})))
        caso("arista a archivo real no declarado solo avisa", valida(proyecto), 0,
             contiene="no está declarado")

        escribe_grafo(proyecto, "{ esto no es json")
        caso("JSON roto → exit 2", valida(proyecto), 2, contiene="No pude cargar")

        (proyecto / "docs/.stark/grafo.json").unlink()
        caso("mapa ausente → exit 2", valida(proyecto), 2, contiene="No existe")

        print("Staleness vía git:")
        r = run(["git", "init", "-q", "-b", "main"], proyecto)
        if r.returncode == 0:
            run(["git", "config", "user.email", "test@stark"], proyecto)
            run(["git", "config", "user.name", "test"], proyecto)
            run(["git", "add", "-A"], proyecto)
            run(["git", "commit", "-q", "-m", "base"], proyecto)
            head = run(["git", "rev-parse", "HEAD"], proyecto).stdout.strip()

            escribe_grafo(proyecto, variante(lambda g: g.__setitem__("commit", head)))
            caso("commit vigente no avisa", valida(proyecto), 0, no_contiene="desactualizado")

            escribe_grafo(proyecto, grafo_base())  # commit deadbeef ≠ HEAD
            caso("commit viejo avisa sin tronar", valida(proyecto), 0, contiene="desactualizado")
        else:
            print("  ⚠️ git no disponible — casos de staleness saltados")

    if FALLOS:
        print(f"\n❌ test_valida_grafo: {len(FALLOS)} fallo(s)")
        for f in FALLOS:
            print(f"  - {f}")
        sys.exit(1)
    print("\n✅ test_valida_grafo: todos los casos en verde.")


if __name__ == "__main__":
    main()
