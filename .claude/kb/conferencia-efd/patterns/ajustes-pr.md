# Ajustes do Parana — E111/E112/E113

> **Purpose**: Validar ajustes de apuracao estaduais do Parana: vigencia, E112 e E113 obrigatorios
> **MCP Validated**: 2026-05-18

## When to Use

- Ao implementar ou debugar as regras REGRA-PR-001, REGRA-PR-002, REGRA-PR-003
- Ao importar nova tabela de codigos de ajuste PR com vigencia
- Ao entender por que um ajuste E111 gerou finding de invalidez

## Implementation

```python
"""
Regras de ajuste do Parana:
  REGRA-PR-001: cod_aj_apur do E111 nao existe na tabela pr_adjustments
                ou esta fora de vigencia para a competencia
  REGRA-PR-002: cod_aj_apur exige E112 mas E112 esta ausente
  REGRA-PR-003: cod_aj_apur exige E113 mas o documento referenciado
                nao existe no C100 do arquivo

Tabela pr_adjustments:
  cod_aj:         str        # ex: "PR020001"
  descricao:      str
  vigencia_ini:   date
  vigencia_fim:   date | None
  exige_e112:     bool
  exige_e113:     bool
  exige_processo: bool       # processo administrativo em E112
"""
from sqlalchemy.orm import Session
import uuid
from datetime import date


def conf_pr_adjustments(
    db: Session,
    efd_file_id: uuid.UUID,
    findings: list,
) -> None:
    from app.models.efd_e110 import EfdE111IcmsAdjustment, EfdE112AdjInfo, EfdE113AdjustmentDoc
    from app.models.pr_adjustment import PrAdjustment
    from app.models.efd_c100 import EfdC100Doc
    from app.models.efd_file import EfdFile
    from app.models.fiscal_period import FiscalPeriod

    # Carregar competencia do arquivo
    efd_file = db.query(EfdFile).filter(EfdFile.id == efd_file_id).first()
    if not efd_file:
        return
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == efd_file.fiscal_period_id).first()
    competencia: date = period.reference_date if period else date.today()

    # Carregar todos os E111 do arquivo
    e111_rows = (
        db.query(EfdE111IcmsAdjustment)
        .filter(EfdE111IcmsAdjustment.efd_file_id == efd_file_id)
        .all()
    )
    if not e111_rows:
        return

    # Indexar regras PR por codigo
    todas_pr = db.query(PrAdjustment).all()
    pr_por_cod: dict[str, list[PrAdjustment]] = {}
    for pr in todas_pr:
        pr_por_cod.setdefault(pr.cod_aj, []).append(pr)

    # Carregar documentos C100 presentes no arquivo
    c100_docs = db.query(EfdC100Doc).filter(EfdC100Doc.efd_file_id == efd_file_id).all()
    docs_presentes: set[str] = {
        f"{d.cod_mod}_{d.ser}_{d.num_doc}" for d in c100_docs
    }

    for e111 in e111_rows:
        cod = (e111.cod_aj_apur or "").strip()
        if not cod.startswith("PR"):
            continue  # ajuste nao e do Parana

        # REGRA-PR-001: codigo inexistente ou fora de vigencia
        regras_vigentes = [
            r for r in pr_por_cod.get(cod, [])
            if r.vigencia_ini <= competencia and
               (r.vigencia_fim is None or r.vigencia_fim >= competencia)
        ]
        if not regras_vigentes:
            findings.append(_finding(
                rule_code="REGRA-PR-001",
                severity="alerta",
                finding_type="ajuste_invalido",
                title=f"Codigo de ajuste PR '{cod}' nao vigente para a competencia",
                register_code="E111",
                field_name="cod_aj_apur",
            ))
            continue  # nao validar E112/E113 sem regra valida

        regra = regras_vigentes[0]

        # Carregar E112 filhos deste E111
        e112_rows = (
            db.query(EfdE112AdjInfo)
            .filter(
                EfdE112AdjInfo.efd_file_id == efd_file_id,
                EfdE112AdjInfo.parent_e111_id == e111.id,
            )
            .all()
        )

        # REGRA-PR-002: E112 obrigatorio mas ausente
        if regra.exige_e112 and not e112_rows:
            findings.append(_finding(
                rule_code="REGRA-PR-002",
                severity="alerta",
                finding_type="ausencia_registro",
                title=f"Codigo PR '{cod}' exige E112 mas E112 esta ausente",
                register_code="E112",
                field_name="cod_aj_apur",
            ))

        # REGRA-PR-003: E113 com documento inexistente
        if regra.exige_e113:
            e113_rows = (
                db.query(EfdE113AdjustmentDoc)
                .filter(
                    EfdE113AdjustmentDoc.efd_file_id == efd_file_id,
                    EfdE113AdjustmentDoc.parent_e111_id == e111.id,
                )
                .all()
            )
            for e113 in e113_rows:
                chave = f"{e113.cod_mod}_{e113.ser}_{e113.num_doc}"
                if chave not in docs_presentes:
                    findings.append(_finding(
                        rule_code="REGRA-PR-003",
                        severity="alerta",
                        finding_type="ajuste_invalido",
                        title=(
                            f"E113 referencia doc {e113.num_doc} "
                            f"(mod {e113.cod_mod}) nao encontrado no C100"
                        ),
                        register_code="E113",
                        field_name="num_doc",
                    ))


def _finding(rule_code, severity, finding_type, title, **kwargs):
    from app.services.conference.engine import Finding
    return Finding(
        rule_code=rule_code,
        severity=severity,
        finding_type=finding_type,
        title=title,
        **kwargs,
    )
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `cod_aj_apur` prefixo | `PR` | So valida ajustes com codigo comecando em PR |
| `exige_e112` | Depende do codigo | Booleano na tabela pr_adjustments |
| `exige_e113` | Depende do codigo | Booleano na tabela pr_adjustments |
| `vigencia_ini/fim` | Obrigatorio | Controle de vigencia da tabela estadual |

## Example Usage

```python
# Importar novos codigos PR via CSV:
# colunas: cod_aj, descricao, vigencia_ini, vigencia_fim, exige_e112, exige_e113, exige_processo

# Na conferencia (engine.py etapa 4):
conf_pr_adjustments(db, efd_file_id, findings)
```

## See Also

- [pipeline-validacao.md](pipeline-validacao.md)
- [../concepts/apuracao-icms-ipi.md](../concepts/apuracao-icms-ipi.md)
- [../concepts/registros-chave.md](../concepts/registros-chave.md)
