---
feature: CORRECOES_TXT
phase: 2-design
status: ✅ Ready for Build
date: 2026-05-19
author: design-agent
---

# DESIGN: TXT Corrigido Completo

> Página dedicada `/competencias/[id]/correcoes` com endpoint de prévia + geração de TXT unificando correções do motor EFD e do cross-check NF-e.

---

## Architecture Overview

```
Usuário
  │
  ▼
/competencias/[id]/correcoes  (Next.js page — "use client")
  │
  ├── GET /api/v1/fiscal-periods/{id}/corrections/preview   [NOVO]
  │       └── agrupa CorrectionSuggestion(status='approved') por (register, rule, field, source, orig, sugg)
  │
  ├── POST /api/v1/efd-files/{efd_file_id}/corrected-files/generate  [EXISTENTE]
  │       └── corrected_file_generator.py  →  CorrectedFile + CorrectionLog
  │
  └── GET /api/v1/efd-files/{efd_file_id}/corrected-files  [EXISTENTE]
          └── histórico de arquivos gerados

Link de acesso:  /competencias/[id]/page.tsx  →  href="/competencias/[id]/correcoes"
```

---

## Architectural Decisions

### Decision 1: Endpoint de prévia no router `fiscal_periods`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** O endpoint de prévia é scoped ao `fiscal_period_id`. Poderia ser um router separado ou ir no `correction.py`.

**Choice:** Adicionar em `fiscal_periods.py` como `GET /{period_id}/corrections/preview`.

**Rationale:** O router de fiscal_periods já tem o `period_id` como parâmetro de path. Criar um router novo para apenas 1 endpoint é overhead. O `correction.py` está scoped a `efd_file_id` — misturar context quebraria coesão.

**Alternatives Rejected:**
1. Novo router `corrections_preview.py` — overhead para 1 endpoint
2. Adicionar em `correction.py` — scoped errado (efd_file vs period)

---

### Decision 2: Buscar `efd_file_id` via `fiscal_period_id` no frontend

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** O endpoint de geração existente requer `efd_file_id`, mas a página de correções recebe `period_id` via URL.

**Choice:** O endpoint `/preview` retorna `efd_file_id` no payload. O frontend usa esse valor para acionar a geração — sem lookup extra.

**Rationale:** Evita request adicional do frontend para buscar o EFD file. A prévia já precisa saber qual EFD usar internamente — é natural retorná-lo.

**Alternatives Rejected:**
1. Frontend busca `/efd-files?fiscal_period_id=X` separado — request extra desnecessário
2. Novo endpoint de geração por `period_id` — duplicação do gerador existente

---

### Decision 3: Página separada com `useParams`, sem estado global

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |

**Context:** A página poderia ser uma aba em `competencias/[id]/page.tsx` ou uma página separada.

**Choice:** Página separada `competencias/[id]/correcoes/page.tsx` com `"use client"` e estado local.

**Rationale:** Usuário definiu rota separada. Mantém `page.tsx` principal leve — ele já é grande (1100+ linhas). Estado local é suficiente: a página carrega prévia no mount, gera sob demanda.

---

## File Manifest

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `backend/app/routers/fiscal_periods.py` | Modify | Adicionar `GET /{period_id}/corrections/preview` |
| 2 | `frontend/src/lib/types.ts` | Modify | Adicionar `CorrectionsPreview`, `PreviewGroup` |
| 3 | `frontend/src/app/competencias/[id]/correcoes/page.tsx` | Create | Página de prévia + geração |
| 4 | `frontend/src/app/competencias/[id]/page.tsx` | Modify | Adicionar link de navegação para `/correcoes` |

**Sem migration de banco. Sem novos modelos. Sem mudança no gerador.**

---

## Code Patterns

### 1. Backend — endpoint de prévia (`fiscal_periods.py`)

