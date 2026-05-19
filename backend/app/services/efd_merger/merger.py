from __future__ import annotations
from dataclasses import dataclass, field

BLOCOS = ["B", "C", "D", "E", "G", "H", "K", "1"]

DEFAULT_CONFIG: dict[str, str] = {
    "B": "contabil", "C": "contabil", "D": "contabil", "E": "contabil",
    "G": "contabil", "H": "empresa",  "K": "empresa",  "1": "contabil",
}


@dataclass
class EfdRecord:
    code: str
    campos: list[str]
    linha: str


@dataclass
class MergeResult:
    ok: bool
    output: str
    total_lines: int
    conflicts: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)


def parse_lines(text: str) -> list[EfdRecord]:
    records = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        parts = line.split("|")
        code = parts[1] if len(parts) > 1 else ""
        if not code:
            continue
        campos = parts[1:-1]
        records.append(EfdRecord(code=code, campos=campos, linha=line))
    return records


def get_block(code: str) -> str | None:
    if not code:
        return None
    if code.startswith("9") or code in ("9900", "9990", "9999"):
        return "9"
    if code == "0990" or code.startswith("0"):
        return "0"
    return code[0].upper()


def build_index(records: list[EfdRecord]) -> dict:
    by_block: dict[str, list[EfdRecord]] = {}
    by_code: dict[str, list[EfdRecord]] = {}
    itens: dict[str, EfdRecord] = {}
    unidades: dict[str, EfdRecord] = {}

    for r in records:
        b = get_block(r.code)
        if b:
            by_block.setdefault(b, []).append(r)
        by_code.setdefault(r.code, []).append(r)
        if r.code == "0200" and len(r.campos) > 1:
            itens[r.campos[1]] = r
        if r.code == "0190" and len(r.campos) > 1:
            unidades[r.campos[1]] = r

    return {"by_block": by_block, "by_code": by_code,
            "itens": itens, "unidades": unidades}


def _extract_header(idx: dict) -> dict | None:
    rows = idx["by_code"].get("0000", [])
    if not rows:
        return None
    p = rows[0].campos
    return {
        "cnpj":   p[7]  if len(p) > 7  else "",
        "dt_ini": p[4]  if len(p) > 4  else "",
        "dt_fin": p[5]  if len(p) > 5  else "",
        "nome":   p[6]  if len(p) > 6  else "",
    }


def merge(
    text_empresa: str,
    text_contabil: str,
    block_config: dict[str, str] | None = None,
) -> MergeResult:
    from app.services.efd_merger.dependency_resolver import resolve_dependencies
    from app.services.efd_merger.bloco9_calculator import recalculate_bloco9

    config = {**DEFAULT_CONFIG, **(block_config or {})}
    logs: list[str] = []
    conflicts: list[str] = []

    regs_e = parse_lines(text_empresa)
    regs_c = parse_lines(text_contabil)
    idx_e = build_index(regs_e)
    idx_c = build_index(regs_c)

    h_e = _extract_header(idx_e)
    h_c = _extract_header(idx_c)
    if h_e and h_c:
        if h_e["cnpj"] != h_c["cnpj"]:
            return MergeResult(ok=False, output="", total_lines=0,
                conflicts=[f"CNPJs diferentes: {h_e['cnpj']} ≠ {h_c['cnpj']}"])
        if h_e["dt_ini"] != h_c["dt_ini"] or h_e["dt_fin"] != h_c["dt_fin"]:
            return MergeResult(ok=False, output="", total_lines=0,
                conflicts=["Períodos diferentes entre os arquivos"])

    bloco0 = resolve_dependencies(regs_e, regs_c, idx_e, idx_c, config, logs, conflicts)

    if any("não encontrado" in c and "Item" in c for c in conflicts):
        return MergeResult(ok=False, output="", total_lines=0, conflicts=conflicts, log=logs)

    cnt0 = len(bloco0) + 1
    bloco0.append(EfdRecord("0990", ["0990", str(cnt0)], f"|0990|{cnt0}|"))

    final: list[EfdRecord] = list(bloco0)

    for bloco in BLOCOS:
        src_idx = idx_e if config.get(bloco) == "empresa" else idx_c
        regs = [r for r in (src_idx["by_block"].get(bloco) or [])
                if r.code not in (f"{bloco}001", f"{bloco}990")]
        ind_mov = "0" if regs else "1"
        final.append(EfdRecord(f"{bloco}001", [f"{bloco}001", ind_mov], f"|{bloco}001|{ind_mov}|"))
        final.extend(regs)
        total_bloco = len(regs) + 2
        final.append(EfdRecord(f"{bloco}990", [f"{bloco}990", str(total_bloco)], f"|{bloco}990|{total_bloco}|"))
        logs.append(f"Bloco {bloco}: {len(regs)} reg → {config.get(bloco, 'contabil').upper()}")

    final = recalculate_bloco9(final, logs)

    output = "\r\n".join(r.linha for r in final) + "\r\n"
    return MergeResult(ok=True, output=output, total_lines=len(final),
                       conflicts=conflicts, log=logs)
