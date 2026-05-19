---
feature: EFD_MERGER
phase: 2-design
status: ✅ Ready for Build
date: 2026-05-19
author: design-agent
---

# DESIGN: EFD Merger — SPED Empresa + SPED Contábil

---

## Architecture Overview

```
Aba "Arquivo EFD"
  │
  ├── [Enviar EFD]  →  POST /efd-files?role=merged  (fluxo atual, inalterado)
  │
  └── [Mesclar EFDs] → MergerModal
        │
        ├── Upload SPED Empresa  →  POST /efd-files?role=empresa  → empresa_file_id
        ├── Upload SPED Contábil →  POST /efd-files?role=contabil → contabil_file_id
        │       (validação client-side: mesmo CNPJ + período)
        │
        ├── Toggle de blocos (B/C/D/E/G/H/K/1) com padrões pré-definidos
        │
        └── [Gerar Arquivo SPED]
              │
              POST /fiscal-periods/{id}/efd-files/merge
                │
                ├── efd_merger.merger        → lê os dois TXTs, mescla blocos
                ├── dependency_resolver      → importa 0200/0190/0300/0305/0500/0600
                ├── bloco9_calculator        → recalcula 9900/9990/9999
                │
                ├── Grava TXT merged em disco
                ├── Cria EfdFile(role='merged')
                └── run_full_parse()  →  conferência usa merged como EFD ativo
```

---

## Architectural Decisions

### Decision 1: `file_role` como coluna simples, não tabela separada

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Precisamos distinguir SPED Empresa, SPED Contábil e Arquivo SPED (merged) no banco.

**Choice:** Adicionar `file_role VARCHAR(10) DEFAULT 'merged'` no `EfdFile` existente.

**Rationale:** Simples, sem JOIN extra. Arquivos existentes recebem `'merged'` por default sem quebrar nada. A conferência sempre filtra pelo `role='merged'` mais recente.

**Alternatives Rejected:**
1. Tabela `EfdFileMerge` separada — overhead para apenas 1 campo discriminador
2. Enum PostgreSQL — mais rígido, migrations mais difíceis

---

### Decision 2: Upload dos dois arquivos separadamente antes do merge

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** O endpoint de merge precisa dos dois arquivos já persistidos para ler do disco.

**Choice:** Adicionar `role` como query param opcional no endpoint de upload existente (`?role=empresa`). O modal faz 2 uploads sequenciais, depois chama `/merge`.

**Rationale:** Reutiliza 100% do endpoint de upload existente. Os arquivos originais ficam persistidos com seus metadados (CNPJ, período, linhas) para rastreabilidade futura.

**Alternatives Rejected:**
1. Multipart com os dois arquivos em uma só chamada — endpoint mais complexo, sem reuso do upload atual
2. Armazenar os dois TXTs apenas em memória — perde rastreabilidade

---

### Decision 3: Motor de merge em Python puro (port do HTML)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** A ferramenta HTML já tem o motor de merge completo e validado. Precisamos portá-lo para o backend.

**Choice:** Port 1:1 do JavaScript para Python em `services/efd_merger/`. Estrutura de dados idêntica (`EfdRecord` equivale ao objeto `{code, campos, linha}` do JS).

**Rationale:** A lógica já foi testada pelo usuário em produção. Não reinventar.

**Consequences:** O motor assume que o arquivo EFD segue o padrão pipe-delimited válido — sem tratamento de arquivos corrompidos além do que o parser atual já faz.

---

### Decision 4: Conferência sempre usa `role='merged'` mais recente

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** Uma competência pode ter 3 arquivos (empresa + contabil + merged). O motor de conferência precisa saber qual usar.

**Choice:** Ao buscar o EFD ativo da competência, filtrar por `role='merged'` ordenado por `created_at DESC`. O upload direto (fluxo atual) cria arquivos com `role='merged'` — comportamento preservado.

---

## File Manifest

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `backend/alembic/versions/b2c3d4e5f6a1_add_efd_file_role.py` | Create | Migration: coluna `file_role` no `efd_files` |
| 2 | `backend/app/models/efd_file.py` | Modify | Adicionar campo `file_role` |
| 3 | `backend/app/services/efd_merger/__init__.py` | Create | Package init |
| 4 | `backend/app/services/efd_merger/merger.py` | Create | Motor principal de merge (port do HTML) |
| 5 | `backend/app/services/efd_merger/dependency_resolver.py` | Create | Resolve 0200/0190/0300/0305/0500/0600 |
| 6 | `backend/app/services/efd_merger/bloco9_calculator.py` | Create | Recalcula Bloco 9 |
| 7 | `backend/app/routers/efd_files.py` | Modify | +`role` query param no upload; +endpoint `/merge` |
| 8 | `frontend/src/lib/types.ts` | Modify | +`EfdFileRole`, `MergeConfig`, `MergeResult` |
| 9 | `frontend/src/app/competencias/[id]/page.tsx` | Modify | +badge de role na lista; +botão "Mesclar EFDs"; +`MergerModal` inline |

