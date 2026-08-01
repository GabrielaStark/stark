#!/usr/bin/env python3
"""sello.py — autoridad ejecutable de los sellos RDD de stark.

Los sellos visibles en Markdown son cortesía de lectura; la autoridad es esto:
- Sello de documento: receipt JSON con sha256 del artefacto aprobado
  (docs/.stark/receipts/). Si cambia una coma del documento, el receipt
  deja de coincidir y la fase siguiente se bloquea.
- Sello de lote: annotated tag `stark-lote-<id>` sobre el commit validado.
  No modifica el árbol (sin Ouroboros) y exige working tree limpio.
- verificar-push: comprobación determinista pre-push. En el hook valida las
  REFS que realmente se empujan (no HEAD): cada commit empujado con cambios
  fuera de docs/ debe tener su tag de lote; los pushes que solo tocan docs/
  (specs, receipts, prototipo) pasan — no son código. instalar-hook lo
  cablea a git para que el push se bloquee solo.

Límites (dichos de frente): el sello REGISTRA la identidad del aprobador y
la declaración `Tests: PASS` — no los firma criptográficamente ni ejecuta la
suite; eso lo garantiza el gate humano. El hook es por clon y `--no-verify`
lo salta: es un candado contra el descuido y la deriva, no contra la mala fe.

Uso:
  python3 .claude/scripts/sello.py sellar-doc <artefacto.md> --por "Nombre" [--re-sellar]
  python3 .claude/scripts/sello.py verificar-doc <artefacto.md>
  python3 .claude/scripts/sello.py sellar-lote <id> --por "Nombre" [--invariantes]
  python3 .claude/scripts/sello.py verificar-push
  python3 .claude/scripts/sello.py instalar-hook

Códigos de salida: 0 = OK, 1 = bloqueado/inválido, 2 = error de uso.
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RECEIPTS_DIR = Path("docs/.stark/receipts")
PREFIJO_TAG = "stark-lote-"
FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_CERO = "0" * 40


def fallo(msg: str) -> "None":
    print(f"❌ SELLO: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✅ SELLO: {msg}")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        fallo(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r.stdout.strip()


def valida_nombre(nombre: str) -> str:
    n = (nombre or "").strip()
    if not n or "[" in n or "]" in n or "YYYY" in n or n.lower() == "nombre":
        fallo(f"nombre de aprobador inválido: {nombre!r}. Debe ser una persona real, sin placeholders.")
    return n


def sha256_de(ruta: Path) -> str:
    return "sha256:" + hashlib.sha256(ruta.read_bytes()).hexdigest()


def ruta_receipt(artefacto: Path) -> Path:
    plano = str(artefacto).replace("\\", "/").strip("/").replace("/", "__")
    return RECEIPTS_DIR / f"{plano}.json"


def sellar_doc(artefacto: str, por: str, re_sellar: bool = False) -> None:
    por = valida_nombre(por)
    ruta = Path(artefacto)
    if not ruta.is_file():
        fallo(f"no existe el artefacto {artefacto}")
    previo = ruta_receipt(ruta)
    if previo.is_file() and not re_sellar:
        try:
            r = json.loads(previo.read_text(encoding="utf-8"))
            quien = f"{r.get('approved_by')} el {r.get('approved_at')}"
        except json.JSONDecodeError:
            quien = "(receipt ilegible)"
        fallo(
            f"{artefacto} ya tiene receipt (aprobado por {quien}). Re-sellar PISA esa aprobación:\n"
            "   hazlo solo tras una NUEVA aprobación humana explícita, con --re-sellar."
        )
    hoy = datetime.date.today().isoformat()
    sello = f"> Aprobado por {por} — {hoy}"

    lineas = ruta.read_text(encoding="utf-8").splitlines()
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
            fallo(f"{artefacto} no tiene título H1 donde estampar el sello")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    receipt = {
        "artifact": str(ruta),
        "artifact_hash": sha256_de(ruta),
        "approved_by": por,
        "approved_at": hoy,
    }
    destino = ruta_receipt(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok(f"{artefacto} sellado por {por} ({hoy}). Receipt: {destino}")


def verificar_doc(artefacto: str) -> None:
    ruta = Path(artefacto)
    if not ruta.is_file():
        fallo(f"no existe el artefacto {artefacto}")
    destino = ruta_receipt(ruta)
    if not destino.is_file():
        fallo(f"{artefacto} no tiene receipt ({destino}). El documento no está aprobado.")
    try:
        receipt = json.loads(destino.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fallo(f"receipt corrupto: {destino}")
    por = receipt.get("approved_by", "")
    fecha = receipt.get("approved_at", "")
    if not por or "[" in por or "YYYY" in por:
        fallo(f"receipt con aprobador placeholder: {por!r}")
    if not FECHA_RE.match(fecha):
        fallo(f"receipt con fecha inválida: {fecha!r}")
    actual = sha256_de(ruta)
    if receipt.get("artifact_hash") != actual:
        fallo(
            f"{artefacto} CAMBIÓ después de aprobarse.\n"
            f"   aprobado: {receipt.get('artifact_hash')}\n"
            f"   actual:   {actual}\n"
            f"   La versión aprobada ya no es la versión presente: re-aprueba antes de avanzar."
        )
    ok(f"{artefacto} coincide con lo aprobado por {por} el {fecha}.")


def exige_tree_limpio() -> None:
    porcelain = git("status", "--porcelain")
    if porcelain:
        fallo(
            "working tree sucio (archivos modificados, staged o untracked):\n"
            + porcelain
            + "\n   Lo validado debe ser exactamente lo commiteado: commitea o descarta antes de sellar/pushear."
        )


def sellar_lote(lote_id: str, por: str, invariantes: bool) -> None:
    por = valida_nombre(por)
    exige_tree_limpio()
    tag = f"{PREFIJO_TAG}{lote_id}"
    existentes = git("tag", "-l", tag)
    if existentes:
        fallo(f"el tag {tag} ya existe. Un lote se sella una sola vez.")
    hoy = datetime.date.today().isoformat()
    msg = "Tests: PASS\n"
    if invariantes:
        msg += "Invariantes: PASS\n"
    msg += f"Aprobado por: {por}\nFecha: {hoy}"
    git("tag", "-a", tag, "-m", msg)
    head = git("rev-parse", "HEAD")
    ok(f"lote {lote_id} sellado: tag {tag} → commit {head} (por {por}, {hoy}).")
    print("   Recuerda pushear el tag junto con la rama: git push origin <rama> --tags")


def tag_valido_en(sha: str) -> "str | None":
    tags = [t for t in git("tag", "--points-at", sha).splitlines() if t.startswith(PREFIJO_TAG)]
    for tag in tags:
        contenido = git("tag", "-l", "--format=%(contents)", tag)
        m = re.search(r"Aprobado por: (.+)", contenido)
        if "Tests: PASS" in contenido and m and "[" not in m.group(1) and "YYYY" not in m.group(1):
            return tag
    return None


def archivos_del_push(local: str, remoto: str) -> list:
    if remoto == SHA_CERO:
        # Ref nueva en el remoto: cuentan los commits que ningún remoto tiene aún.
        commits = [c for c in git("rev-list", local, "--not", "--remotes").splitlines() if c]
        archivos = set()
        for c in commits:
            archivos |= {a for a in git("show", "--format=", "--name-only", c).splitlines() if a}
        return sorted(archivos)
    return [a for a in git("diff", "--name-only", remoto, local).splitlines() if a]


NO_CODIGO = {"CONSTITUTION.md", "README.md", "LICENSE", ".gitignore"}


def solo_docs(archivos: list) -> bool:
    return all(a in NO_CODIGO or a.startswith("docs/") for a in archivos)


def verificar_push() -> None:
    # En el hook pre-push, git entrega por stdin las refs que se empujan:
    # "<local ref> <local sha> <remote ref> <remote sha>" por línea.
    updates = []
    if not sys.stdin.isatty():
        for linea in sys.stdin.read().splitlines():
            partes = linea.split()
            if len(partes) == 4:
                updates.append(partes)

    if not git("tag", "-l", f"{PREFIJO_TAG}*"):
        # Aún no hay lotes sellados: stark no ha validado nada que proteger.
        # El candado se activa con el primer sello de lote.
        ok("aún no hay lotes sellados — el candado se activa con el primer sellar-lote. Push permitido.")
        return

    if not updates:
        # Invocación manual (sin refs): pre-vuelo sobre HEAD.
        exige_tree_limpio()
        head = git("rev-parse", "HEAD")
        tag = tag_valido_en(head)
        if not tag:
            fallo(
                f"HEAD ({head[:12]}) no está sellado: ningún tag {PREFIJO_TAG}* válido apunta a este commit.\n"
                "   Valida el lote con el humano y séllalo (sellar-lote) antes de pushear código."
            )
        ok(f"HEAD {head[:12]} está sellado ({tag}). Push permitido.")
        return

    hay_codigo = False
    detalle = []
    for _local_ref, local_sha, remote_ref, remote_sha in updates:
        if local_sha == SHA_CERO:  # borrado de ref remota: no entrega contenido
            continue
        archivos = archivos_del_push(local_sha, remote_sha)
        if solo_docs(archivos):
            detalle.append(f"{remote_ref}: solo docs/ — pasa sin sello")
            continue
        hay_codigo = True
        tag = tag_valido_en(local_sha)
        if not tag:
            fallo(
                f"el push a {remote_ref} entrega CÓDIGO sin sellar (commit {local_sha[:12]}):\n"
                f"   ningún tag {PREFIJO_TAG}* válido apunta a ese commit exacto.\n"
                "   Lo validado debe ser exactamente lo entregado: valida el lote y séllalo (sellar-lote)."
            )
        detalle.append(f"{remote_ref}: sellado ({tag})")
    if hay_codigo:
        exige_tree_limpio()
    ok("push verificado — " + ("; ".join(detalle) if detalle else "sin contenido nuevo") + ".")


def instalar_hook() -> None:
    git_dir = Path(git("rev-parse", "--git-dir"))
    hook = git_dir / "hooks" / "pre-push"
    contenido = (
        "#!/bin/sh\n"
        "# stark (RDD): bloquea el push de código no sellado. Instalado por sello.py.\n"
        'cd "$(git rev-parse --show-toplevel)" || exit 1\n'
        "exec python3 .claude/scripts/sello.py verificar-push\n"
    )
    if hook.exists() and "stark (RDD)" not in hook.read_text(encoding="utf-8"):
        fallo(f"ya existe un hook pre-push ajeno en {hook}. Intégralo a mano — no lo piso.")
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(contenido, encoding="utf-8")
    hook.chmod(0o755)
    ok(f"hook pre-push instalado en {hook}: git bloqueará el push de código no sellado.")


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

    sub.add_parser("verificar-push", help="comprobación determinista pre-push")
    sub.add_parser("instalar-hook", help="cablea verificar-push al hook pre-push de git")

    args = p.parse_args()
    if args.cmd == "sellar-doc":
        sellar_doc(args.artefacto, args.por, args.re_sellar)
    elif args.cmd == "verificar-doc":
        verificar_doc(args.artefacto)
    elif args.cmd == "sellar-lote":
        sellar_lote(args.id, args.por, args.invariantes)
    elif args.cmd == "verificar-push":
        verificar_push()
    elif args.cmd == "instalar-hook":
        instalar_hook()


if __name__ == "__main__":
    main()