```python
from sqlalchemy import func
from app.models.correction import CorrectionSuggestion
from app.models.efd_file import EfdFile

@router.get("/{period_id}/corrections/preview")
def corrections_preview(period_id: uuid.UUID, db: Session = Depends(get_db)):
    efd_file = (
        db.query(EfdFile)
        .filter(EfdFile.fiscal_period_id == period_id)
        .order_by(EfdFile.uploaded_at.desc())
        .first()
    )
    if not efd_file:
        return {"efd_file_id": None, "total_approved": 0, "groups": []}

    rows = (
        db.query(
            CorrectionSuggestion.register_code,
            CorrectionSuggestion.rule_code,
            CorrectionSuggestion.field_name,
            CorrectionSuggestion.source,
            CorrectionSuggestion.original_value,
            CorrectionSuggestion.suggested_value,
            func.count(CorrectionSuggestion.id).label("count"),
        )
        .filter(
            CorrectionSuggestion.efd_file_id == efd_file.id,
            CorrectionSuggestion.status == "approved",
        )
        .group_by(
            CorrectionSuggestion.register_code,
            CorrectionSuggestion.rule_code,
            CorrectionSuggestion.field_name,
            CorrectionSuggestion.source,
            CorrectionSuggestion.original_value,
            CorrectionSuggestion.suggested_value,
        )
        .all()
    )

    groups = [
        {
            "register_code": r.register_code,
            "rule_code": r.rule_code,
            "field_name": r.field_name,
            "source": r.source,
            "original_value": r.original_value,
            "suggested_value": r.suggested_value,
            "count": r.count,
        }
        for r in rows
    ]

    return {
        "efd_file_id": str(efd_file.id),
        "total_approved": sum(g["count"] for g in groups),
        "groups": groups,
    }
```

---

### 2. Frontend — tipos (`types.ts`)

```typescript
export interface PreviewGroup {
  register_code: string;
  rule_code: string | null;
  field_name: string;
  source: string | null;
  original_value: string | null;
  suggested_value: string;
  count: number;
}

export interface CorrectionsPreview {
  efd_file_id: string | null;
  total_approved: number;
  groups: PreviewGroup[];
}
```

---

### 3. Frontend — página de correções (`correcoes/page.tsx`)

```typescript
"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeftIcon, DownloadIcon, FileCheckIcon, WandSparklesIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import type { CorrectionsPreview, CorrectedFile } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function CorrecoesPage() {
  const { id: periodId } = useParams<{ id: string }>();
  const router = useRouter();

  const [preview, setPreview] = useState<CorrectionsPreview | null>(null);
  const [correctedFiles, setCorrectedFiles] = useState<CorrectedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const prev = await api.get<CorrectionsPreview>(
        `/api/v1/fiscal-periods/${periodId}/corrections/preview`
      );
      setPreview(prev);

      if (prev.efd_file_id) {
        const files = await api.get<CorrectedFile[]>(
          `/api/v1/efd-files/${prev.efd_file_id}/corrected-files`
        );
        setCorrectedFiles(files);
      }
    } catch (err) {
      toast.error("Erro ao carregar prévia de correções.");
    } finally {
      setLoading(false);
    }
  }, [periodId]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleGenerate = useCallback(async () => {
    if (!preview?.efd_file_id) return;
    setGenerating(true);
    try {
      const cf = await api.post<CorrectedFile>(
        `/api/v1/efd-files/${preview.efd_file_id}/corrected-files/generate`,
        {}
      );
      setCorrectedFiles((prev) => [cf, ...prev]);
      toast.success(`TXT gerado: ${cf.generated_filename}`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro ao gerar TXT.");
    } finally {
      setGenerating(false);
    }
  }, [preview]);

  const canGenerate = (preview?.total_approved ?? 0) > 0 && !generating;

  // --- render ---

  if (loading) return <div className="p-6 text-sm text-muted-foreground">Carregando...</div>;

  return (
    <div className="p-6 space-y-6">
      {/* Cabeçalho */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Voltar
        </Button>
        <h1 className="text-2xl font-semibold">TXT Corrigido</h1>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded border p-4 text-center">
          <p className="text-xs text-muted-foreground">Correções aprovadas</p>
          <p className="text-2xl font-semibold">{preview?.total_approved ?? 0}</p>
        </div>
        <div className="rounded border p-4 text-center">
          <p className="text-xs text-muted-foreground">Registros afetados</p>
          <p className="text-2xl font-semibold">
            {new Set(preview?.groups.map((g) => g.register_code)).size ?? 0}
          </p>
        </div>
        <div className="rounded border p-4 text-center">
          <p className="text-xs text-muted-foreground">Fontes</p>
          <p className="text-2xl font-semibold">
            {new Set(preview?.groups.map((g) => g.source ?? "efd")).size ?? 0}
          </p>
        </div>
      </div>

      {/* Tabela de prévia */}
      {preview && preview.groups.length > 0 ? (
        <div className="space-y-2">
          <p className="text-sm font-medium">Prévia das correções a aplicar</p>
          <div className="rounded-lg border overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Registro</TableHead>
                  <TableHead>Regra</TableHead>
                  <TableHead>Campo</TableHead>
                  <TableHead>Original → Sugerido</TableHead>
                  <TableHead className="text-right">Qtd</TableHead>
                  <TableHead>Fonte</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {preview.groups.map((g, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-mono text-xs">{g.register_code}</TableCell>
                    <TableCell className="font-mono text-xs">{g.rule_code ?? "—"}</TableCell>
                    <TableCell className="text-xs">{g.field_name}</TableCell>
                    <TableCell className="text-xs">
                      <span className="text-destructive">{g.original_value ?? "—"}</span>
                      {" → "}
                      <span className="text-green-600 font-medium">{g.suggested_value}</span>
                    </TableCell>
                    <TableCell className="text-right text-xs font-semibold">{g.count}</TableCell>
                    <TableCell>
                      {g.source === "nfe_crosscheck" ? (
                        <Badge variant="outline" className="text-xs">
                          NF-e · Perspectiva do destinatário
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">Motor EFD</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Nenhuma correção aprovada para esta competência. Aprove sugestões nas abas de Validação ou NF-e.
        </p>
      )}

      {/* Botão de geração */}
      <div>
        <Button onClick={handleGenerate} disabled={!canGenerate}>
          <WandSparklesIcon className="mr-2 h-4 w-4" />
          {generating ? "Gerando..." : "Gerar TXT Corrigido"}
        </Button>
        {!canGenerate && !generating && (
          <p className="text-xs text-muted-foreground mt-1">
            Nenhuma correção aprovada para aplicar.
          </p>
        )}
      </div>

      {/* Histórico de arquivos gerados */}
      {correctedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Histórico de arquivos gerados</p>
          <div className="rounded-lg border overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Arquivo</TableHead>
                  <TableHead className="text-right">Correções aplicadas</TableHead>
                  <TableHead>Gerado em</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {correctedFiles.map((cf) => (
                  <TableRow key={cf.id}>
                    <TableCell className="font-mono text-xs">{cf.generated_filename}</TableCell>
                    <TableCell className="text-right text-xs">{cf.applied_suggestions_count}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(cf.generated_at).toLocaleString("pt-BR")}
                    </TableCell>
                    <TableCell>
                      <a
                        href={`${API_URL}/api/v1/corrected-files/${cf.id}/download`}
                        download
                      >
                        <Button size="sm" variant="outline">
                          <DownloadIcon className="h-4 w-4 mr-1" />
                          Baixar
                        </Button>
                      </a>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### 4. Frontend — link de navegação em `page.tsx`

Adicionar junto aos outros links/botões de ação da competência (próximo ao botão de relatórios ou no topo da página):

```typescript
import Link from "next/link";
import { FileCheckIcon } from "lucide-react";

