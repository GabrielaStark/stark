#!/usr/bin/env python3
"""test_sello.py — pruebas de aceptación reproducibles de sello.py (RDD).

Monta un repo git temporal (con remoto bare real y hook pre-push instalado)
y ejercita los escenarios completos que sostienen el claim del README:
documento editado tras aprobarse bloquea la fase siguiente; código dirty,
untracked, commits sin sellar o ramas no selladas empujadas por nombre
bloquean el push; los placeholders se rechazan; el re-sellado silencioso
no existe; los pushes de solo-documentación pasan; el candado se activa
con el primer lote sellado.

Uso: python3 scripts/test_sello.py   →   exit 0 = todo verde. Sin dependencias.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FALLOS = []


def run(args, cwd, stdin=None):
    return subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True)


def git(repo, *args):
    r = run(["git", *args], repo)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r.stdout.strip()


def sello(repo, *args):
    return run([sys.executable, ".claude/scripts/sello.py", *args], repo)


def caso(desc, resultado, esperado_ok):
    exito = (resultado.returncode == 0) == esperado_ok
    print(f"  {'✅' if exito else '❌'} {desc}")
    if not exito:
        FALLOS.append(
            f"{desc}\n    exit={resultado.returncode}"
            f"\n    stdout: {resultado.stdout.strip()}\n    stderr: {resultado.stderr.strip()}"
        )


def commit_todo(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def main():
    base = Path(tempfile.mkdtemp(prefix="stark-rdd-"))
    remoto = base / "remoto.git"
    repo = base / "proyecto"
    run(["git", "init", "-q", "--bare", str(remoto)], base)
    (repo / ".claude/scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".claude/scripts/sello.py").write_text(
        (RAIZ / ".claude/scripts/sello.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@stark")
    git(repo, "config", "user.name", "test")
    (repo / ".gitignore").write_text(".claude/\n")
    (repo / "app.py").write_text("v1\n")
    (repo / "docs/requirements.md").write_text(
        "# Requirements: demo\n\n> Estado: PENDIENTE\n\n## R1\nTHE SYSTEM SHALL demo.\n"
    )
    commit_todo(repo, "inicial")
    git(repo, "remote", "add", "origin", str(remoto))
    caso("instalar-hook cablea el pre-push", sello(repo, "instalar-hook"), True)

    print("— Candado inactivo antes del primer lote —")
    caso("push inicial (specs + código, sin lotes sellados) pasa",
         run(["git", "push", "-q", "-u", "origin", "main"], repo), True)

    print("— Sello de documento (prueba 1 del veredicto) —")
    caso("sellar-doc con aprobador real", sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela"), True)
    caso("recién sellado, verificar-doc acepta", sello(repo, "verificar-doc", "docs/requirements.md"), True)
    doc = repo / "docs/requirements.md"
    doc.write_text(doc.read_text().replace("demo.", "demo!"))
    caso("editar una letra tras aprobar bloquea la fase siguiente", sello(repo, "verificar-doc", "docs/requirements.md"), False)
    git(repo, "checkout", "-q", "--", "docs/requirements.md")

    print("— Re-sellado nunca es silencioso —")
    caso("sellar-doc sobre doc ya sellado, sin flag, se rechaza",
         sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela"), False)
    caso("con --re-sellar (nueva aprobación humana) pasa",
         sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela", "--re-sellar"), True)

    print("— Placeholders (prueba 5 del veredicto) —")
    caso("sellar-doc --por '[nombre]' se rechaza", sello(repo, "sellar-doc", "docs/requirements.md", "--por", "[nombre]"), False)
    caso("sellar-lote --por '[nombre]' se rechaza", sello(repo, "sellar-lote", "9", "--por", "[nombre]"), False)
    receipt = next((repo / "docs/.stark/receipts").glob("*.json"))
    datos = json.loads(receipt.read_text())
    datos["approved_by"] = "[nombre]"
    receipt.write_text(json.dumps(datos))
    caso("receipt hand-editado con placeholder bloquea", sello(repo, "verificar-doc", "docs/requirements.md"), False)
    caso("re-sellar tras nueva aprobación lo repara",
         sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela", "--re-sellar"), True)

    print("— Sello de lote —")
    commit_todo(repo, "lote 1: specs selladas + código")
    (repo / "sucio.txt").write_text("x")
    caso("sellar-lote con tree sucio se rechaza", sello(repo, "sellar-lote", "1", "--por", "Gabriela"), False)
    (repo / "sucio.txt").unlink()
    caso("sellar-lote con tree limpio sella", sello(repo, "sellar-lote", "1", "--por", "Gabriela"), True)
    caso("un lote se sella una sola vez", sello(repo, "sellar-lote", "1", "--por", "Gabriela"), False)
    caso("verificar-push manual con HEAD sellado acepta", sello(repo, "verificar-push"), True)
    caso("push del commit sellado pasa", run(["git", "push", "-q", "origin", "main", "--tags"], repo), True)

    print("— Dirty y untracked tras validar (pruebas 2-3 del veredicto) —")
    (repo / "app.py").write_text("v2\n")
    commit_todo(repo, "lote 2")
    caso("sellar-lote 2", sello(repo, "sellar-lote", "2", "--por", "Gabriela"), True)
    (repo / "app.py").write_text("v2-dirty\n")
    caso("código modificado sin commit bloquea el push", run(["git", "push", "-q", "origin", "main"], repo), False)
    git(repo, "checkout", "-q", "--", "app.py")
    (repo / "colado.txt").write_text("secreto\n")
    caso("archivo untracked bloquea el push", run(["git", "push", "-q", "origin", "main"], repo), False)
    (repo / "colado.txt").unlink()
    caso("limpio, el push del lote 2 pasa", run(["git", "push", "-q", "origin", "main", "--tags"], repo), True)

    print("— Refs empujadas, no HEAD (bypass cazado) —")
    git(repo, "branch", "evil")
    git(repo, "checkout", "-q", "evil")
    (repo / "app.py").write_text("codigo NO validado\n")
    commit_todo(repo, "evil")
    git(repo, "checkout", "-q", "main")
    caso("push de rama no sellada por nombre (evil:main) bloquea aunque HEAD esté sellado",
         run(["git", "push", "-q", "origin", "evil:main"], repo), False)
    git(repo, "branch", "-D", "evil")

    print("— Commit posterior sin sellar (prueba 4) y push sin sellar (prueba 6) —")
    (repo / "app.py").write_text("v3\n")
    commit_todo(repo, "cambio posterior sin sellar")
    caso("commit de código tras validar, sin sellar, bloquea el push",
         run(["git", "push", "-q", "origin", "main"], repo), False)
    caso("sellar-lote 3 lo habilita", sello(repo, "sellar-lote", "3", "--por", "Gabriela"), True)
    caso("push sellado pasa", run(["git", "push", "-q", "origin", "main", "--tags"], repo), True)

    print("— Solo documentación pasa con el candado activo —")
    (repo / "docs/notas.md").write_text("specs nuevas\n")
    commit_todo(repo, "specs de la siguiente fase")
    caso("push que solo toca docs/ pasa sin sello", run(["git", "push", "-q", "origin", "main"], repo), True)

    print()
    if FALLOS:
        print(f"❌ test_sello.py: {len(FALLOS)} caso(s) fallaron")
        for f in FALLOS:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ test_sello.py: todos los escenarios RDD en verde.")


if __name__ == "__main__":
    main()
