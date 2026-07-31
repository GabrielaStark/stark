#!/usr/bin/env python3
"""sello.py — autoridad ejecutable de los sellos RDD de stark.

Los sellos visibles en Markdown son cortesía de lectura; la autoridad es esto:
- Sello de documento: receipt JSON con sha256 del artefacto aprobado
  (docs/.stark/receipts/). Si cambia una coma del documento, el receipt
  deja de coincidir y la fase siguiente se bloquea.
- Sello de lote: annotated tag `stark-lote-<id>` sobre el commit validado.
  No modifica el árbol (sin Ouroboros) y exige working tree limpio.
- verificar-push: comprobación determinista pre-push (tree limpio, sin
  untracked, HEAD sellado, Tests: PASS registrado). instalar-hook la
  cablea a git para que el push se bloquee solo.

Uso:
  python3 .claude/scripts/sello.py sellar-doc <artefacto.md> --por "Nombre"
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


def sellar_doc(artefacto: str, por: str) -> None:
    por = valida_nombre(por)
    ruta = Path(artefacto)
    if not ruta.is_file():
        fallo(f"no existe el artefacto {artefacto}")
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


def verificar_push() -> None:
    exige_tree_limpio()
    head = git("rev-parse", "HEAD")
    tags_en_head = [t for t in git("tag", "--points-at", "HEAD").splitlines() if t.startswith(PREFIJO_TAG)]
    if not tags_en_head:
        fallo(
            f"HEAD ({head[:12]}) no está sellado: ningún tag {PREFIJO_TAG}* apunta a este commit.\n"
            "   Valida el lote con el humano y séllalo (sellar-lote) antes de pushear."
        )
    tag = tags_en_head[0]
    contenido = git("tag", "-l", "--format=%(contents)", tag)
    if "Tests: PASS" not in contenido:
        fallo(f"el tag {tag} no registra 'Tests: PASS'.")
    m = re.search(r"Aprobado por: (.+)", contenido)
    if not m or "[" in m.group(1) or "YYYY" in m.group(1):
        fallo(f"el tag {tag} no registra un aprobador válido.")
    ok(f"HEAD {head[:12]} está sellado ({tag}, {m.group(1).strip()}). Push permitido.")


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
        sellar_doc(args.artefacto, args.por)
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
