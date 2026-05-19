"""
Resolve dependências do Bloco 0 ao mesclar dois arquivos EFD.

Lógica portada do sped-merger.html (JavaScript → Python):
- Bloco 0 base sempre vem do Contábil (arquivo A)
- Se Bloco K vem do Empresa: importa 0200/0205/0220/0190 ausentes no Contábil
- Se Bloco G vem do Empresa: importa 0300/0305/0500/0600 ausentes no Contábil
- Conflito de COD_ITEM: default = preferir Contábil (política A do HTML)
"""
from __future__ import annotations
from app.services.efd_merger.merger import EfdRecord

ORDEM_0_INICIO = ["0000", "0001", "0005", "0015", "0100", "0150"]


def resolve_dependencies(
    regs_empresa: list[EfdRecord],
    regs_contabil: list[EfdRecord],
    idx_empresa: dict,
    idx_contabil: dict,
    config: dict[str, str],
    logs: list[str],
    conflicts: list[str],
) -> list[EfdRecord]:
    """
    Monta o Bloco 0 mesclado na ordem correta do SPED.
    Retorna a lista sem 0990 (adicionado pelo caller).
    """
    blocos_empresa = {b for b, src in config.items() if src == "empresa"}

    # ── Identificar itens referenciados pelo Bloco K do Empresa ──────────────
    itens_kb: set[str] = set()
    if "K" in blocos_empresa:
        k_regs = [r for r in (idx_empresa["by_block"].get("K") or [])
                  if r.code not in ("K001", "K990", "K100")]
        for r in k_regs:
            cod = r.campos[2] if len(r.campos) > 2 else (r.campos[1] if len(r.campos) > 1 else "")
            if cod:
                itens_kb.add(cod)
        logs.append(f"Bloco K do Empresa: {len(k_regs)} registros, {len(itens_kb)} itens referenciados")

    # ── Identificar bens referenciados pelo Bloco G do Empresa ───────────────
    bens_gb: set[str] = set()
    if "G" in blocos_empresa:
        g_regs = [r for r in (idx_empresa["by_block"].get("G") or [])
                  if r.code not in ("G001", "G990")]
        for r in g_regs:
            if r.code == "G125" and len(r.campos) > 1:
                bens_gb.add(r.campos[1])
        logs.append(f"Bloco G do Empresa: {len(g_regs)} registros, {len(bens_gb)} bens (G125)")

    # ── Mapear filhos 0205/0220 do Empresa por COD_ITEM ──────────────────────
    map_0205_empresa: dict[str, list[EfdRecord]] = {}
    map_0220_empresa: dict[str, list[EfdRecord]] = {}
    cur_item: str | None = None
    for r in regs_empresa:
        if r.code == "0200":
            cur_item = r.campos[1] if len(r.campos) > 1 else None
            if cur_item:
                map_0205_empresa.setdefault(cur_item, [])
                map_0220_empresa.setdefault(cur_item, [])
        elif r.code == "0205" and cur_item:
            map_0205_empresa[cur_item].append(r)
        elif r.code == "0220" and cur_item:
            map_0220_empresa[cur_item].append(r)

    # ── Mapear filhos 0305 do Empresa por COD_BEM ────────────────────────────
    map_0305_empresa: dict[str, list[EfdRecord]] = {}
    cur_bem: str | None = None
    for r in regs_empresa:
        if r.code == "0300":
            cur_bem = r.campos[1] if len(r.campos) > 1 else None
            if cur_bem:
                map_0305_empresa.setdefault(cur_bem, [])
        elif r.code == "0305" and cur_bem:
            map_0305_empresa[cur_bem].append(r)

    # ── Resolver novos 0200 e 0190 (Bloco K do Empresa) ──────────────────────
    novos_0200: list[EfdRecord] = []
    novos_0205: dict[str, list[EfdRecord]] = {}
    novos_0220: dict[str, list[EfdRecord]] = {}
    novos_0190: list[EfdRecord] = []
    unids_ja = {r.campos[1] for r in (idx_contabil["by_code"].get("0190") or []) if len(r.campos) > 1}

    for cod in itens_kb:
        in_contabil = idx_contabil["itens"].get(cod)
        in_empresa = idx_empresa["itens"].get(cod)

        if not in_contabil and not in_empresa:
            conflicts.append(f'Item "{cod}" usado no Bloco K não encontrado em nenhum arquivo.')
            continue

        if not in_contabil and in_empresa:
            novos_0200.append(in_empresa)
            novos_0205[cod] = map_0205_empresa.get(cod, [])
            novos_0220[cod] = map_0220_empresa.get(cod, [])
            logs.append(f"0200 importado do Empresa: {cod}")

            unid = in_empresa.campos[5] if len(in_empresa.campos) > 5 else ""
            if unid and unid not in unids_ja:
                r_190 = idx_empresa["unidades"].get(unid) or idx_contabil["unidades"].get(unid)
                if r_190:
                    novos_0190.append(r_190)
                    unids_ja.add(unid)
                    logs.append(f"0190 importado do Empresa: unidade {unid}")
                else:
                    conflicts.append(f'Unidade "{unid}" do item {cod} não encontrada.')
        else:
            # Item em ambos: preferir Contábil (política default)
            unid = (in_contabil.campos[5] if in_contabil and len(in_contabil.campos) > 5 else "")
            if unid and unid not in unids_ja:
                r_190 = idx_contabil["unidades"].get(unid) or idx_empresa["unidades"].get(unid)
                if r_190:
                    novos_0190.append(r_190)
                    unids_ja.add(unid)
                    logs.append(f"0190 importado (unidade ausente no Contábil): {unid} para item {cod}")

    # ── Resolver novos 0300/0305/0500/0600 (Bloco G do Empresa) ──────────────
    novos_0300: list[EfdRecord] = []
    novos_0305: dict[str, list[EfdRecord]] = {}
    novos_0500: list[EfdRecord] = []
    novos_0600: list[EfdRecord] = []

    idx_0300_contabil = {r.campos[1]: r for r in (idx_contabil["by_code"].get("0300") or []) if len(r.campos) > 1}
    idx_0500_contabil = {r.campos[5]: r for r in (idx_contabil["by_code"].get("0500") or []) if len(r.campos) > 5}
    idx_0600_contabil = {r.campos[2]: r for r in (idx_contabil["by_code"].get("0600") or []) if len(r.campos) > 2}
    idx_0500_empresa = {r.campos[5]: r for r in (idx_empresa["by_code"].get("0500") or []) if len(r.campos) > 5}
    idx_0600_empresa = {r.campos[2]: r for r in (idx_empresa["by_code"].get("0600") or []) if len(r.campos) > 2}

    cods_bem_ja = set(idx_0300_contabil.keys())
    cods_cta_ja = set(idx_0500_contabil.keys())
    cods_ccus_ja = set(idx_0600_contabil.keys())

    for bem in bens_gb:
        if bem not in cods_bem_ja:
            r_0300 = idx_empresa["by_code"].get("0300", [])
            r_0300 = next((r for r in r_0300 if len(r.campos) > 1 and r.campos[1] == bem), None)
            if not r_0300:
                conflicts.append(f'Bem "{bem}" do Bloco G não encontrado no 0300 do Empresa.')
                continue
            novos_0300.append(r_0300)
            cods_bem_ja.add(bem)
            novos_0305[bem] = map_0305_empresa.get(bem, [])
            logs.append(f"0300 importado do Empresa: bem {bem}")

            cod_cta = r_0300.campos[5] if len(r_0300.campos) > 5 else ""
            if cod_cta and cod_cta not in cods_cta_ja:
                r_0500 = idx_0500_empresa.get(cod_cta) or idx_0500_contabil.get(cod_cta)
                if r_0500:
                    novos_0500.append(r_0500)
                    cods_cta_ja.add(cod_cta)
                    logs.append(f"0500 importado: conta {cod_cta} para bem {bem}")
                else:
                    conflicts.append(f'Conta contábil "{cod_cta}" do bem {bem} não encontrada no 0500.')

            for cod_ccus, r_ccus in idx_0600_empresa.items():
                if cod_ccus not in cods_ccus_ja:
                    novos_0600.append(r_ccus)
                    cods_ccus_ja.add(cod_ccus)
                    logs.append(f"0600 importado do Empresa: centro de custo {cod_ccus}")

    # ── Montar Bloco 0 na ordem SPED ─────────────────────────────────────────
    bloco0: list[EfdRecord] = []

    # 1. Registros de abertura (0000 → 0150) do Contábil
    for code in ORDEM_0_INICIO:
        bloco0.extend(idx_contabil["by_code"].get(code) or [])

    # 2. 0190: Contábil + novos do Empresa
    unids_no_final: set[str] = set()
    for r in (idx_contabil["by_code"].get("0190") or []):
        bloco0.append(r)
        if len(r.campos) > 1:
            unids_no_final.add(r.campos[1])
    for r in novos_0190:
        unid = r.campos[1] if len(r.campos) > 1 else ""
        if unid not in unids_no_final:
            bloco0.append(r)
            unids_no_final.add(unid)

    # 3. 0200/0205/0220: Contábil em ordem original + novos do Empresa
    cods_add_200: set[str] = set()
    regs_0_contabil_filtrados = [r for r in regs_contabil
                                  if get_block_local(r.code) == "0"
                                  and r.code not in ORDEM_0_INICIO
                                  and r.code not in ("0190", "0990")]

    cur_0200_cod: str | None = None
    for r in regs_0_contabil_filtrados:
        if r.code == "0200":
            cur_0200_cod = r.campos[1] if len(r.campos) > 1 else None
            if cur_0200_cod:
                bloco0.append(r)
                cods_add_200.add(cur_0200_cod)
        elif r.code in ("0205", "0220") and cur_0200_cod and cur_0200_cod in cods_add_200:
            bloco0.append(r)

    for r in novos_0200:
        cod = r.campos[1] if len(r.campos) > 1 else ""
        if cod and cod not in cods_add_200:
            bloco0.append(r)
            cods_add_200.add(cod)
            bloco0.extend(novos_0205.get(cod, []))
            bloco0.extend(novos_0220.get(cod, []))

    # 4. 0300/0305: Contábil em ordem original + novos do Empresa
    cods_add_300: set[str] = set()
    cur_bem_c: str | None = None
    for r in regs_0_contabil_filtrados:
        if r.code == "0300":
            cur_bem_c = r.campos[1] if len(r.campos) > 1 else None
            if cur_bem_c:
                bloco0.append(r)
                cods_add_300.add(cur_bem_c)
        elif r.code == "0305" and cur_bem_c and cur_bem_c in cods_add_300:
            bloco0.append(r)

    for r in novos_0300:
        cod = r.campos[1] if len(r.campos) > 1 else ""
        if cod and cod not in cods_add_300:
            bloco0.append(r)
            cods_add_300.add(cod)
            bloco0.extend(novos_0305.get(cod, []))

    # 5. 0400/0450/0460 do Contábil
    for code in ("0400", "0450", "0460"):
        bloco0.extend(idx_contabil["by_code"].get(code) or [])

    # 6. 0500: Contábil + novos do Empresa
    cods_add_500: set[str] = set()
    for r in (idx_contabil["by_code"].get("0500") or []):
        bloco0.append(r)
        if len(r.campos) > 5:
            cods_add_500.add(r.campos[5])
    for r in novos_0500:
        cod = r.campos[5] if len(r.campos) > 5 else ""
        if cod and cod not in cods_add_500:
            bloco0.append(r)
            cods_add_500.add(cod)

    # 7. 0600: Contábil + novos do Empresa
    cods_add_600: set[str] = set()
    for r in (idx_contabil["by_code"].get("0600") or []):
        bloco0.append(r)
        if len(r.campos) > 2:
            cods_add_600.add(r.campos[2])
    for r in novos_0600:
        cod = r.campos[2] if len(r.campos) > 2 else ""
        if cod and cod not in cods_add_600:
            bloco0.append(r)
            cods_add_600.add(cod)

    # 8. Outros registros do Contábil não tratados acima
    especiais_tratados = {
        *ORDEM_0_INICIO, "0190", "0200", "0205", "0220",
        "0300", "0305", "0400", "0450", "0460", "0500", "0600", "0990",
    }
    for r in regs_0_contabil_filtrados:
        if r.code not in especiais_tratados:
            bloco0.append(r)

    return bloco0


def get_block_local(code: str) -> str | None:
    if not code:
        return None
    if code.startswith("9") or code in ("9900", "9990", "9999"):
        return "9"
    if code == "0990" or code.startswith("0"):
        return "0"
    return code[0].upper()
