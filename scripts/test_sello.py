#!/usr/bin/env python3
"""test_sello.py — pruebas de aceptación y regresión de sello.py (RDD).

Monta repos git temporales (remotos bare reales, hooks reales) y ejercita
los escenarios del veredicto original MÁS cada probe adversarial de la
auditoría externa 2026-07-31: tag no empujado, lote sellado + docs en el
mismo push, historial con revert, rename código→docs, multi-remoto,
core.hooksPath, tag lightweight, colisión de receipts, alias de ruta,
symlinks, checkboxes que no invalidan, receipts malformados, borrado de
tags, clon con candado heredado y repos SHA-256.

Requisitos: Python 3.9+ y Git 2.29+ en PATH (sin dependencias de pip).
Uso: python3 scripts/test_sello.py   →   exit 0 = todo verde.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SELLO_SRC = (RAIZ / ".claude/scripts/sello.py").read_text(encoding="utf-8")
FALLOS = []


def run(args, cwd, stdin=""):
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


def nuevo_repo(base, nombre, **config):
    repo = base / nombre
    (repo / ".claude/scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".claude/scripts/sello.py").write_text(SELLO_SRC, encoding="utf-8")
    run(["git", "init", "-q", "-b", "main"], base / nombre)
    git(repo, "config", "user.email", "test@stark")
    git(repo, "config", "user.name", "test")
    for k, v in config.items():
        git(repo, "config", k.replace("_", "."), v)
    (repo / ".gitignore").write_text(".claude/\n")
    return repo


def flujo_principal(base):
    remoto = base / "remoto.git"
    run(["git", "init", "-q", "--bare", str(remoto)], base)
    repo = nuevo_repo(base, "proyecto")
    (repo / "app.py").write_text("v1\n")
    (repo / "docs/requirements.md").write_text(
        "# Requirements: demo\n\n> Estado: PENDIENTE\n\n## R1\nTHE SYSTEM SHALL demo.\n"
    )
    (repo / "docs/tasks.md").write_text(
        "# Tasks: demo\n\n> Estado: PENDIENTE\n\n## Slice 1\n\n- [ ] 1. Implementar demo\n- [ ] 2. Tests de demo\n"
    )
    commit_todo(repo, "inicial")
    git(repo, "remote", "add", "origin", str(remoto))
    caso("instalar-hook cablea el pre-push", sello(repo, "instalar-hook"), True)

    print("— Candado inactivo antes del primer sello —")
    caso("push inicial (specs + código, sin sellos) pasa",
         run(["git", "push", "-q", "-u", "origin", "main"], repo), True)

    print("— Sello de documento —")
    caso("sellar-doc con aprobador real", sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela"), True)
    caso("recién sellado, verificar-doc acepta", sello(repo, "verificar-doc", "docs/requirements.md"), True)
    doc = repo / "docs/requirements.md"
    original = doc.read_text()
    doc.write_text(original.replace("demo.", "demo!"))
    caso("editar una letra tras aprobar bloquea", sello(repo, "verificar-doc", "docs/requirements.md"), False)
    doc.write_text(original)

    print("— Checkboxes no invalidan el plan aprobado (P1-01) —")
    caso("sellar tasks.md", sello(repo, "sellar-doc", "docs/tasks.md", "--por", "Gabriela"), True)
    tasks = repo / "docs/tasks.md"
    tasks.write_text(tasks.read_text().replace("- [ ] 1.", "- [x] 1."))
    caso("marcar [x] una tarea NO invalida el receipt", sello(repo, "verificar-doc", "docs/tasks.md"), True)
    tasks.write_text(tasks.read_text().replace("Tests de demo", "Tarea colada"))
    caso("cambiar el TEXTO del plan sí bloquea", sello(repo, "verificar-doc", "docs/tasks.md"), False)
    tasks.write_text(tasks.read_text().replace("Tarea colada", "Tests de demo"))
    caso("restaurado el texto (checkbox marcado), vuelve a aceptar", sello(repo, "verificar-doc", "docs/tasks.md"), True)

    print("— Re-sellado nunca es silencioso; identidad canónica (P1-05) —")
    caso("re-sellar sin flag se rechaza", sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela"), False)
    caso("re-sellar por ruta ABSOLUTA (alias) también se rechaza",
         sello(repo, "sellar-doc", str(doc.resolve()), "--por", "Gabriela"), False)
    caso("con --re-sellar (nueva aprobación humana) pasa",
         sello(repo, "sellar-doc", "docs/requirements.md", "--por", "Gabriela", "--re-sellar"), True)
    (repo / "docs/a").mkdir()
    (repo / "docs/a/b.md").write_text("# Doc\n\nmismo contenido\n")
    (repo / "docs/a__b.md").write_text("# Doc\n\nmismo contenido\n")
    caso("sellar docs/a/b.md", sello(repo, "sellar-doc", "docs/a/b.md", "--por", "Gabriela"), True)
    caso("docs/a__b.md (colisión de aplanado) NO valida con receipt ajeno",
         sello(repo, "verificar-doc", "docs/a__b.md"), False)
    (repo / "docs/enlace.md").symlink_to(doc.resolve())
    caso("un symlink no se puede sellar", sello(repo, "sellar-doc", "docs/enlace.md", "--por", "Gabriela"), False)
    (repo / "docs/enlace.md").unlink()
    caso("sellar-doc sobre código de producción se rechaza",
         sello(repo, "sellar-doc", "app.py", "--por", "Gabriela"), False)

    print("— Placeholders y receipts malformados (P2-01) —")
    caso("sellar-doc --por '[nombre]' se rechaza", sello(repo, "sellar-doc", "docs/a/b.md", "--por", "[nombre]"), False)
    caso("sellar-lote --por '[nombre]' se rechaza", sello(repo, "sellar-lote", "x9", "--por", "[nombre]"), False)
    receipt = next(p for p in (repo / "docs/.stark/receipts").glob("*.json") if "requirements" in p.name)
    datos = json.loads(receipt.read_text())
    respaldo = receipt.read_text()
    datos["approved_at"] = "2026-99-99"
    receipt.write_text(json.dumps(datos))
    caso("fecha imposible (2026-99-99) en el receipt bloquea", sello(repo, "verificar-doc", "docs/requirements.md"), False)
    receipt.write_text("[]")
    caso("receipt JSON [] bloquea sin reventar", sello(repo, "verificar-doc", "docs/requirements.md"), False)
    receipt.write_text(respaldo)

    print("— Candado activo por receipts: specs pasan, código exige sello —")
    commit_todo(repo, "specs selladas")
    caso("push de solo docs con candado activo pasa", run(["git", "push", "-q", "origin", "main"], repo), True)

    print("— Sello de lote y entrega atómica del tag (P1-02) —")
    (repo / "app.py").write_text("v2\n")
    commit_todo(repo, "lote feature-a-1")
    (repo / "sucio.txt").write_text("x")
    caso("sellar-lote con tree sucio se rechaza", sello(repo, "sellar-lote", "feature-a-1", "--por", "Gabriela"), False)
    (repo / "sucio.txt").unlink()
    caso("id de lote inválido se rechaza", sello(repo, "sellar-lote", "lote uno", "--por", "Gabriela"), False)
    caso("sellar-lote con namespace de feature", sello(repo, "sellar-lote", "feature-a-1", "--por", "Gabriela"), True)
    caso("un lote se sella una sola vez", sello(repo, "sellar-lote", "feature-a-1", "--por", "Gabriela"), False)
    caso("push del código SIN su tag se rechaza (evidencia debe viajar)",
         run(["git", "push", "-q", "origin", "main"], repo), False)
    caso("push de rama y tag JUNTOS pasa",
         run(["git", "push", "-q", "origin", "main", "refs/tags/stark-lote-feature-a-1"], repo), True)

    print("— Por commit, no por diff neto (P1-03) —")
    (repo / "docs/notas.md").write_text("notas\n")
    commit_todo(repo, "docs encima de lote sellado")
    caso("docs-only encima de código ya entregado pasa", run(["git", "push", "-q", "origin", "main"], repo), True)
    (repo / "app.py").write_text("v3\n")
    commit_todo(repo, "código del lote feature-a-2")
    (repo / "docs/notas.md").write_text("notas v2\n")
    commit_todo(repo, "docs del cierre del lote")
    caso("sellar el tip cubre el código anterior del lote",
         sello(repo, "sellar-lote", "feature-a-2", "--por", "Gabriela"), True)
    caso("push de lote multi-commit (código + docs) sellado en el tip pasa",
         run(["git", "push", "-q", "origin", "main", "refs/tags/stark-lote-feature-a-2"], repo), True)
    punto_estable = git(repo, "rev-parse", "HEAD")
    (repo / "app.py").write_text("secreto colado\n")
    commit_todo(repo, "código no validado")
    (repo / "app.py").write_text("v3\n")
    commit_todo(repo, "revert del colado")
    caso("historial con commit de código no sellado + revert se bloquea (diff neto vacío no engaña)",
         run(["git", "push", "-q", "origin", "main"], repo), False)
    git(repo, "reset", "-q", "--hard", punto_estable)
    git(repo, "mv", "app.py", "docs/app_disfrazado.py")
    commit_todo(repo, "rename código a docs")
    caso("rename código→docs/ se clasifica por ambas rutas y se bloquea",
         run(["git", "push", "-q", "origin", "main"], repo), False)
    git(repo, "reset", "-q", "--hard", punto_estable)

    print("— Tags inmutables y tags falsos (P1-02, P2-01) —")
    caso("borrar un tag stark-lote-* del remoto se rechaza",
         run(["git", "push", "-q", "origin", ":refs/tags/stark-lote-feature-a-1"], repo), False)
    git(repo, "commit", "-q", "--allow-empty", "-m", "Tests: PASS\nAprobado por: Humano\nFecha: 2026-07-31")
    git(repo, "tag", "stark-lote-falso")  # lightweight: el mensaje es del commit
    caso("tag lightweight con mensaje fabricado NO cuenta como sello",
         sello(repo, "verificar-push"), False)
    git(repo, "tag", "-d", "stark-lote-falso")
    git(repo, "reset", "-q", "--hard", punto_estable)

    print("— Refs empujadas, dirty y untracked —")
    git(repo, "branch", "evil")
    git(repo, "checkout", "-q", "evil")
    (repo / "app.py").write_text("codigo NO validado\n")
    commit_todo(repo, "evil")
    git(repo, "checkout", "-q", "main")
    caso("push de rama no sellada por nombre (evil:main) se bloquea",
         run(["git", "push", "-q", "origin", "evil:main"], repo), False)
    git(repo, "branch", "-D", "evil")
    (repo / "app.py").write_text("v4\n")
    commit_todo(repo, "lote feature-a-3")
    caso("sellar-lote feature-a-3", sello(repo, "sellar-lote", "feature-a-3", "--por", "Gabriela"), True)
    (repo / "app.py").write_text("v4-dirty\n")
    caso("código modificado sin commit bloquea el push", run(["git", "push", "-q", "origin", "main"], repo), False)
    git(repo, "checkout", "-q", "--", "app.py")
    (repo / "colado.txt").write_text("secreto\n")
    caso("archivo untracked bloquea el push", run(["git", "push", "-q", "origin", "main"], repo), False)
    (repo / "colado.txt").unlink()
    caso("limpio y sellado, el push pasa",
         run(["git", "push", "-q", "origin", "main", "refs/tags/stark-lote-feature-a-3"], repo), True)

    print("— Multi-remoto: ref nueva se evalúa contra SU remoto (P1-03) —")
    remoto_b = base / "remoto-b.git"
    run(["git", "init", "-q", "--bare", str(remoto_b)], base)
    git(repo, "remote", "add", "b", str(remoto_b))
    (repo / "app.py").write_text("solo en A, sin sellar\n")
    commit_todo(repo, "código no sellado para B")
    caso("ref nueva hacia remoto B no se excusa con los refs de origin",
         run(["git", "push", "-q", "b", "main"], repo), False)
    fantasma = git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/b/fantasma", fantasma)
    git(repo, "checkout", "-q", "-b", "colada")
    caso("caché de remote-tracking obsoleta/manipulada tampoco excusa código (ls-remote manda)",
         run(["git", "push", "-q", "b", "colada"], repo), False)
    git(repo, "checkout", "-q", "main")
    git(repo, "branch", "-D", "colada")
    git(repo, "update-ref", "-d", "refs/remotes/b/fantasma")
    git(repo, "reset", "-q", "--hard", "HEAD~1")

    print("— Clon hereda el candado (receipts commiteados) —")
    clon = base / "clon"
    run(["git", "clone", "-q", str(remoto), str(clon)], base)
    (clon / ".claude/scripts").mkdir(parents=True)
    (clon / ".claude/scripts/sello.py").write_text(SELLO_SRC, encoding="utf-8")
    git(clon, "config", "user.email", "t@t")
    git(clon, "config", "user.name", "t")
    caso("instalar-hook en el clon", sello(clon, "instalar-hook"), True)
    (clon / "app.py").write_text("clon sin validar\n")
    commit_todo(clon, "código desde el clon")
    caso("el clon NO nace permisivo: código sin sellar se bloquea",
         run(["git", "push", "-q", "origin", "main"], clon), False)


def hooks_path(base):
    print("— core.hooksPath y worktrees (P1-04) —")
    remoto = base / "remoto-hp.git"
    run(["git", "init", "-q", "--bare", str(remoto)], base)
    repo = nuevo_repo(base, "proyecto-hp", core_hooksPath=".githooks")
    (repo / "app.py").write_text("v1\n")
    (repo / "docs/doc.md").write_text("# Doc\n\n> Estado: PENDIENTE\n\nx\n")
    commit_todo(repo, "inicial")
    git(repo, "remote", "add", "origin", str(remoto))
    caso("instalar-hook respeta core.hooksPath", sello(repo, "instalar-hook"), True)
    caso("el hook quedó donde git lo ejecuta (.githooks/pre-push)",
         run(["test", "-x", ".githooks/pre-push"], repo), True)
    caso("sellar doc activa el candado", sello(repo, "sellar-doc", "docs/doc.md", "--por", "Gabriela"), True)
    commit_todo(repo, "doc sellado")
    (repo / "app.py").write_text("v2 sin sellar\n")
    commit_todo(repo, "código sin sellar")
    caso("con core.hooksPath, el push de código sin sellar SÍ se bloquea",
         run(["git", "push", "-q", "-u", "origin", "main"], repo), False)


def hook_ajeno(base):
    print("— El instalador no pisa hooks ajenos ni modificados —")
    repo = nuevo_repo(base, "proyecto-hook")
    (repo / "x.txt").write_text("x\n")
    commit_todo(repo, "inicial")
    hooks = Path(git(repo, "rev-parse", "--git-path", "hooks"))
    hooks = hooks if hooks.is_absolute() else (repo / hooks)
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "pre-push").write_text("#!/bin/sh\necho hook del equipo\n")
    caso("hook ajeno: instalar-hook se rehúsa", sello(repo, "instalar-hook"), False)
    (hooks / "pre-push").write_text("#!/bin/sh\n# stark (RDD) modificado a mano\nexit 0\n")
    caso("hook stark modificado: instalar-hook se rehúsa", sello(repo, "instalar-hook"), False)


def sha256_repo(base):
    print("— Repos SHA-256 (P2-03) —")
    sonda = base / "sonda-sha256"
    r = run(["git", "init", "-q", "--object-format=sha256", str(sonda)], base)
    if r.returncode != 0:
        print("  ⚠️  git sin soporte sha256 en este entorno — escenario omitido")
        return
    shutil.rmtree(sonda)
    remoto = base / "remoto-256.git"
    run(["git", "init", "-q", "--bare", "--object-format=sha256", str(remoto)], base)
    repo = base / "proyecto-256"
    (repo / ".claude/scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".claude/scripts/sello.py").write_text(SELLO_SRC, encoding="utf-8")
    run(["git", "init", "-q", "-b", "main", "--object-format=sha256", str(repo)], base)
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (repo / ".gitignore").write_text(".claude/\n")
    (repo / "docs/doc.md").write_text("# Doc\n\n> Estado: PENDIENTE\n\nx\n")
    (repo / "app.py").write_text("v1\n")
    commit_todo(repo, "inicial")
    git(repo, "remote", "add", "origin", str(remoto))
    caso("instalar-hook (sha256)", sello(repo, "instalar-hook"), True)
    caso("sellar doc (sha256) activa el candado", sello(repo, "sellar-doc", "docs/doc.md", "--por", "Gabriela"), True)
    commit_todo(repo, "doc sellado")
    caso("ref nueva en repo sha256: código sin sellar se bloquea (OID nulo de 64 ceros)",
         run(["git", "push", "-q", "-u", "origin", "main"], repo), False)
    caso("sellar-lote (sha256)", sello(repo, "sellar-lote", "s1", "--por", "Gabriela"), True)
    caso("push sellado con tag (sha256) pasa",
         run(["git", "push", "-q", "-u", "origin", "main", "refs/tags/stark-lote-s1"], repo), True)


def untracked_oculto(base):
    print("— Config local no debilita el sello (P2-02) —")
    repo = nuevo_repo(base, "proyecto-unt", status_showUntrackedFiles="no")
    (repo / "x.txt").write_text("x\n")
    commit_todo(repo, "inicial")
    (repo / "oculto.txt").write_text("secreto\n")
    caso("status.showUntrackedFiles=no no oculta untracked a sellar-lote",
         sello(repo, "sellar-lote", "u1", "--por", "Gabriela"), False)


def main():
    base = Path(tempfile.mkdtemp(prefix="stark-rdd-"))
    try:
        flujo_principal(base)
        hooks_path(base)
        hook_ajeno(base)
        untracked_oculto(base)
        sha256_repo(base)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print()
    if FALLOS:
        print(f"❌ test_sello.py: {len(FALLOS)} caso(s) fallaron")
        for f in FALLOS:
            print(f"  - {f}")
        sys.exit(1)
    print("✅ test_sello.py: todos los escenarios RDD (incluidos los probes de la auditoría) en verde.")


if __name__ == "__main__":
    main()