// Dentro do JSX, na área de ações da competência:
<Link href={`/competencias/${period.id}/correcoes`}>
  <Button variant="outline" size="sm">
    <FileCheckIcon className="mr-2 h-4 w-4" />
    TXT Corrigido
    {dashboard?.suggestions?.approved > 0 && (
      <Badge className="ml-2" variant="secondary">
        {dashboard.suggestions.approved}
      </Badge>
    )}
  </Button>
</Link>
```

---

## Testing Strategy

| Test | Tipo | Como verificar |
|------|------|----------------|
| Preview com 0 aprovadas | Manual | Página mostra mensagem e botão desabilitado |
| Preview com sugestões EFD + NF-e | Manual | Tabela exibe ambas as fontes com badges corretos |
| Badge "Perspectiva do destinatário" | Manual | Linhas `source='nfe_crosscheck'` têm badge NF-e |
| Gerar TXT com aprovadas | Manual | Arquivo aparece no histórico, download funciona |
| CST no TXT gerado | Manual | Abrir TXT, verificar campo 10 do C170 com CST 060 |
| AT-008 conflito | Manual | Gerar com 2 sugestões na mesma linha — apenas limpa sem erro |
| AT-009 sem EFD | Manual | Endpoint retorna `{"efd_file_id": null, "total_approved": 0}` |

---

## Checklist de qualidade

```text
[x] Sem migration de banco
[x] Sem modificação do corrected_file_generator.py
[x] efd_file_id retornado pelo preview evita request extra no frontend
[x] CST NF-e usa suggested_value (perspectiva do destinatário) — não modificado pelo frontend
[x] Botão desabilitado se total_approved = 0
[x] Histórico usa endpoint existente GET /efd-files/{id}/corrected-files
[x] Download usa href nativo (não api.get) para forçar download do browser
[x] Encoding latin-1 garantido pelo gerador existente
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_CORRECOES_TXT.md`
