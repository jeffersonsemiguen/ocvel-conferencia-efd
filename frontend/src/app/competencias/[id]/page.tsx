"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import {
  FileTextIcon, UploadIcon, PlusIcon, CheckIcon,
  ChevronDownIcon, ChevronRightIcon, AlertCircleIcon, PlayIcon,
  DownloadIcon, WandSparklesIcon, XIcon, RefreshCwIcon, ClockIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import type {
  ApuracaoReferenceValue, Company, CorrectedFile, CorrectionSuggestion,
  EfdFile, FiscalPeriod, PdfApuracaoFile, PdfExtractedPage,
  ValidationFinding, ValidationRun,
} from "@/lib/types";

// ─── Tipos Sprint 8 ───────────────────────────────────────────────────────────

interface RiskScoreResult {
  score: number;
  risk_level: "low" | "moderate" | "high" | "critical";
  breakdown: { reason: string; points: number }[];
  critical_count: number;
  warning_count: number;
  snapshot_id?: string;
  calculated_at?: string;
}

interface PeriodDashboard {
  period: { id: string; year: number; month: number; status: string };
  company: { id: string; name: string; cnpj: string };
  files: { efd_count: number; pdf_count: number; corrected_count: number; latest_efd_status: string | null };
  findings: { critical_count: number; warning_count: number; total: number; last_run_at: string | null };
  suggestions: { pending: number; approved: number; rejected: number; applied: number; total: number };
  risk: RiskScoreResult;
  next_action: string;
}

interface PeriodEvent {
  id: string;
  event_type: string;
  event_title: string;
  event_description: string | null;
  created_at: string;
}

// ─── RiskScoreCard ────────────────────────────────────────────────────────────

function riskColor(risk: string): string {
  switch (risk) {
    case "low":      return "text-green-600";
    case "moderate": return "text-yellow-600";
    case "high":     return "text-orange-500";
    case "critical": return "text-destructive";
    default:         return "text-muted-foreground";
  }
}

function riskBgColor(score: number): string {
  if (score <= 20) return "bg-green-50 border-green-200 dark:bg-green-950/20";
  if (score <= 50) return "bg-yellow-50 border-yellow-200 dark:bg-yellow-950/20";
  if (score <= 80) return "bg-orange-50 border-orange-200 dark:bg-orange-950/20";
  return "bg-red-50 border-red-200 dark:bg-red-950/20";
}

const RISK_LABELS: Record<string, string> = {
  low: "Baixo", moderate: "Moderado", high: "Alto", critical: "Crítico",
};