---

## Code Patterns

### 1. Migration (`b2c3d4e5f6a1_add_efd_file_role.py`)

```python
"""add efd file_role

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a1"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "efd_files",
        sa.Column("file_role", sa.String(10), nullable=False, server_default="merged"),
    )
    op.create_index("ix_efd_files_role", "efd_files", ["fiscal_period_id", "file_role"])


def downgrade():
    op.drop_index("ix_efd_files_role", "efd_files")
    op.drop_column("efd_files", "file_role")
```

---

### 2. Modelo (`efd_file.py` — adição)

```python
# Adicionar após efd_end_date:
file_role: Mapped[str] = mapped_column(String(10), default="merged", nullable=False)
# empresa | contabil | merged
```

---

### 3. Motor de merge (`merger.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field

BLOCOS = ["B", "C", "D", "E", "G", "H", "K", "1"]
DEFAULT_CONFIG = {"B":"contabil","C":"contabil","D":"contabil","E":"contabil",
                  "G":"contabil","H":"empresa","K":"empresa","1":"contabil"}


@dataclass
class EfdRecord:
    code: str
    campos: list[str]
    linha: str


@dataclass
class MergeResult:
    ok: bool
    output: str          # TXT merged em latin-1
    total_lines: int
    conflicts: list[str]
    log: list[str]


def parse_lines(text: str) -> list[EfdRecord]:
    records = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        parts = line.split("|")
        # parts[0]='', parts[1]=code, ..., parts[-1]=''
        code = parts[1] if len(parts) > 1 else ""
        if not code:
            continue
        campos = parts[1:-1]  # exclui '' inicial e '' final
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
    itens: dict[str, EfdRecord] = {}      # 0200: COD_ITEM → record
    unidades: dict[str, EfdRecord] = {}   # 0190: UNID → record

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


def merge(
    text_empresa: str,
    text_contabil: str,
    block_config: dict[str, str] | None = None,
) -> MergeResult:
    """
    text_empresa:  conteúdo do SPED Empresa (latin-1 decoded)
    text_contabil: conteúdo do SPED Contábil (latin-1 decoded)
    block_config:  {"K": "empresa", "G": "contabil", ...}
    """
    from app.services.efd_merger.dependency_resolver import resolve_dependencies
    from app.services.efd_merger.bloco9_calculator import recalculate_bloco9

    config = {**DEFAULT_CONFIG, **(block_config or {})}
    logs: list[str] = []
    conflicts: list[str] = []

    regs_e = parse_lines(text_empresa)
    regs_c = parse_lines(text_contabil)
    idx_e = build_index(regs_e)
    idx_c = build_index(regs_c)

    # Validar compatibilidade
    h_e = _extract_header(idx_e)
    h_c = _extract_header(idx_c)
    if h_e and h_c:
        if h_e["cnpj"] != h_c["cnpj"]:
            return MergeResult(ok=False, output="", total_lines=0,
                conflicts=[f"CNPJs diferentes: {h_e['cnpj']} ≠ {h_c['cnpj']}"], log=[])
        if h_e["dt_ini"] != h_c["dt_ini"] or h_e["dt_fin"] != h_c["dt_fin"]:
            return MergeResult(ok=False, output="", total_lines=0,
                conflicts=["Períodos diferentes entre os arquivos"], log=[])

    # Montar Bloco 0 mesclado com dependências
    bloco0 = resolve_dependencies(regs_e, regs_c, idx_e, idx_c, config, logs, conflicts)

    # Contar 0990
    cnt0 = len(bloco0) + 1
    bloco0.append(EfdRecord("0990", ["0990", str(cnt0)], f"|0990|{cnt0}|"))

    final: list[EfdRecord] = list(bloco0)

    # Blocos B a 1
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

    # Bloco 9
    final = recalculate_bloco9(final, logs)

    output = "\r\n".join(r.linha for r in final) + "\r\n"
    return MergeResult(ok=True, output=output, total_lines=len(final),
                       conflicts=conflicts, log=logs)


def _extract_header(idx: dict) -> dict | None:
    rows = idx["by_code"].get("0000", [])
    if not rows:
        return None
    p = rows[0].campos
    return {"cnpj": p[7] if len(p) > 7 else "",
            "dt_ini": p[4] if len(p) > 4 else "",
            "dt_fin": p[5] if len(p) > 5 else ""}
