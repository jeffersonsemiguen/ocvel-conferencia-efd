from __future__ import annotations

import io
import zipfile


def extract_xmls_from_zip(zip_bytes: bytes) -> list[tuple[str, bytes]]:
    """Returns [(filename, xml_bytes), ...] for every .xml inside the ZIP (non-recursive)."""
    out: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".xml") and not name.endswith("/"):
                out.append((name, zf.read(name)))
    return out
