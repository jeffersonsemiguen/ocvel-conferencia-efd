"""
Parser básico para arquivos TXT da EFD ICMS/IPI.
Sprint 1: extrai apenas o registro 0000 (header do arquivo).
"""
from dataclasses import dataclass


@dataclass
class EfdHeader:
    version: str | None = None
    purpose: str | None = None  # 0=original, 1=substitution
    start_date: str | None = None
    end_date: str | None = None
    company_name: str | None = None
    cnpj: str | None = None
    cpf: str | None = None
    state_registration: str | None = None
    state: str | None = None
    municipality_code: str | None = None
    ie_st: str | None = None
    im: str | None = None
    suffix_cnpj: str | None = None
    profile: str | None = None
    activity_type: str | None = None


@dataclass
class EfdParseResult:
    header: EfdHeader | None
    total_lines: int
    error: str | None = None


def parse_efd_txt(file_path: str) -> EfdParseResult:
    header = None
    total_lines = 0
    error = None

    try:
        with open(file_path, encoding="latin-1") as f:
            for line in f:
                total_lines += 1
                line = line.strip()
                if not line:
                    continue

                fields = line.split("|")
                # Fields: |RECORD|field1|field2|...|
                if len(fields) < 2:
                    continue

                record_type = fields[1] if len(fields) > 1 else ""

                if record_type == "0000":
                    header = _parse_0000(fields)
    except Exception as exc:
        error = str(exc)

    return EfdParseResult(header=header, total_lines=total_lines, error=error)


def _parse_0000(fields: list[str]) -> EfdHeader:
    def get(i: int) -> str | None:
        return fields[i].strip() if i < len(fields) and fields[i].strip() else None

    return EfdHeader(
        version=get(2),
        purpose=get(3),
        start_date=get(4),
        end_date=get(5),
        company_name=get(6),
        cnpj=get(7),
        cpf=get(8),
        state_registration=get(9),
        state=get(10),
        municipality_code=get(11),
        ie_st=get(12),
        im=get(13),
        suffix_cnpj=get(14),
        profile=get(15),
        activity_type=get(16),
    )