```

---

### 4. Dependency resolver (`dependency_resolver.py`) — estrutura

```python
ORDEM_0_INICIO = ["0000","0001","0005","0015","0100","0150"]
ESPECIAIS_0 = {"0190","0200","0205","0220","0300","0305","0400","0450","0460","0500","0600","0990"}

def resolve_dependencies(regs_e, regs_c, idx_e, idx_c, config, logs, conflicts):
    """
    Monta o Bloco 0 mesclado:
    1. Registros iniciais (0000→0150) do Contábil (base)
    2. 0190: Contábil + unidades novas do Empresa (se K vem da Empresa)
    3. 0200/0205/0220: Contábil + itens novos do Empresa (se K vem da Empresa)
    4. 0300/0305: Contábil + bens novos do Empresa (se G vem do Contábil)
    5. 0400/0450/0460: Contábil
    6. 0500: Contábil + contas novas referenciadas pelo 0300 importado
    7. 0600: Contábil + centros de custo novos
    """
    # (implementação completa portada do HTML durante o /build)
    ...
```

---

### 5. Bloco 9 calculator (`bloco9_calculator.py`)

```python
def recalculate_bloco9(final: list, logs: list) -> list:
    """
    Remove qualquer Bloco 9 existente e recalcula:
    - 9001 (abertura)
    - 9900 (uma linha por código distinto, ordenado)
    - 9990 (total do bloco 9)
    - 9999 (total geral do arquivo)
    """
    # Remove registros do bloco 9
    base = [r for r in final if not r.code.startswith("9")]

    contagem: dict[str, int] = {}
    for r in base:
        contagem[r.code] = contagem.get(r.code, 0) + 1

    # 9001 será adicionado
    contagem["9001"] = 1
    # calcular quantas linhas 9900 haverá: todos os codes distintos + 9900 em si + 9990 + 9999
    todos_codes = set(contagem.keys()) | {"9900", "9990", "9999"}
    qtd_9900 = len(todos_codes)
    contagem["9900"] = qtd_9900
    contagem["9990"] = 1
    contagem["9999"] = 1

    r9900_list = []
    for code in sorted(contagem.keys()):
        cnt = contagem[code]
        r9900_list.append(EfdRecord("9900", ["9900", code, str(cnt)], f"|9900|{code}|{cnt}|"))

    base.append(EfdRecord("9001", ["9001", "0"], "|9001|0|"))
    base.extend(r9900_list)
    cnt9 = 1 + len(r9900_list) + 1  # 9001 + 9900s + 9990
    base.append(EfdRecord("9990", ["9990", str(cnt9 + 1)], f"|9990|{cnt9 + 1}|"))
    total = len(base) + 1  # +1 para o próprio 9999
    base.append(EfdRecord("9999", ["9999", str(total)], f"|9999|{total}|"))

    logs.append(f"Bloco 9 recalculado. Total de linhas: {total}")
    return base
```

---

### 6. Endpoint de merge (`efd_files.py` — adição)

```python
class MergeRequest(BaseModel):
    empresa_file_id: uuid.UUID
    contabil_file_id: uuid.UUID
    block_config: dict[str, str] = {}


@router.post("/fiscal-periods/{period_id}/efd-files/merge", status_code=201)
def merge_efd_files(
    period_id: uuid.UUID,
    body: MergeRequest,
    db: Session = Depends(get_db),
):
    from app.services.efd_merger.merger import merge

    f_e = db.query(EfdFile).filter(EfdFile.id == body.empresa_file_id).first()
    f_c = db.query(EfdFile).filter(EfdFile.id == body.contabil_file_id).first()
    if not f_e or not f_c:
        raise HTTPException(404, "Arquivo não encontrado")

    text_e = open(f_e.stored_path, encoding="latin-1").read()
    text_c = open(f_c.stored_path, encoding="latin-1").read()

    result = merge(text_e, text_c, body.block_config)
    if not result.ok:
        raise HTTPException(422, detail={"conflicts": result.conflicts})

    # Salvar arquivo merged
    merged_id = uuid.uuid4()
    out_dir = os.path.join(settings.upload_dir, str(period_id))
    os.makedirs(out_dir, exist_ok=True)
    filename = f"MERGED_{merged_id}.txt"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "wb") as f:
        f.write(result.output.encode("latin-1"))

    merged_record = EfdFile(
        id=merged_id,
        fiscal_period_id=period_id,
        original_filename=filename,
        stored_path=out_path,
        file_size_bytes=len(result.output.encode("latin-1")),
        file_role="merged",
        parse_status="uploaded",
    )
    db.add(merged_record)
    db.flush()
    run_full_parse(db, merged_record, out_path)
    db.commit()

    return {
        "merged_file_id": str(merged_id),
        "generated_filename": filename,
        "total_lines": result.total_lines,
        "parse_status": merged_record.parse_status,
        "conflicts": result.conflicts,
        "log": result.log,
    }
