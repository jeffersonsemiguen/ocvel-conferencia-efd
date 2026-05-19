from __future__ import annotations
from app.services.efd_merger.merger import EfdRecord


def recalculate_bloco9(records: list[EfdRecord], logs: list[str]) -> list[EfdRecord]:
    base = [r for r in records if not (r.code.startswith("9") or r.code in ("9900", "9990", "9999", "9001"))]

    contagem: dict[str, int] = {}
    for r in base:
        contagem[r.code] = contagem.get(r.code, 0) + 1

    contagem["9001"] = 1
    todos_codes = set(contagem.keys()) | {"9900", "9990", "9999"}
    qtd_9900 = len(todos_codes)
    contagem["9900"] = qtd_9900
    contagem["9990"] = 1
    contagem["9999"] = 1

    r9900_list = [
        EfdRecord("9900", ["9900", code, str(contagem[code])], f"|9900|{code}|{contagem[code]}|")
        for code in sorted(contagem.keys())
    ]

    base.append(EfdRecord("9001", ["9001", "0"], "|9001|0|"))
    base.extend(r9900_list)

    cnt9 = 1 + len(r9900_list) + 1
    base.append(EfdRecord("9990", ["9990", str(cnt9 + 1)], f"|9990|{cnt9 + 1}|"))

    total = len(base) + 1
    base.append(EfdRecord("9999", ["9999", str(total)], f"|9999|{total}|"))

    logs.append(f"Bloco 9 recalculado. Total de linhas: {total}")
    return base