function RiskScoreCard({ periodId }: { periodId: string }) {
  const [result, setResult] = useState<RiskScoreResult | null>(null);
  const [loading, setLoading] = useState(false);

  const calculate = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.post<RiskScoreResult>(
        `/api/v1/fiscal-periods/${periodId}/risk-score/calculate`, {}
      );
      setResult(data);
    } catch {
      toast.error("Erro ao calcular score de risco");
    } finally {
      setLoading(false);
    }
  }, [periodId]);

  useEffect(() => { calculate(); }, [calculate]);

  if (!result && !loading) return null;

  return (
    <div className={`rounded-lg border p-4 ${result ? riskBgColor(result.score) : "bg-muted/30"}`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Score de Risco</p>
        <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" onClick={calculate} disabled={loading}>
          <RefreshCwIcon className={`w-3 h-3 mr-1 ${loading ? "animate-spin" : ""}`} />
          Recalcular
        </Button>
      </div>
      {loading && !result ? (
        <p className="text-sm text-muted-foreground">Calculando...</p>
      ) : result ? (
        <div className="flex items-end gap-3">
          <span className={`text-4xl font-bold tabular-nums ${riskColor(result.risk_level)}`}>
            {result.score}
          </span>
          <div className="mb-1">
            <span className="text-sm text-muted-foreground">/100</span>
            <div className="mt-0.5">
              <Badge
                variant={result.risk_level === "critical" ? "destructive" : "secondary"}
                className="text-xs"
              >
                {RISK_LABELS[result.risk_level] ?? result.risk_level}
              </Badge>
            </div>
          </div>
          {result.breakdown.length > 0 && (
            <div className="ml-auto text-right text-xs text-muted-foreground space-y-0.5">
              <p>{result.critical_count} crítico(s) · {result.warning_count} alerta(s)</p>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

// ─── NextActionCard ───────────────────────────────────────────────────────────

function NextActionCard({ periodId }: { periodId: string }) {
  const [dashboard, setDashboard] = useState<PeriodDashboard | null>(null);

  useEffect(() => {
    api.get<PeriodDashboard>(`/api/v1/fiscal-periods/${periodId}/dashboard`)
      .then(setDashboard)
      .catch(() => { /* silently ignore on first load */ });
  }, [periodId]);

  if (!dashboard) return null;

  const { findings, suggestions, next_action } = dashboard;

  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Próxima Ação</p>
      <p className="text-base font-medium">{next_action}</p>
      <div className="flex gap-4 text-sm text-muted-foreground flex-wrap">
        {findings.critical_count > 0 && (
          <span className="text-destructive font-medium">{findings.critical_count} crítico(s)</span>
        )}
        {findings.warning_count > 0 && (
          <span className="text-orange-500">{findings.warning_count} alerta(s)</span>
        )}
        {suggestions.pending > 0 && (
          <span className="text-yellow-600">{suggestions.pending} sugestão(ões) pendente(s)</span>
        )}
        {findings.critical_count === 0 && findings.warning_count === 0 && suggestions.pending === 0 && (
          <span className="text-green-600">Sem pendências críticas</span>
        )}
      </div>
    </div>
  );
}

// ─── TimelineCard ─────────────────────────────────────────────────────────────

const EVENT_TYPE_LABELS: Record<string, string> = {
  efd_processed: "EFD Processada",
  validation_run: "Conferência",
  corrected_file_generated: "TXT Corrigido",
  manual: "Evento Manual",
};

function TimelineCard({ periodId }: { periodId: string }) {
  const [events, setEvents] = useState<PeriodEvent[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api.get<PeriodEvent[]>(`/api/v1/fiscal-periods/${periodId}/events?limit=10`)
      .then(data => { setEvents(data); setLoaded(true); })
      .catch(() => setLoaded(true));
  }, [periodId]);

  if (!loaded || events.length === 0) return null;

  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
        Histórico de Atividades
      </p>
      <div className="space-y-2">
        {events.map(ev => (
          <div key={ev.id} className="flex items-start gap-2 text-sm">
            <ClockIcon className="w-3.5 h-3.5 mt-0.5 text-muted-foreground shrink-0" />
            <div className="flex-1 min-w-0">
              <span className="font-medium">{EVENT_TYPE_LABELS[ev.event_type] ?? ev.event_type}</span>
              {" — "}
              <span className="text-muted-foreground">{ev.event_title}</span>
            </div>
            <span className="text-xs text-muted-foreground shrink-0">
              {new Date(ev.created_at).toLocaleDateString("pt-BR")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

const MESES = [
  "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
  "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro",
];
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const fmt = (v: number | null | undefined) =>
  v != null ? v.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) : "—";

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
    parsed:         { label: "Processado",     variant: "default" },
    extracted:      { label: "Extraído",       variant: "default" },
    uploaded:       { label: "Aguardando",     variant: "secondary" },
    pending:        { label: "Pendente",       variant: "secondary" },
    low_confidence: { label: "Baixa confiança",variant: "outline" },
    error:          { label: "Erro",           variant: "destructive" },
    failed:         { label: "Falha",          variant: "destructive" },
  };
  const info = map[status] ?? { label: status, variant: "secondary" as const };
  return <Badge variant={info.variant}>{info.label}</Badge>;
}

// ─── Aba EFD ────────────────────────────────────────────────────────────────

function EfdTab({ period }: { period: FiscalPeriod }) {
  const [files, setFiles] = useState<EfdFile[]>([]);
  const [loading, setLoading] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    api.get<EfdFile[]>(`/api/v1/fiscal-periods/${period.id}/efd-files`)
      .then(setFiles).catch(() => toast.error("Erro ao carregar arquivos EFD"))
      .finally(() => setLoading(false));
  }, [period.id]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/fiscal-periods/${period.id}/efd-files`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText);
      const efd: EfdFile = await res.json();
      setFiles(p => [...p, efd]);
      toast.success(efd.parse_status === "parsed"
        ? `Processado — ${efd.total_lines?.toLocaleString()} linhas`
        : "Arquivo enviado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{files.length} arquivo(s) EFD</p>
        <Button size="sm" variant="outline" onClick={() => inputRef.current?.click()} disabled={uploading}>
          <UploadIcon className="w-3.5 h-3.5 mr-1" />
          {uploading ? "Enviando..." : "Enviar EFD (.txt)"}
        </Button>
        <input ref={inputRef} type="file" accept=".txt" className="hidden" onChange={handleUpload} />
      </div>

      {loading ? <p className="text-sm text-muted-foreground">Carregando...</p> : files.length === 0 ? (
        <div className="border-2 border-dashed rounded-lg p-10 text-center text-muted-foreground text-sm">
          Nenhum arquivo EFD enviado ainda.
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Arquivo</TableHead>
                <TableHead>Empresa (EFD)</TableHead>
                <TableHead>Período EFD</TableHead>
                <TableHead>Linhas</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-24" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {files.map(f => (
                <TableRow key={f.id}>
                  <TableCell className="font-mono text-xs">{f.original_filename}</TableCell>
                  <TableCell className="text-sm">{f.efd_company_name ?? "—"}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {f.efd_start_date && f.efd_end_date ? `${f.efd_start_date} → ${f.efd_end_date}` : "—"}
                  </TableCell>
                  <TableCell className="text-sm">{f.total_lines?.toLocaleString() ?? "—"}</TableCell>
                  <TableCell><StatusBadge status={f.parse_status} /></TableCell>
                  <TableCell>
                    <Button
                      size="sm" variant="ghost" className="h-6 text-xs px-2"
                      onClick={async () => {
                        try {
                          const updated = await api.post<EfdFile>(`/api/v1/efd-files/${f.id}/reparse`, {});
                          setFiles(prev => prev.map(x => x.id === f.id ? updated : x));
                          toast.success("Re-processado com sucesso");
                        } catch { toast.error("Erro ao re-processar"); }
                      }}
                    >
                      Re-parsear
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}

// ─── Aba PDF ─────────────────────────────────────────────────────────────────

function PdfTab({ period }: { period: FiscalPeriod }) {
  const [pdfs, setPdfs] = useState<PdfApuracaoFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [pages, setPages] = useState<Record<string, PdfExtractedPage[]>>({});
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.get<PdfApuracaoFile[]>(`/api/v1/fiscal-periods/${period.id}/pdf-apuracao-files`)
      .then(setPdfs).catch(() => toast.error("Erro ao carregar PDFs"))
      .finally(() => setLoading(false));
  }, [period.id]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/fiscal-periods/${period.id}/pdf-apuracao-files`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText);
      const pdf: PdfApuracaoFile = await res.json();
      setPdfs(p => [...p, pdf]);
      if (pdf.extraction_status === "extracted") {
        toast.success(`PDF processado — ${pdf.total_pages} página(s), confiança ${pdf.average_confidence?.toFixed(0)}%`);
      } else if (pdf.extraction_status === "low_confidence") {
        toast.warning(`PDF com baixa confiança (${pdf.average_confidence?.toFixed(0)}%). Considere importar planilha.`);
      } else {
        toast.error(`Extração falhou: ${pdf.extraction_error}`);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function togglePages(pdfId: string) {
    if (expandedId === pdfId) { setExpandedId(null); return; }
    setExpandedId(pdfId);
    if (!pages[pdfId]) {
      try {
        const data = await api.get<PdfExtractedPage[]>(`/api/v1/pdf-apuracao-files/${pdfId}/extracted-pages`);
        setPages(p => ({ ...p, [pdfId]: data }));
      } catch {
        toast.error("Erro ao carregar páginas");
      }
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{pdfs.length} PDF(s) de apuração</p>
        <Button size="sm" variant="outline" onClick={() => inputRef.current?.click()} disabled={uploading}>
          <UploadIcon className="w-3.5 h-3.5 mr-1" />
          {uploading ? "Enviando..." : "Enviar PDF de apuração"}
        </Button>
        <input ref={inputRef} type="file" accept=".pdf" className="hidden" onChange={handleUpload} />
      </div>

      {loading ? <p className="text-sm text-muted-foreground">Carregando...</p> : pdfs.length === 0 ? (
        <div className="border-2 border-dashed rounded-lg p-10 text-center text-muted-foreground text-sm">
          Nenhum PDF de apuração enviado ainda.
        </div>
      ) : (
        <div className="space-y-2">
          {pdfs.map(pdf => (
            <div key={pdf.id} className="border rounded-lg overflow-hidden">
              <div
                className="flex items-center gap-3 p-3 cursor-pointer hover:bg-muted/30"
                onClick={() => togglePages(pdf.id)}
              >
                {expandedId === pdf.id
                  ? <ChevronDownIcon className="w-4 h-4 text-muted-foreground shrink-0" />
                  : <ChevronRightIcon className="w-4 h-4 text-muted-foreground shrink-0" />}
                <FileTextIcon className="w-4 h-4 text-muted-foreground shrink-0" />
                <span className="text-sm font-medium flex-1">{pdf.original_filename}</span>
                <span className="text-xs text-muted-foreground">{pdf.total_pages ?? "?"} pág.</span>
                {pdf.average_confidence != null && (
                  <span className="text-xs text-muted-foreground">
                    confiança {pdf.average_confidence.toFixed(0)}%
                  </span>
                )}
                <StatusBadge status={pdf.extraction_status} />
              </div>

              {expandedId === pdf.id && (
                <div className="border-t bg-muted/10 p-3 space-y-1 max-h-72 overflow-y-auto">
                  {pdf.extraction_status === "low_confidence" && (
                    <div className="flex items-center gap-2 text-amber-600 text-xs mb-2">
                      <AlertCircleIcon className="w-3.5 h-3.5" />
                      Texto extraído com baixa confiança. Recomenda-se importar planilha padronizada.
                    </div>
                  )}
                  {!pages[pdf.id] ? (
                    <p className="text-xs text-muted-foreground">Carregando páginas...</p>
                  ) : pages[pdf.id].length === 0 ? (
                    <p className="text-xs text-muted-foreground">Nenhuma página encontrada.</p>
                  ) : (
                    pages[pdf.id].map(p => (
                      <div key={p.page_number} className="text-xs border rounded p-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">Página {p.page_number}</span>
                          <span className="text-muted-foreground">
                            {p.char_count} chars · confiança {p.confidence_score}%
                          </span>
                        </div>
                        {p.extracted_text ? (
                          <pre className="text-muted-foreground whitespace-pre-wrap font-mono text-[10px] max-h-20 overflow-y-auto">
                            {p.extracted_text.slice(0, 400)}{p.extracted_text.length > 400 ? "…" : ""}
                          </pre>
                        ) : (
                          <span className="text-muted-foreground italic">Sem texto extraído</span>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Aba Valores de Referência ────────────────────────────────────────────────

const OP_LABELS: Record<string, string> = {
  entrada: "Entrada", saida: "Saída",
  apuracao_icms: "Apuração ICMS", apuracao_icms_st: "Apuração ICMS-ST",
  apuracao_ipi: "Apuração IPI", ajuste_icms: "Ajuste ICMS", ajuste_ipi: "Ajuste IPI",
};

const TAX_LABELS: Record<string, string> = {
  icms: "ICMS", icms_st: "ICMS-ST", ipi: "IPI",
  difal: "DIFAL", fecop: "FECOP", outros: "Outros",
};

function ApuracaoTab({ period }: { period: FiscalPeriod }) {
  const [values, setValues] = useState<ApuracaoReferenceValue[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  function reload() {
    api.get<ApuracaoReferenceValue[]>(`/api/v1/fiscal-periods/${period.id}/apuracao-reference-values`)
      .then(setValues).catch(() => toast.error("Erro ao carregar valores"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { reload(); }, [period.id]);

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(
        `${API_BASE}/api/v1/fiscal-periods/${period.id}/apuracao-reference/import-spreadsheet`,
        { method: "POST", body: form }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(Array.isArray(data.detail) ? data.detail.join("; ") : data.detail);
      toast.success(`${data.rows_imported} linha(s) importada(s)${data.rows_skipped > 0 ? `, ${data.rows_skipped} ignorada(s)` : ""}`);
      if (data.errors?.length) toast.warning(`Avisos: ${data.errors.join("; ")}`);
      reload();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro na importação");
    } finally {
      setImporting(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function markReviewed(id: string) {
    try {
      await api.post(`/api/v1/apuracao-reference-values/${id}/mark-reviewed`, {});
      setValues(v => v.map(r => r.id === id ? { ...r, is_reviewed: true } : r));
      toast.success("Marcado como revisado");
    } catch {
      toast.error("Erro ao marcar como revisado");
    }
  }

  async function deleteValue(id: string) {
    try {
      await fetch(`${API_BASE}/api/v1/apuracao-reference-values/${id}`, { method: "DELETE" });
      setValues(v => v.filter(r => r.id !== id));
    } catch {
      toast.error("Erro ao remover valor");
    }
  }

  const unreviewedCount = values.filter(v => !v.is_reviewed).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            {values.length} valor(es) de referência
            {unreviewedCount > 0 && (
              <span className="ml-2 text-amber-600 font-medium">{unreviewedCount} pendente(s) de revisão</span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()} disabled={importing}>
            <UploadIcon className="w-3.5 h-3.5 mr-1" />
            {importing ? "Importando..." : "Importar planilha"}
          </Button>
          <input ref={fileRef} type="file" accept=".xlsx,.xlsm,.csv" className="hidden" onChange={handleImport} />
          <NovoValorDialog periodId={period.id} companyId={period.company_id} onCreated={v => setValues(p => [...p, v])} />
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : values.length === 0 ? (
        <div className="border-2 border-dashed rounded-lg p-10 text-center text-muted-foreground text-sm space-y-1">
          <p>Nenhum valor de referência cadastrado.</p>
          <p>Importe uma planilha padronizada ou cadastre manualmente.</p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Origem</TableHead>
                <TableHead>Tipo operação</TableHead>
                <TableHead>Imposto</TableHead>
                <TableHead>CFOP</TableHead>
                <TableHead>CST</TableHead>
                <TableHead className="text-right">Vl. Contábil</TableHead>
                <TableHead className="text-right">Base ICMS</TableHead>
                <TableHead className="text-right">ICMS</TableHead>
                <TableHead className="text-right">IPI</TableHead>
                <TableHead>Revisão</TableHead>
                <TableHead className="w-20" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {values.map(v => (
                <TableRow key={v.id} className={v.is_reviewed ? "" : "bg-amber-50/30 dark:bg-amber-950/10"}>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {v.source_type === "spreadsheet" ? "Planilha" : v.source_type === "manual" ? "Manual" : "PDF"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">{OP_LABELS[v.operation_type] ?? v.operation_type}</TableCell>
                  <TableCell className="text-sm">{TAX_LABELS[v.tax_type] ?? v.tax_type}</TableCell>
                  <TableCell className="font-mono text-sm">{v.cfop ?? "—"}</TableCell>
                  <TableCell className="font-mono text-sm">{v.cst ?? v.csosn ?? "—"}</TableCell>
                  <TableCell className="text-right text-sm tabular-nums">{fmt(v.accounting_value)}</TableCell>
                  <TableCell className="text-right text-sm tabular-nums">{fmt(v.icms_base)}</TableCell>
                  <TableCell className="text-right text-sm tabular-nums">{fmt(v.icms_amount)}</TableCell>
                  <TableCell className="text-right text-sm tabular-nums">{fmt(v.ipi_amount)}</TableCell>
                  <TableCell>
                    {v.is_reviewed ? (
                      <Badge variant="default" className="text-xs gap-1">
                        <CheckIcon className="w-3 h-3" />Revisado
                      </Badge>
                    ) : (
                      <Button size="sm" variant="outline" className="h-6 text-xs px-2"
                        onClick={() => markReviewed(v.id)}>
                        Revisar
                      </Button>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button size="sm" variant="ghost" className="h-6 text-xs px-2 text-destructive"
                      onClick={() => deleteValue(v.id)}>
                      Excluir
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}

function NovoValorDialog({
  periodId, companyId, onCreated,
}: {
  periodId: string;
  companyId: string;
  onCreated: (v: ApuracaoReferenceValue) => void;
}) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    operation_type: "entrada", tax_type: "icms",
    cfop: "", cst: "", source_label: "",
    accounting_value: "", icms_base: "", icms_amount: "",
    icms_st_base: "", icms_st_amount: "", ipi_base: "", ipi_amount: "",
  });

  function set(k: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm(f => ({ ...f, [k]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const toNum = (s: string) => s.trim() ? parseFloat(s.replace(",", ".")) : null;
      const val = await api.post<ApuracaoReferenceValue>(
        `/api/v1/fiscal-periods/${periodId}/apuracao-reference-values`,
        {
          operation_type: form.operation_type, tax_type: form.tax_type,
          cfop: form.cfop || null, cst: form.cst || null,
          source_label: form.source_label || null,
          accounting_value: toNum(form.accounting_value),
          icms_base: toNum(form.icms_base), icms_amount: toNum(form.icms_amount),
          icms_st_base: toNum(form.icms_st_base), icms_st_amount: toNum(form.icms_st_amount),
          ipi_base: toNum(form.ipi_base), ipi_amount: toNum(form.ipi_amount),
        }
      );
      onCreated(val);
      setOpen(false);
      toast.success("Valor criado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao criar valor");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm"><PlusIcon className="w-4 h-4 mr-1" />Novo valor</Button>} />
      <DialogContent className="sm:max-w-lg">
        <DialogHeader><DialogTitle>Novo valor de referência</DialogTitle></DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Tipo de operação *</Label>
              <select value={form.operation_type} onChange={set("operation_type")}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm">
                {Object.entries(OP_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Tipo de imposto *</Label>
              <select value={form.tax_type} onChange={set("tax_type")}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm">
                {Object.entries(TAX_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label>CFOP</Label>
              <Input placeholder="5102" value={form.cfop} onChange={set("cfop")} />
            </div>
            <div className="space-y-1">
              <Label>CST</Label>
              <Input placeholder="000" value={form.cst} onChange={set("cst")} />
            </div>
            <div className="col-span-1 space-y-1">
              <Label>Descrição</Label>
              <Input placeholder="Ex: Saídas CFOP 5102" value={form.source_label} onChange={set("source_label")} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              ["accounting_value", "Vl. Contábil"], ["icms_base", "Base ICMS"], ["icms_amount", "ICMS"],
              ["icms_st_base", "Base ICMS-ST"], ["icms_st_amount", "ICMS-ST"],
              ["ipi_base", "Base IPI"], ["ipi_amount", "IPI"],
            ].map(([k, label]) => (
              <div key={k} className="space-y-1">
                <Label>{label}</Label>
                <Input placeholder="0,00" value={form[k as keyof typeof form]} onChange={set(k as keyof typeof form)} />
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" disabled={loading}>{loading ? "Salvando..." : "Salvar"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── Seção de Sugestões de Correção ──────────────────────────────────────────

const RISK_CONFIG: Record<string, { label: string; className: string }> = {
  critical: { label: "Crítico",    className: "bg-destructive text-destructive-foreground" },
  high:     { label: "Alto",       className: "bg-orange-100 text-orange-800" },
  medium:   { label: "Médio",      className: "bg-primary/20 text-foreground" },
  low:      { label: "Baixo",      className: "bg-muted text-muted-foreground" },
};

const TYPE_CONFIG: Record<string, { label: string; className: string }> = {
  technical:     { label: "Técnico",      className: "bg-blue-100 text-blue-800" },
  fiscal:        { label: "Fiscal",       className: "bg-primary/20 text-foreground" },
  structural:    { label: "Estrutural",   className: "bg-purple-100 text-purple-800" },
  informational: { label: "Informativo",  className: "bg-muted text-muted-foreground" },
};

function RiskBadge({ risk }: { risk: string }) {
  const cfg = RISK_CONFIG[risk] ?? { label: risk, className: "bg-muted text-muted-foreground" };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}

function TypeBadge({ type }: { type: string }) {
  const cfg = TYPE_CONFIG[type] ?? { label: type, className: "bg-muted text-muted-foreground" };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}

function SugestoesSection({
  run,
  efdFileId,
}: {
  run: ValidationRun;
  efdFileId: string;
}) {
  const [suggestions, setSuggestions] = useState<CorrectionSuggestion[]>([]);
  const [correctedFiles, setCorrectedFiles] = useState<CorrectedFile[]>([]);
  const [loadingGen, setLoadingGen] = useState(false);
  const [loadingTxt, setLoadingTxt] = useState(false);
  const [expanded, setExpanded] = useState(false);

  async function loadData() {
    try {
      const [sugs, files] = await Promise.all([
        api.get<CorrectionSuggestion[]>(`/api/v1/validation-runs/${run.id}/correction-suggestions`),
        api.get<CorrectedFile[]>(`/api/v1/efd-files/${efdFileId}/corrected-files`),
      ]);
      setSuggestions(sugs);
      setCorrectedFiles(files);
    } catch { /* silently */ }
  }

  useEffect(() => { loadData(); }, [run.id]);

  async function handleGenerate() {
    setLoadingGen(true);
    try {
      const res = await api.post<{ created: number; skipped: number; pending_total: number }>(
        `/api/v1/validation-runs/${run.id}/correction-suggestions/generate`, {}
      );
      // Reload the list after generation
      const sugs = await api.get<CorrectionSuggestion[]>(`/api/v1/validation-runs/${run.id}/correction-suggestions`);
      setSuggestions(sugs);
      if (res.created === 0) {
        toast.info("Nenhuma sugestão automática disponível para os achados desta conferência");
      } else {
        toast.success(`${res.created} sugestão(ões) gerada(s) · ${res.skipped} ignorada(s)`);
        setExpanded(true);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao gerar sugestões");
    } finally {
      setLoadingGen(false);
    }
  }

  async function handleApprove(id: string) {
    try {
      const updated = await api.post<CorrectionSuggestion>(`/api/v1/correction-suggestions/${id}/approve`, {});
      setSuggestions(prev => prev.map(s => s.id === id ? updated : s));
      toast.success("Sugestão aprovada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao aprovar");
    }
  }

  async function handleReject(id: string) {
    try {
      const updated = await api.post<CorrectionSuggestion>(`/api/v1/correction-suggestions/${id}/reject`, {});
      setSuggestions(prev => prev.map(s => s.id === id ? updated : s));
    } catch { toast.error("Erro ao rejeitar"); }
  }

  async function handleBulkApprove() {
    const pendingLowMed = suggestions
      .filter(s => s.status === "pending" && !["high", "critical"].includes(s.risk_level))
      .map(s => s.id);
    if (!pendingLowMed.length) {
      toast.info("Nenhuma sugestão de baixo/médio risco para aprovar em lote");
      return;
    }
    try {
      const res = await api.post<{ approved: number }>(
        `/api/v1/correction-suggestions/bulk-approve`,
        { suggestion_ids: pendingLowMed }
      );
      // Reload list for accuracy
      const sugs = await api.get<CorrectionSuggestion[]>(`/api/v1/validation-runs/${run.id}/correction-suggestions`);
      setSuggestions(sugs);
      toast.success(`${res.approved} sugestão(ões) aprovada(s) em lote`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao aprovar em lote");
    }
  }

  async function handleGenerateTxt() {
    setLoadingTxt(true);
    try {
      const corrected = await api.post<CorrectedFile>(
        `/api/v1/efd-files/${efdFileId}/corrected-files/generate`, {}
      );
      setCorrectedFiles(prev => [corrected, ...prev]);
      toast.success(`TXT corrigido gerado: ${corrected.generated_filename}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao gerar TXT");
    } finally {
      setLoadingTxt(false);
    }
  }

  const pending = suggestions.filter(s => s.status === "pending");
  const approved = suggestions.filter(s => s.status === "approved");
  const rejected = suggestions.filter(s => s.status === "rejected");
  const hasSuggestions = suggestions.length > 0;

  return (
    <div className="border rounded-lg overflow-hidden mt-4 bg-card">
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/30 bg-muted/10"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex items-center gap-2">
          {expanded ? <ChevronDownIcon className="w-4 h-4" /> : <ChevronRightIcon className="w-4 h-4" />}
          <span className="text-sm font-semibold">Sugestões de Correção</span>
          {hasSuggestions && (
            <Badge variant="secondary" className="text-xs">{suggestions.length} total</Badge>
          )}
          {pending.length > 0 && (
            <Badge variant="outline" className="text-xs text-amber-600">{pending.length} pendente(s)</Badge>
          )}
          {approved.length > 0 && (
            <Badge variant="default" className="text-xs">{approved.length} aprovada(s)</Badge>
          )}
          {rejected.length > 0 && (
            <Badge variant="secondary" className="text-xs">{rejected.length} rejeitada(s)</Badge>
          )}
        </div>
        <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
          <Button size="sm" variant="outline" onClick={handleGenerate} disabled={loadingGen}>
            <WandSparklesIcon className="w-3.5 h-3.5 mr-1" />
            {loadingGen ? "Gerando..." : "Gerar sugestões"}
          </Button>
          {approved.length > 0 && (
            <Button size="sm" className="bg-primary" onClick={handleGenerateTxt} disabled={loadingTxt}>
              <DownloadIcon className="w-3.5 h-3.5 mr-1" />
              {loadingTxt ? "Gerando TXT..." : "Gerar TXT Corrigido"}
            </Button>
          )}
        </div>
      </div>

      {expanded && (
        <div className="border-t">
          {!hasSuggestions ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              Clique em &quot;Gerar sugestões&quot; para criar sugestões automáticas a partir dos achados.
            </p>
          ) : (
            <>
              {pending.length > 0 && (
                <div className="flex items-center justify-between px-4 py-2 bg-amber-50/30 border-b text-xs">
                  <span className="text-amber-700">
                    {pending.length} sugestão(ões) aguardando revisão
                    {pending.some(s => ["high", "critical"].includes(s.risk_level)) && (
                      <span className="ml-2 text-destructive font-medium">· contém risco alto/crítico (aprovação individual)</span>
                    )}
                  </span>
                  <Button size="sm" variant="outline" className="h-6 text-xs px-2" onClick={handleBulkApprove}>
                    <CheckIcon className="w-3 h-3 mr-1" />Aprovar baixo/médio risco
                  </Button>
                </div>
              )}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Linha</TableHead>
                    <TableHead className="w-16">Registro</TableHead>
                    <TableHead className="w-24">Tipo</TableHead>
                    <TableHead>Campo / Motivo</TableHead>
                    <TableHead>Valor atual</TableHead>
                    <TableHead>Valor sugerido</TableHead>
                    <TableHead className="w-24">Risco</TableHead>
                    <TableHead className="w-28">Status</TableHead>
                    <TableHead className="w-36" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {suggestions.map(s => (
                    <TableRow key={s.id} className={s.status === "rejected" ? "opacity-40" : ""}>
                      <TableCell className="font-mono text-xs">
                        {s.line_number > 0 ? s.line_number : "—"}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{s.register_code || "—"}</TableCell>
                      <TableCell>
                        <TypeBadge type={s.suggestion_type} />
                      </TableCell>
                      <TableCell>
                        <p className="text-xs font-mono">{s.field_name || "—"}</p>
                        {s.suggestion_reason && (
                          <p className="text-xs text-muted-foreground mt-0.5 max-w-xs truncate">{s.suggestion_reason}</p>
                        )}
                        {s.rule_code && (
                          <p className="text-xs text-muted-foreground font-mono">{s.rule_code}</p>
                        )}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">{s.original_value ?? "—"}</TableCell>
                      <TableCell className="font-mono text-xs font-medium max-w-[160px] truncate" title={s.suggested_value}>
                        {s.suggested_value}
                      </TableCell>
                      <TableCell>
                        <RiskBadge risk={s.risk_level} />
                      </TableCell>
                      <TableCell>
                        {s.status === "pending" && <Badge variant="outline" className="text-xs">Pendente</Badge>}
                        {s.status === "approved" && <Badge variant="default" className="text-xs gap-1"><CheckIcon className="w-3 h-3" />Aprovado</Badge>}
                        {s.status === "rejected" && <Badge variant="secondary" className="text-xs gap-1"><XIcon className="w-3 h-3" />Rejeitado</Badge>}
                        {s.status === "applied" && <Badge variant="default" className="text-xs">Aplicado</Badge>}
                        {s.status === "conflict" && <Badge variant="destructive" className="text-xs">Conflito</Badge>}
                        {s.status === "canceled" && <Badge variant="secondary" className="text-xs">Cancelado</Badge>}
                      </TableCell>
                      <TableCell>
                        {s.status === "pending" && (
                          <div className="flex gap-1">
                            <Button size="sm" variant="default" className="h-6 text-xs px-2"
                              onClick={() => handleApprove(s.id)}>
                              <CheckIcon className="w-3 h-3 mr-1" />Aprovar
                            </Button>
                            <Button size="sm" variant="ghost" className="h-6 text-xs px-2 text-destructive"
                              onClick={() => handleReject(s.id)}>
                              Rejeitar
                            </Button>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </>
          )}

          {/* Arquivos corrigidos gerados */}
          {correctedFiles.length > 0 && (
            <div className="border-t bg-muted/10 px-4 py-3">
              <p className="text-xs font-semibold text-muted-foreground mb-2">Arquivos TXT corrigidos gerados</p>
              <div className="space-y-2">
                {correctedFiles.map(cf => (
                  <div key={cf.id} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="font-mono text-xs">{cf.generated_filename}</span>
                      <span className="text-xs text-muted-foreground ml-2">
                        {cf.applied_suggestions_count} alteração(ões)
                        {cf.total_lines != null && ` · ${cf.total_lines.toLocaleString()} linhas`}
                        {" · "}{new Date(cf.generated_at).toLocaleString("pt-BR")}
                      </span>
                    </div>
                    <a
                      href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/corrected-files/${cf.id}/download`}
                      download
                    >
                      <Button size="sm" variant="outline" className="h-7 text-xs">
                        <DownloadIcon className="w-3 h-3 mr-1" />Download
                      </Button>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Aba Conferências ─────────────────────────────────────────────────────────

const SEVERITY_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline"; color: string }> = {
  critico:              { label: "Crítico",              variant: "destructive", color: "text-red-600" },
  alerta:               { label: "Alerta",               variant: "outline",     color: "text-amber-600" },
  divergencia_monetaria:{ label: "Divergência",          variant: "secondary",   color: "text-blue-600" },
  observacao:           { label: "Observação",           variant: "outline",     color: "text-muted-foreground" },
};

function ConferenciaTab({ period }: { period: FiscalPeriod }) {
  const [runs, setRuns] = useState<ValidationRun[]>([]);
  const [activeRun, setActiveRun] = useState<ValidationRun | null>(null);
  const [findings, setFindings] = useState<ValidationFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState("");

  useEffect(() => {
    api.get<ValidationRun[]>(`/api/v1/fiscal-periods/${period.id}/validation-runs`)
      .then(r => { setRuns(r); if (r.length > 0) loadFindings(r[0]); })
      .catch(() => toast.error("Erro ao carregar conferências"))
      .finally(() => setLoading(false));
  }, [period.id]);

  async function loadFindings(run: ValidationRun) {
    setActiveRun(run);
    try {
      const data = await api.get<ValidationFinding[]>(`/api/v1/validation-runs/${run.id}/findings`);
      setFindings(data);
    } catch {
      toast.error("Erro ao carregar achados");
    }
  }

  async function executeConference() {
    setRunning(true);
    try {
      const run = await api.post<ValidationRun>(
        `/api/v1/fiscal-periods/${period.id}/validation-runs`, {}
      );
      setRuns(prev => [run, ...prev]);
      await loadFindings(run);
      if (run.status === "completed") {
        toast.success(`Conferência concluída — ${run.total_findings} achado(s)`);
      } else {
        toast.error(`Erro na conferência: ${run.error}`);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao executar conferência");
    } finally {
      setRunning(false);
    }
  }

  async function updateFindingStatus(id: string, newStatus: "acknowledged" | "resolved") {
    try {
      await api.post(`/api/v1/validation-findings/${id}/${newStatus}`, {});
      setFindings(prev => prev.map(f => f.id === id ? { ...f, status: newStatus } : f));
    } catch {
      toast.error("Erro ao atualizar status");
    }
  }

  const filteredFindings = filterSeverity
    ? findings.filter(f => f.severity === filterSeverity)
    : findings;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          {activeRun ? (
            <p className="text-sm text-muted-foreground">
              Última execução: {new Date(activeRun.started_at).toLocaleString("pt-BR")}
              {" · "}{activeRun.total_findings} achado(s)
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">Nenhuma conferência executada ainda</p>
          )}
        </div>
        <div className="flex gap-2">
          {activeRun && (
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/validation-runs/${activeRun.id}/export-xlsx`}
              download
            >
              <Button size="sm" variant="outline">
                <DownloadIcon className="w-3.5 h-3.5 mr-1" />
                Exportar XLSX
              </Button>
            </a>
          )}
          <Button size="sm" onClick={executeConference} disabled={running}>
            <PlayIcon className="w-3.5 h-3.5 mr-1" />
            {running ? "Executando..." : "Executar conferência"}
          </Button>
        </div>
      </div>

      {/* Histórico de execuções */}
      {runs.length > 1 && (
        <div className="flex gap-2 flex-wrap">
          {runs.map(r => (
            <button
              key={r.id}
              onClick={() => loadFindings(r)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                activeRun?.id === r.id
                  ? "bg-foreground text-background border-foreground"
                  : "hover:bg-muted border-input"
              }`}
            >
              {new Date(r.started_at).toLocaleDateString("pt-BR")} — {r.total_findings} achados
            </button>
          ))}
        </div>
      )}

      {/* Cards de resumo */}
      {activeRun && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { key: "critico",               label: "Críticos",     count: activeRun.critical_count },
            { key: "alerta",                label: "Alertas",      count: activeRun.alert_count },
            { key: "divergencia_monetaria", label: "Divergências", count: activeRun.monetary_count },
            { key: "observacao",            label: "Observações",  count: activeRun.observation_count },
          ].map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setFilterSeverity(filterSeverity === key ? "" : key)}
              className={`border rounded-lg p-3 text-left transition-colors hover:bg-muted/50 ${
                filterSeverity === key ? "ring-2 ring-foreground/20 bg-muted/50" : ""
              }`}
            >
              <p className={`text-2xl font-bold ${SEVERITY_CONFIG[key]?.color}`}>{count}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </button>
          ))}
        </div>
      )}

      {/* Tabela de achados */}
      {loading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : !activeRun ? (
        <div className="border-2 border-dashed rounded-lg p-10 text-center text-muted-foreground text-sm">
          Clique em &quot;Executar conferência&quot; para iniciar a análise.
        </div>
      ) : filteredFindings.length === 0 ? (
        <div className="border rounded-lg p-8 text-center text-muted-foreground text-sm">
          {filterSeverity ? "Nenhum achado com este filtro." : "Nenhum achado encontrado."}
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          {filterSeverity && (
            <div className="px-4 py-2 bg-muted/30 border-b text-xs text-muted-foreground flex items-center justify-between">
              <span>Filtrando por: <strong>{SEVERITY_CONFIG[filterSeverity]?.label}</strong> ({filteredFindings.length})</span>
              <button onClick={() => setFilterSeverity("")} className="hover:text-foreground">Limpar filtro ×</button>
            </div>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-28">Severidade</TableHead>
                <TableHead>Achado</TableHead>
                <TableHead className="w-20">Registro</TableHead>
                <TableHead className="w-16">CFOP</TableHead>
                <TableHead className="text-right w-28">EFD</TableHead>
                <TableHead className="text-right w-28">Referência</TableHead>
                <TableHead className="text-right w-28">Diferença</TableHead>
                <TableHead className="w-32">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredFindings.map(f => {
                const sev = SEVERITY_CONFIG[f.severity] ?? { label: f.severity, variant: "outline" as const, color: "" };
                return (
                  <TableRow key={f.id} className={f.status === "resolved" ? "opacity-50" : ""}>
                    <TableCell>
                      <Badge variant={sev.variant} className="text-xs">{sev.label}</Badge>
                    </TableCell>
                    <TableCell>
                      <p className="text-sm font-medium">{f.title}</p>
                      {f.description && (
                        <p className="text-xs text-muted-foreground mt-0.5 max-w-md truncate">{f.description}</p>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{f.register_code ?? "—"}</TableCell>
                    <TableCell className="font-mono text-xs">{f.cfop ?? "—"}</TableCell>
                    <TableCell className="text-right text-xs tabular-nums">
                      {f.efd_value != null ? f.efd_value.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) : "—"}
                    </TableCell>
                    <TableCell className="text-right text-xs tabular-nums">
                      {f.reference_value != null ? f.reference_value.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) : "—"}
                    </TableCell>
                    <TableCell className={`text-right text-xs tabular-nums font-medium ${f.difference_value && f.difference_value > 0 ? "text-red-600" : ""}`}>
                      {f.difference_value != null ? f.difference_value.toLocaleString("pt-BR", { minimumFractionDigits: 2 }) : "—"}
                    </TableCell>
                    <TableCell>
                      {f.status === "open" ? (
                        <div className="flex gap-1">
                          <Button size="sm" variant="outline" className="h-6 text-xs px-2"
                            onClick={() => updateFindingStatus(f.id, "acknowledged")}>Ciente</Button>
                          <Button size="sm" variant="ghost" className="h-6 text-xs px-2"
                            onClick={() => updateFindingStatus(f.id, "resolved")}>Resolver</Button>
                        </div>
                      ) : (
                        <Badge variant="secondary" className="text-xs">
                          {f.status === "acknowledged" ? "Ciente" : "Resolvido"}
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Sugestões de Correção */}
      {activeRun && (
        <SugestoesSection run={activeRun} efdFileId={activeRun.efd_file_id} />
      )}
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────

export default function CompetenciaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [period, setPeriod] = useState<FiscalPeriod | null>(null);
  const [company, setCompany] = useState<Company | null>(null);

  useEffect(() => {
    api.get<FiscalPeriod>(`/api/v1/fiscal-periods/${id}`)
      .then(p => {
        setPeriod(p);
        return api.get<Company>(`/api/v1/companies/${p.company_id}`);
      })
      .then(setCompany)
      .catch(() => toast.error("Erro ao carregar competência"));
  }, [id]);

  if (!period || !company) {
    return <main className="max-w-6xl mx-auto px-6 py-8"><p className="text-muted-foreground text-sm">Carregando...</p></main>;
  }

  return (
    <main className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          <a href="/empresas" className="hover:text-foreground">Empresas</a>
          <span>/</span>
          <a href={`/empresas/${company.id}`} className="hover:text-foreground">{company.name}</a>
          <span>/</span>
          <span>{MESES[period.month - 1]} {period.year}</span>
        </div>
        <h1 className="text-2xl font-bold">
          {MESES[period.month - 1]} / {period.year}
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          {company.name} · CNPJ {company.cnpj}
        </p>
      </div>

      {/* Sprint 8: Score de Risco + Próxima Ação + Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <RiskScoreCard periodId={period.id} />
        <NextActionCard periodId={period.id} />
      </div>
      <div className="mb-6">
        <TimelineCard periodId={period.id} />
      </div>

      <Tabs defaultValue="efd">
        <TabsList>
          <TabsTrigger value="efd">Arquivo EFD</TabsTrigger>
          <TabsTrigger value="pdf">PDF de Apuração</TabsTrigger>
          <TabsTrigger value="referencia">Valores de Referência</TabsTrigger>
          <TabsTrigger value="conferencia">Conferências</TabsTrigger>
        </TabsList>

        <TabsContent value="efd" className="mt-4">
          <EfdTab period={period} />
        </TabsContent>

        <TabsContent value="pdf" className="mt-4">
          <PdfTab period={period} />
        </TabsContent>

        <TabsContent value="referencia" className="mt-4">
          <ApuracaoTab period={period} />
        </TabsContent>

        <TabsContent value="conferencia" className="mt-4">
          <ConferenciaTab period={period} />
        </TabsContent>
      </Tabs>
    </main>
  );
}