```

Modificar upload existente para aceitar `role`:
```python
@router.post("/fiscal-periods/{period_id}/efd-files", ...)
def upload_efd_file(
    period_id: uuid.UUID,
    file: UploadFile,
    role: str = "merged",   # ← NOVO query param
    db: Session = Depends(get_db),
):
    ...
    efd_record = EfdFile(..., file_role=role)
```

---

### 7. Tipos TypeScript (`types.ts` — adição)

```typescript
export type EfdFileRole = "empresa" | "contabil" | "merged";

export interface MergeConfig {
  B: EfdFileRole; C: EfdFileRole; D: EfdFileRole; E: EfdFileRole;
  G: EfdFileRole; H: EfdFileRole; K: EfdFileRole; "1": EfdFileRole;
}

export const DEFAULT_MERGE_CONFIG: MergeConfig = {
  B: "contabil", C: "contabil", D: "contabil", E: "contabil",
  G: "contabil", H: "empresa",  K: "empresa",  "1": "contabil",
};

export interface MergeResult {
  merged_file_id: string;
  generated_filename: string;
  total_lines: number;
  parse_status: string;
  conflicts: string[];
  log: string[];
}

// Adicionar ao EfdFile existente:
// file_role: EfdFileRole
```

---

### 8. Frontend — badge de role e botão Mesclar EFDs

No `EfdTab`, adicionar badge ao lado do nome do arquivo:

```typescript
const ROLE_BADGE: Record<string, { label: string; variant: string }> = {
  empresa:  { label: "SPED Empresa",  variant: "outline" },
  contabil: { label: "SPED Contábil", variant: "secondary" },
  merged:   { label: "Ativo",         variant: "default" },
};

// Na linha da tabela de arquivos:
{file.file_role && (
  <Badge variant={ROLE_BADGE[file.file_role]?.variant as any ?? "outline"}>
    {ROLE_BADGE[file.file_role]?.label ?? file.file_role}
  </Badge>
)}
```

Botão "Mesclar EFDs" ao lado de "Enviar EFD":
```typescript
<Button variant="outline" size="sm" onClick={() => setMergerOpen(true)}>
  <MergeIcon className="mr-2 h-4 w-4" />
  Mesclar EFDs
</Button>
```

`MergerModal` — estrutura:
```typescript
// Dialog com 3 seções:
// 1. Upload SPED Empresa + Upload SPED Contábil
//    → client-side: lê 0000 de cada arquivo para extrair CNPJ/período
//    → mostra status de compatibilidade
// 2. Grid de toggles por bloco (Empresa/Contábil)
//    → estado inicial = DEFAULT_MERGE_CONFIG
// 3. Botão "Gerar Arquivo SPED"
//    → POST empresa file (?role=empresa) → empresa_file_id
//    → POST contabil file (?role=contabil) → contabil_file_id
//    → POST /merge com {empresa_file_id, contabil_file_id, block_config}
//    → Atualiza lista de arquivos + fecha modal
```

---

## Testing Strategy

| Test | Tipo | Como verificar |
|------|------|----------------|
| CNPJ incompatível | Manual | Upload dois arquivos de empresas diferentes → erro claro |
| Período incompatível | Manual | Upload dois arquivos de meses diferentes → erro claro |
| Merge K=Empresa | Manual | Bloco K do Empresa no arquivo merged; 0200 importados |
| Merge G=Contábil | Manual | Bloco G do Contábil; 0300/0305/0500/0600 importados |
| Bloco 9 | Manual | Abrir no PVA ou contar linhas: 9999 deve bater com total |
| Upload direto (regressão) | Manual | Upload normal sem modal → role='merged', fluxo idêntico ao atual |
| Re-merge | Manual | Gerar segundo merged → ambos aparecem na lista, novo é "Ativo" |

---

## Checklist de qualidade

```text
[x] Motor de merge portado 1:1 do HTML validado em produção
[x] run_full_parse não modificado — recebe o merged como qualquer EFD
[x] Upload direto preservado (role='merged' por default)
[x] Migration com DEFAULT garante zero breaking change nos arquivos existentes
[x] Encoding latin-1 mantido no arquivo gerado
[x] Bloco 9 recalculado — PVA não rejeita o arquivo
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_EFD_MERGER.md`
