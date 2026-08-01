#!/usr/bin/env python3
"""sello.py — autoridad ejecutable de los sellos RDD de stark (v2).

Los sellos visibles en Markdown son cortesía de lectura; la autoridad es esto:

- Sello de documento: receipt JSON (schema 2) con sha256 del contenido
  aprobado, en docs/.stark/receipts/. La identidad es la ruta canónica
  relativa al repo (symlinks y rutas fuera del repo se rechazan; el nombre
  del receipt lleva digest de la ruta para que no haya colisiones). El hash
  usa canonicalización `checkbox-v1`: el ESTADO de los checkboxes
  (`[ ]`/`[x]`) no cuenta — marcar tareas no invalida el sello; cualquier
  otro cambio, sí.
- Sello de lote: annotated tag `stark-lote-<id>` sobre el commit validado.
  <id> es libre ([A-Za-z0-9._-]); en mantenimiento usa `<feature>-<n>` para
  que los lotes de features distintas no colisionen.
- verificar-push (hook): valida POR COMMIT lo que entra al remoto objetivo.
  Cada commit empujado que toque código debe estar cubierto por un tag de
  lote (ser el commit sellado o ancestro de uno sellado dentro del push);
  el tag que cubre debe viajar en el mismo push o existir ya en el remoto;
  borrar o mover tags stark-lote-* se rechaza; los commits que solo tocan
  documentación (docs/, README, LICENSE, CONSTITUTION, .gitignore) pasan.
  El candado se activa con el primer sello (tag local O receipts
  commiteados — un clon con receipts ya nace con el candado puesto).

Límites (dichos de frente): el sello REGISTRA identidad y la declaración
`Tests: PASS` — no los firma criptográficamente ni ejecuta la suite; eso lo
garantiza el gate humano. El hook es por clon y `--no-verify` lo salta: es
un candado contra el descuido y la deriva, no contra la mala fe. La
garantía definitiva contra manipulación requiere además reglas server-side
(tags protegidos, CI obligatorio). La exención de docs/ es política
deliberada (specs y prototipo); si tu docs/ contiene código de producción,
ajusta NO_CODIGO/solo_docs a tu proyecto.

Uso:
  python3 .claude/scripts/sello.py sellar-doc <artefacto.md> --por "Nombre" [--re-sellar]
  python3 .claude/scripts/sello.py verificar-doc <artefacto.md>
  python3 .claude/scripts/sello.py sellar-lote <id> --por "Nombre" [--invariantes]
  python3 .claude/scripts/sello.py verificar-push [--remoto <nombre>] [--url <url>]
  python3 .claude/scripts/sello.py instalar-hook

Códigos de salida: 0 = OK, 1 = bloqueado/inválido, 2 = error de uso.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VERSION = "0.2.0"
SCHEMA = 2
CANONICALIZACION = "checkbox-v1"
RECEIPTS_DIR = "docs/.stark/receipts"
PREFIJO_TAG = "stark-lote-"
NO_CODIGO = {"CONSTITUTION.md", "README.md", "LICENSE", "LICENSE.stark", ".gitignore"}
CHECKBOX_RE = re.compile(rb"^(\s*[-*] )\[[xX]\]", re.M)
ID_LOTE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
MARCADOR_HOOK = "stark (RDD)"


def fallo(msg: str) -> None:
    print(f"❌ SELLO: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✅ SELLO: {msg}")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        fallo(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r.stdout


def git_rc(*args: str) -> "subprocess.CompletedProcess":
    return subprocess.run(["git", *args], capture_output=True, text=True)


def es_sha_cero(sha: str) -> bool:
    # OID nulo por contenido, no por longitud: cubre SHA-1 (40) y SHA-256 (64).
    return bool(sha) and set(sha) <= {"0"}


def raiz_repo() -> Path:
    return Path(git("rev-parse", "--show-toplevel").strip()).resolve()


def valida_nombre(nombre: str) -> str:
    n = (nombre or "").strip()
    if not n or "[" in n or "]" in n or "YYYY" in n or n.lower() == "nombre":
        fallo(f"nombre de aprobador inválido: {nombre!r}. Debe ser una persona real, sin placeholders.")
    return n


def valida_fecha(fecha: str) -> bool:
    try:
        datetime.date.fromisoformat(fecha)
        return True
    except (ValueError, TypeError):
        return False


def ruta_canonica(artefacto: str) -> "tuple[str, Path]":
    raiz = raiz_repo()
    ruta = Path(artefacto)
    if ruta.is_symlink():
        fallo(f"{artefacto} es un symlink: los artefactos sellados deben ser archivos reales del repo.")
    absoluta = ruta.resolve() if ruta.is_absolute() else (Path.cwd() / ruta).resolve()
    try:
        rel = absoluta.relative_to(raiz)
    except ValueError:
        fallo(f"{artefacto} resuelve fuera del repo ({raiz}).")
    return rel.as_posix(), absoluta


def contenido_canonico(absoluta: Path) -> bytes:
    # checkbox-v1: el ESTADO de los checkboxes no forma parte del contenido
    # aprobado — marcar [x] al cerrar tareas no invalida el sello.
    return CHECKBOX_RE.sub(rb"\1[ ]", absoluta.read_bytes())


def hash_canonico(absoluta: Path) -> str:
    return "sha256:" + hashlib.sha256(contenido_canonico(absoluta)).hexdigest()


def ruta_receipt(rel: str, raiz: Path) -> Path:
    plano = rel.replace("/", "__")
    sufijo = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:8]
    return raiz / RECEIPTS_DIR / f"{plano}.{sufijo}.json"


def escribe_atomico(destino: Path, texto: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, destino)


def sellar_doc(artefacto: str, por: str, re_sellar: bool = False) -> None:
    por = valida_nombre(por)
    rel, absoluta = ruta_canonica(artefacto)
    if not absoluta.is_file():
        fallo(f"no existe el artefacto {artefacto}")
    raiz = raiz_repo()
    destino = ruta_receipt(rel, raiz)
    if destino.is_file() and not re_sellar:
        try:
            r = json.loads(destino.read_text(encoding="utf-8"))
            quien = f"{r.get('approved_by')} el {r.get('approved_at')}"
        except (json.JSONDecodeError, AttributeError):
            quien = "(receipt ilegible)"
        fallo(
            f"{rel} ya tiene receipt (aprobado por {quien}). Re-sellar PISA esa aprobación:\n"
            "   hazlo solo tras una NUEVA aprobación humana explícita, con --re-sellar."
        )
    hoy = datetime.date.today().isoformat()
    sello = f"> Aprobado por {por} — {hoy}"
    lineas = absoluta.read_text(encoding="utf-8").splitlines()
    reemplazada = False
    for i, linea in enumerate(lineas):
        if linea.startswith("> Estado: PENDIENTE") or linea.startswith("> Aprobado por "):
            lineas[i] = sello
            reemplazada = True
            break
    if not reemplazada:
        for i, linea in enumerate(lineas):
            if linea.startswith("# "):
                lineas[i + 1 : i + 1] = ["", sello]
                break
        else:
            fallo(f"{rel} no tiene título H1 donde estampar el sello")
    absoluta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    receipt = {
        "schema": SCHEMA,
        "sello_version": VERSION,
        "artifact": rel,
        "artifact_hash": hash_canonico(absoluta),
        "canonicalization": CANONICALIZACION,
        "approved_by": por,
        "approved_at": hoy,
    }
    escribe_atomico(destino, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    ok(f"{rel} sellado por {por} ({hoy}). Receipt: {destino.relative_to(raiz)}")


def verificar_doc(artefacto: str) -> None:
    rel, absoluta = ruta_canonica(artefacto)
    if not absoluta.is_file():
        fallo(f"no existe el artefacto {artefacto}")
    raiz = raiz_repo()
    destino = ruta_receipt(rel, raiz)
    if not destino.is_file():
        fallo(f"{rel} no tiene receipt ({destino.relative_to(raiz)}). El documento no está aprobado.")
    try:
        receipt = json.loads(destino.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fallo(f"receipt corrupto (JSON inválido): {destino.relative_to(raiz)}")
    if not isinstance(receipt, dict):
        fallo(f"receipt malformado (no es un objeto JSON): {destino.relative_to(raiz)}")
    if receipt.get("schema") != SCHEMA:
        fallo(f"receipt con schema desconocido ({receipt.get('schema')!r}, esperado {SCHEMA}): re-aprueba y re-sella.")
    if receipt.get("artifact") != rel:
        fallo(
            f"el receipt es de OTRO artefacto ({receipt.get('artifact')!r}, no {rel!r}): "
            "un receipt no es transferible entre rutas."
        )
    por = receipt.get("approved_by")
    if not isinstance(por, str) or not por or "[" in por or "YYYY" in por or por.lower() == "nombre":
        fallo(f"receipt con aprobador inválido: {por!r}")
    fecha = receipt.get("approved_at")
    if not isinstance(fecha, str) or not valida_fecha(fecha):
        fallo(f"receipt con fecha inválida (debe ser una fecha real YYYY-MM-DD): {fecha!r}")
    actual = hash_canonico(absoluta)
    if receipt.get("artifact_hash") != actual:
        fallo(
            f"{rel} CAMBIÓ después de aprobarse.\n"
            f"   aprobado: {receipt.get('artifact_hash')}\n"
            f"   actual:   {actual}\n"
            "   (El estado de los checkboxes [ ]/[x] NO cuenta: marcar tareas no invalida el sello.)\n"
            "   La versión aprobada ya no es la versión presente: re-aprueba y re-sella antes de avanzar."
        )
    ok(f"{rel} coincide con lo aprobado por {por} el {fecha}.")


def exige_tree_limpio() -> None:
    porcelain = git("status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none").strip()
    if porcelain:
        fallo(
            "working tree sucio (archivos modificados, staged o untracked):\n"
            + porcelain
            + "\n   Lo validado debe ser exactamente lo commiteado: commitea o descarta antes de sellar/pushear."
        )


def sellar_lote(lote_id: str, por: str, invariantes: bool) -> None:
    por = valida_nombre(por)
    if not ID_LOTE_RE.match(lote_id):
        fallo(f"id de lote inválido: {lote_id!r} (usa [A-Za-z0-9._-]; en mantenimiento: <feature>-<n>).")
    exige_tree_limpio()
    tag = f"{PREFIJO_TAG}{lote_id}"
    if git("tag", "-l", tag).strip():
        fallo(f"el tag {tag} ya existe. Un lote se sella una sola vez (¿features distintas? usa <feature>-<n>).")
    hoy = datetime.date.today().isoformat()
    msg = "Tests: PASS\n"
    if invariantes:
        msg += "Invariantes: PASS\n"
    msg += f"Aprobado por: {por}\nFecha: {hoy}\nSello: v{VERSION}"
    git("tag", "-a", tag, "-m", msg)
    head = git("rev-parse", "HEAD").strip()
    ok(f"lote {lote_id} sellado: tag {tag} → commit {head} (por {por}, {hoy}).")
    print(f"   Empuja rama y tag JUNTOS (el hook lo exige): git push <remoto> <rama> refs/tags/{tag}")


def tag_valido_en(sha: str) -> "str | None":
    tags = [t for t in git("tag", "--points-at", sha).splitlines() if t.startswith(PREFIJO_TAG)]
    for tag in tags:
        if git_rc("cat-file", "-t", f"refs/tags/{tag}").stdout.strip() != "tag":
            continue  # lightweight: el mensaje sería el del commit, no una aprobación
        contenido = git("tag", "-l", "--format=%(contents)", tag)
        m = re.search(r"Aprobado por: (.+)", contenido)
        f = re.search(r"Fecha: (\S+)", contenido)
        if (
            "Tests: PASS" in contenido
            and m and "[" not in m.group(1) and "YYYY" not in m.group(1)
            and f and valida_fecha(f.group(1))
        ):
            return tag
    return None


def solo_docs(archivos: list) -> bool:
    return all(a in NO_CODIGO or a.startswith("docs/") for a in archivos)


def archivos_de_commit(sha: str) -> list:
    # --no-renames: un rename código→docs/ aparece como borrado + alta y se
    # clasifica por AMBAS rutas. -c cubre merges con cambios propios; --root,
    # el commit inicial.
    salida = git("diff-tree", "-r", "-c", "--root", "--no-commit-id", "--name-only", "--no-renames", "-z", sha)
    return [a for a in salida.split("\0") if a]


def commits_introducidos(local_sha: str, remote_sha: str, remoto: "str | None") -> list:
    if es_sha_cero(remote_sha):
        # Ref nueva: cuentan los commits que el REMOTO OBJETIVO no tiene aún
        # (no cualquier remoto — eso dejaba pasar código presente en otro remote).
        exclusion = f"--remotes={remoto}" if remoto else "--remotes"
        return [c for c in git("rev-list", local_sha, "--not", exclusion).splitlines() if c]
    r = git_rc("rev-list", f"{remote_sha}..{local_sha}")
    if r.returncode != 0:
        fallo(
            f"no puedo enumerar los commits del push ({remote_sha[:12]}..{local_sha[:12]}): "
            f"{r.stderr.strip()}\n   Corre `git fetch` del remoto y reintenta."
        )
    return [c for c in r.stdout.splitlines() if c]


def tag_llega_al_remoto(tag: str, tags_del_push: set, remoto: "str | None") -> bool:
    if tag in tags_del_push:
        return True
    if not remoto:
        return False
    r = git_rc("ls-remote", "--tags", remoto, f"refs/tags/{tag}")
    return r.returncode == 0 and bool(r.stdout.strip())


def candado_activo(raiz: Path) -> bool:
    if git("tag", "-l", f"{PREFIJO_TAG}*").strip():
        return True
    receipts = raiz / RECEIPTS_DIR
    return receipts.is_dir() and any(receipts.glob("*.json"))


def verificar_push(remoto: "str | None" = None, url: "str | None" = None) -> None:
    raiz = raiz_repo()
    updates = []
    if not sys.stdin.isatty():
        for linea in sys.stdin.read().splitlines():
            partes = linea.split()
            if len(partes) == 4:
                updates.append(partes)

    if not candado_activo(raiz):
        ok("aún no hay sellos en este repo — el candado se activa con el primer sello. Push permitido.")
        return

    if not updates:
        # Invocación manual (sin refs): pre-vuelo sobre HEAD.
        exige_tree_limpio()
        head = git("rev-parse", "HEAD").strip()
        tag = tag_valido_en(head)
        if not tag:
            fallo(
                f"HEAD ({head[:12]}) no está sellado: ningún tag {PREFIJO_TAG}* válido apunta a este commit.\n"
                "   Valida el lote con el humano y séllalo (sellar-lote) antes de pushear código."
            )
        ok(f"HEAD {head[:12]} está sellado ({tag}). Pre-vuelo OK — el hook validará las refs del push real.")
        return

    tags_del_push = set()
    ramas = []
    for _local_ref, local_sha, remote_ref, remote_sha in updates:
        if remote_ref.startswith("refs/tags/" + PREFIJO_TAG):
            tag = remote_ref[len("refs/tags/"):]
            if es_sha_cero(local_sha):
                fallo(f"borrar el tag remoto {tag} está prohibido: los sellos de lote son inmutables.")
            if not es_sha_cero(remote_sha):
                fallo(f"mover/actualizar el tag remoto {tag} está prohibido: los sellos de lote son inmutables.")
            tags_del_push.add(tag)
        else:
            ramas.append((local_sha, remote_ref, remote_sha))

    hay_codigo = False
    detalle = []
    for local_sha, remote_ref, remote_sha in ramas:
        if es_sha_cero(local_sha):  # borrado de rama: no entrega contenido
            continue
        commits = commits_introducidos(local_sha, remote_sha, remoto)
        sellados = {c: tag_valido_en(c) for c in commits}
        sellados = {c: t for c, t in sellados.items() if t}
        tags_usados = set()
        for c in commits:
            archivos = archivos_de_commit(c)
            if solo_docs(archivos):
                continue
            hay_codigo = True
            cobertura = None
            for s, t in sellados.items():
                if c == s or git_rc("merge-base", "--is-ancestor", c, s).returncode == 0:
                    cobertura = t
                    break
            if not cobertura:
                fallo(
                    f"el push a {remote_ref} entrega CÓDIGO sin sellar (commit {c[:12]}):\n"
                    f"   no es un commit sellado ni ancestro de un lote sellado dentro del push.\n"
                    "   Lo validado debe ser exactamente lo entregado: valida el lote y séllalo (sellar-lote)."
                )
            tags_usados.add(cobertura)
        for t in sorted(tags_usados):
            if not tag_llega_al_remoto(t, tags_del_push, remoto):
                destino = remoto or "el remoto"
                fallo(
                    f"el código de {remote_ref} está sellado por {t}, pero ese tag NO viaja en este push "
                    f"ni existe en {destino}.\n"
                    f"   La evidencia debe llegar con el código: git push {destino} <rama> refs/tags/{t}"
                )
        etiqueta = "solo docs" if not any(
            not solo_docs(archivos_de_commit(c)) for c in commits
        ) else f"sellado ({', '.join(sorted(tags_usados))})"
        detalle.append(f"{remote_ref}: {etiqueta}")
    if hay_codigo:
        exige_tree_limpio()
    ok("push verificado — " + ("; ".join(detalle) if detalle else "sin contenido nuevo") + ".")


def contenido_hook() -> str:
    return (
        "#!/bin/sh\n"
        f"# {MARCADOR_HOOK}: bloquea el push de código no sellado. Instalado por sello.py v{VERSION}.\n"
        "# No editar: la instalación verifica el contenido exacto. Para encadenar tus\n"
        "# propios checks, crea tu hook aparte y llama a este script desde ahí.\n"
        'cd "$(git rev-parse --show-toplevel)" || exit 1\n'
        'exec python3 .claude/scripts/sello.py verificar-push --remoto "$1" --url "$2"\n'
    )


def ruta_hook_efectiva(raiz: Path) -> Path:
    # core.hooksPath manda sobre <git-dir>/hooks; --git-path resuelve
    # worktrees (los hooks viven en el directorio común).
    cfg = git_rc("config", "--get", "core.hooksPath").stdout.strip()
    if cfg:
        base = Path(cfg)
        if not base.is_absolute():
            base = raiz / base
        return base / "pre-push"
    ruta = Path(git("rev-parse", "--git-path", "hooks/pre-push").strip())
    if not ruta.is_absolute():
        ruta = (Path.cwd() / ruta).resolve()
    return ruta


def instalar_hook() -> None:
    raiz = raiz_repo()
    hook = ruta_hook_efectiva(raiz)
    esperado = contenido_hook()
    if hook.exists():
        actual = hook.read_text(encoding="utf-8")
        if actual == esperado:
            ok(f"hook pre-push ya instalado y exacto: {hook}")
            return
        if MARCADOR_HOOK not in actual:
            fallo(f"ya existe un hook pre-push ajeno en {hook}. Intégralo a mano — no lo piso.")
        fallo(
            f"el hook en {hook} tiene el marcador stark pero fue modificado. No lo piso:\n"
            "   bórralo tú y reinstala, o intégralo a mano."
        )
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(esperado, encoding="utf-8")
    hook.chmod(0o755)
    # Self-test: la ruta escrita debe ser la que git va a ejecutar.
    if not hook.is_file() or not os.access(hook, os.X_OK):
        fallo(f"no pude dejar ejecutable el hook en {hook}")
    ok(f"hook pre-push instalado en {hook} (respeta core.hooksPath y worktrees): git bloqueará el push de código no sellado.")


def main() -> None:
    p = argparse.ArgumentParser(prog="sello.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("sellar-doc", help="sella un artefacto aprobado (línea visible + receipt sha256)")
    s1.add_argument("artefacto")
    s1.add_argument("--por", required=True)
    s1.add_argument("--re-sellar", action="store_true", dest="re_sellar",
                    help="pisa un receipt existente (solo tras nueva aprobación humana)")

    s2 = sub.add_parser("verificar-doc", help="verifica que el artefacto coincide con su receipt")
    s2.add_argument("artefacto")

    s3 = sub.add_parser("sellar-lote", help="sella el commit validado con un annotated tag")
    s3.add_argument("id")
    s3.add_argument("--por", required=True)
    s3.add_argument("--invariantes", action="store_true")

    s4 = sub.add_parser("verificar-push", help="comprobación determinista pre-push (por commit y por ref)")
    s4.add_argument("--remoto", default=None)
    s4.add_argument("--url", default=None)

    sub.add_parser("instalar-hook", help="cablea verificar-push al hook pre-push efectivo de git")

    args = p.parse_args()
    if args.cmd == "sellar-doc":
        sellar_doc(args.artefacto, args.por, args.re_sellar)
    elif args.cmd == "verificar-doc":
        verificar_doc(args.artefacto)
    elif args.cmd == "sellar-lote":
        sellar_lote(args.id, args.por, args.invariantes)
    elif args.cmd == "verificar-push":
        verificar_push(args.remoto, args.url)
    elif args.cmd == "instalar-hook":
        instalar_hook()


if __name__ == "__main__":
    main()
