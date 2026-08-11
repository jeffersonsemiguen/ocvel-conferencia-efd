"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import {
  FileTextIcon, UploadIcon, PlusIcon, CheckIcon,
  ChevronDownIcon, ChevronRightIcon, AlertCircleIcon, PlayIcon,
  DownloadIcon, WandSparklesIcon, XIcon, RefreshCwIcon, ClockIcon,
  FileCheckIcon, MergeIcon,
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
  ValidationFinding, ValidationRun, NfeUploadResponse, NfeFinding,
  MergeBlockConfig, MergeResult,
} from "@/lib/types";
import { DEFAULT_MERGE_CONFIG } from "@/lib/types";

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

// ─── Role badges ─────────────────────────────────────────────────────────────

const ROLE_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "outline" }> = {
  empresa:  { label: "SPED Empresa",  variant: "outline" },
  contabil: { label: "SPED Contábil", variant: "secondary" },
  merged:   { label: "Ativo",         variant: "default" },
};

// ─── MergerModal ─────────────────────────────────────────────────────────────

const BLOCOS_CONFIG = ["B","C","D","E","G","H","K","1"] as const;
const BLOCO_NOMES: Record<string, string> = {
  B:"Bloco B", C:"Bloco C", D:"Bloco D", E:"Bloco E",
  G:"Bloco G (CIAP)", H:"Bloco H (Inventário)", K:"Bloco K (Estoque)", "1":"Bloco 1",
};

function readEfdHeader(file: File): Promise<{ cnpj: string; dtIni: string; dtFin: string; nome: string } | null> {
  return new Promise(resolve => {
    const reader = new FileReader();
    reader.onload = e => {
      const text = e.target?.result as string;
      for (const line of text.split(/\r?\n/)) {
        if (line.startsWith("|0000|")) {
          const p = line.split("|");
          resolve({ cnpj: p[7]??'', dtIni: p[4]??'', dtFin: p[5]??'', nome: p[6]??'' });
          return;
        }
      }
      resolve(null);
    };
    reader.readAsText(file, "windows-1252");
  });
}

function MergerModal({ period, onMerged }: { period: FiscalPeriod; onMerged: (f: EfdFile) => void }) {
  const [open, setOpen] = useState(false);
  const [fileEmpresa, setFileEmpresa] = useState<File | null>(null);
  const [fileContabil, setFileContabil] = useState<File | null>(null);
  const [metaEmpresa, setMetaEmpresa] = useState<{ cnpj: string; dtIni: string; dtFin: string; nome: string } | null>(null);
  const [metaContabil, setMetaContabil] = useState<{ cnpj: string; dtIni: string; dtFin: string; nome: string } | null>(null);
  const [config, setConfig] = useState<MergeBlockConfig>({ ...DEFAULT_MERGE_CONFIG });
  const [merging, setMerging] = useState(false);
  const [result, setResult] = useState<MergeResult | null>(null);
  const [compatError, setCompatError] = useState<string | null>(null);

  async function handleFileChange(tipo: "empresa" | "contabil", e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const meta = await readEfdHeader(file);
    if (tipo === "empresa") { setFileEmpresa(file); setMetaEmpresa(meta); }
    else { setFileContabil(file); setMetaContabil(meta); }
  }

  useEffect(() => {
    if (!metaEmpresa || !metaContabil) { setCompatError(null); return; }
    if (metaEmpresa.cnpj !== metaContabil.cnpj)
      setCompatError(`CNPJs diferentes: ${metaEmpresa.cnpj} ≠ ${metaContabil.cnpj}`);
    else if (metaEmpresa.dtIni !== metaContabil.dtIni || metaEmpresa.dtFin !== metaContabil.dtFin)
      setCompatError("Períodos diferentes entre os arquivos");
    else
      setCompatError(null);
  }, [metaEmpresa, metaContabil]);

  async function handleMerge() {
    if (!fileEmpresa || !fileContabil || compatError) return;
    setMerging(true);
    try {
      const formE = new FormData();
      formE.append("file", fileEmpresa);
      const efdE = await api.upload<EfdFile>(`/api/v1/fiscal-periods/${period.id}/efd-files?role=empresa`, formE);

      const formC = new FormData();
      formC.append("file", fileContabil);
      const efdC = await api.upload<EfdFile>(`/api/v1/fiscal-periods/${period.id}/efd-files?role=contabil`, formC);

      const res = await api.post<MergeResult>(
        `/api/v1/fiscal-periods/${period.id}/efd-files/merge`,
        { empresa_file_id: efdE.id, contabil_file_id: efdC.id, block_config: config }
      );
      setResult(res);
      const merged = await api.get<EfdFile>(`/api/v1/efd-files/${res.merged_file_id}`);
      onMerged(merged);
      toast.success(`Arquivo SPED gerado — ${res.total_lines.toLocaleString()} linhas`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro ao mesclar arquivos.");
    } finally {
      setMerging(false);
    }
  }

  const canMerge = fileEmpresa && fileContabil && !compatError && !merging;

  return (
    <>
      <Button size="sm" variant="outline" onClick={() => { setOpen(true); setResult(null); }}>
        <MergeIcon className="w-3.5 h-3.5 mr-1" />
        Mesclar EFDs
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Mesclar EFDs — SPED Empresa + SPED Contábil</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Upload dos dois arquivos */}
            <div className="grid grid-cols-2 gap-3">
              {(["empresa", "contabil"] as const).map(tipo => (
                <div key={tipo} className="rounded border p-3 space-y-2">
                  <p className="text-xs font-medium capitalize">SPED {tipo === "empresa" ? "Empresa" : "Contábil"}</p>
                  <input
                    type="file" accept=".txt,.sped"
                    className="text-xs w-full"
                    onChange={e => handleFileChange(tipo, e)}
                  />
                  {(tipo === "empresa" ? metaEmpresa : metaContabil) && (
                    <p className="text-xs text-muted-foreground">
                      {(tipo === "empresa" ? metaEmpresa : metaContabil)?.nome}<br />
                      CNPJ {(tipo === "empresa" ? metaEmpresa : metaContabil)?.cnpj}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {compatError && (
              <div className="rounded bg-destructive/10 border border-destructive/30 px-3 py-2 text-xs text-destructive">
                {compatError}
              </div>
            )}
            {metaEmpresa && metaContabil && !compatError && (
              <div className="rounded bg-green-50 border border-green-200 px-3 py-2 text-xs text-green-700">
                Arquivos compatíveis — mesma empresa e período
              </div>
            )}

            {/* Configuração de blocos */}
            <div>
              <p className="text-xs font-medium mb-2">Origem por bloco</p>
              <div className="grid grid-cols-2 gap-1">
                {BLOCOS_CONFIG.map(b => (
                  <div key={b} className="flex items-center justify-between rounded border px-2 py-1.5">
                    <span className="text-xs">{BLOCO_NOMES[b]}</span>
                    <div className="flex gap-1">
                      {(["empresa", "contabil"] as const).map(src => (
                        <button
                          key={src}
                          className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                            config[b] === src
                              ? src === "empresa"
                                ? "bg-blue-600 text-white border-blue-600"
                                : "bg-green-700 text-white border-green-700"
                              : "bg-muted text-muted-foreground border-input"
                          }`}
                          onClick={() => setConfig(c => ({ ...c, [b]: src }))}
                        >
                          {src === "empresa" ? "Emp" : "Cont"}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resultado */}
            {result && (
              <div className="rounded bg-muted p-3 space-y-1">
                <p className="text-xs font-medium">Log do merge</p>
                <div className="max-h-32 overflow-y-auto font-mono text-xs text-muted-foreground space-y-0.5">
                  {result.log.map((l, i) => <div key={i}>{l}</div>)}
                  {result.conflicts.map((c, i) => (
                    <div key={`c${i}`} className="text-amber-600">[AVISO] {c}</div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setOpen(false)}>Fechar</Button>
              <Button size="sm" disabled={!canMerge} onClick={handleMerge}>
                {merging ? "Gerando..." : "Gerar Arquivo SPED"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
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
      const efd = await api.upload<EfdFile>(`/api/v1/fiscal-periods/${period.id}/efd-files`, form);
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
        <div className="flex gap-2">
          <MergerModal period={period} onMerged={f => setFiles(p => [f, ...p])} />
          <Button size="sm" variant="outline" onClick={() => inputRef.current?.click()} disabled={uploading}>
            <UploadIcon className="w-3.5 h-3.5 mr-1" />
            {uploading ? "Enviando..." : "Enviar EFD (.txt)"}
          </Button>
          <input ref={inputRef} type="file" accept=".txt,.sped" className="hidden" onChange={handleUpload} />
        </div>
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
                <TableHead>Papel</TableHead>
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
                  <TableCell className="font-mono text-xs max-w-xs truncate">{f.original_filename}</TableCell>
                  <TableCell>
                    <Badge variant={ROLE_CONFIG[f.file_role ?? "merged"]?.variant ?? "outline"}>
                      {ROLE_CONFIG[f.file_role ?? "merged"]?.label ?? f.file_role}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">{f.efd_company_name ?? "—"}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {f.efd_start_date && f.efd_end_date ? `${f.efd_start_date} → ${f.efd_end_date}` : "—"}
                  </TableCell>
                  <TableCell className="text-sm">{f.total_lines?.toLocaleString() ?? "—"}</TableCell>
                  <TableCell><StatusBadge status={f.parse_status} /></TableCell>
                  <TableCell>
                    <div className="flex gap-1">
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
                      <Button
                        size="sm" variant="ghost" className="h-6 text-xs px-2 text-destructive hover:text-destructive"
                        onClick={async () => {
                          if (!confirm(`Excluir "${f.original_filename}"? Esta ação remove o arquivo e todos os dados processados.`)) return;
                          try {
                            await api.delete(`/api/v1/efd-files/${f.id}`);
                            setFiles(prev => prev.filter(x => x.id !== f.id));
                            toast.success("Arquivo excluído");
                          } catch { toast.error("Erro ao excluir arquivo"); }
                        }}
                      >
                        <XIcon className="h-3 w-3" />
                      </Button>
                    </div>
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
      const pdf = await api.upload<PdfApuracaoFile>(`/api/v1/fiscal-periods/${period.id}/pdf-apuracao-files`, form);
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
      const data = await api.upload<{ rows_imported: number; rows_skipped: number; errors: string[] }>(
        `/api/v1/fiscal-periods/${period.id}/apuracao-reference/import-spreadsheet`,
        form
      );
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
      await api.delete(`/api/v1/apuracao-reference-values/${id}`);
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

  const pending = suggestions.filter(s => s.status === "pending" && s.source !== "c190_correcao");
  const approved = suggestions.filter(s => s.status === "approved" && s.source !== "c190_correcao");
  const rejected = suggestions.filter(s => s.status === "rejected" && s.source !== "c190_correcao");
  const hasSuggestions = pending.length > 0 || approved.length > 0 || rejected.length > 0;

  // Grupos C190×C100
  const c190Sugs = suggestions.filter(s => s.source === "c190_correcao");
  const c190Groups = (() => {
    const map = new Map<string, { cfop: string | null; cst: string | null; original: string; suggested: string; items: CorrectionSuggestion[] }>();
    for (const s of c190Sugs) {
      const key = `${s.cfop ?? ""}|${s.cst ?? ""}|${s.original_value}|${s.suggested_value}`;
      if (!map.has(key)) map.set(key, { cfop: s.cfop ?? null, cst: s.cst ?? null, original: s.original_value ?? "", suggested: s.suggested_value, items: [] });
      map.get(key)!.items.push(s);
    }
    return [...map.values()];
  })();

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
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs"
                      onClick={() =>
                        api.download(
                          `/api/v1/corrected-files/${cf.id}/download`,
                          cf.generated_filename
                        ).catch(() => toast.error("Erro ao baixar arquivo."))
                      }
                    >
                      <DownloadIcon className="w-3 h-3 mr-1" />Download
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Painel C190×C100 — grupos de correção */}
      {c190Groups.length > 0 && (
        <C190CorrectionPanel
          groups={c190Groups}
          efdFileId={efdFileId}
          onApproved={(ids) =>
            setSuggestions(prev => prev.map(s => ids.includes(s.id) ? { ...s, status: "approved" } : s))
          }
          onReverted={(orig, sugg) =>
            setSuggestions(prev => prev.map(s =>
              s.source === "c190_correcao" && s.original_value === orig && s.suggested_value === sugg
                ? { ...s, status: "pending", approved_by: null, approved_at: null }
                : s
            ))
          }
        />
      )}
    </div>
  );
}

// ─── C190 Correction Panel ────────────────────────────────────────────────────

function C190CorrectionPanel({
  groups, efdFileId, onApproved, onReverted,
}: {
  groups: { cfop: string | null; cst: string | null; original: string; suggested: string; items: CorrectionSuggestion[] }[];
  efdFileId: string;
  onApproved: (ids: string[]) => void;
  onReverted: (original: string, suggested: string) => void;
}) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    groups.forEach(g => g.items.forEach(s => { init[s.id] = s.status === "pending"; }));
    return init;
  });
  const [approving, setApproving] = useState<string | null>(null);
  const [reverting, setReverting] = useState<string | null>(null);

  function toggleGroup(idx: number, allChecked: boolean) {
    const ids = groups[idx].items.map(s => s.id);
    setChecked(c => { const n = { ...c }; ids.forEach(id => { n[id] = !allChecked; }); return n; });
  }

  async function confirmGroup(idx: number) {
    const g = groups[idx];
    const ids = g.items.filter(s => checked[s.id] && s.status === "pending").map(s => s.id);
    if (!ids.length) return;
    const key = `${g.original}|${g.suggested}`;
    setApproving(key);
    try {
      await api.post("/api/v1/correction-suggestions/bulk-approve", { suggestion_ids: ids });
      onApproved(ids);
      toast.success(`${ids.length} correção(ões) C190 aprovada(s)`);
    } catch { toast.error("Erro ao aprovar correções C190"); }
    finally { setApproving(null); }
  }

  async function revertGroup(idx: number) {
    const g = groups[idx];
    const key = `${g.original}|${g.suggested}`;
    setReverting(key);
    try {
      const res = await api.post<{ reverted_count: number }>("/api/v1/correction-suggestions/revert-batch", {
        efd_file_id: efdFileId,
        rule_code: "CONF-C190-C100",
        original_value: g.original,
        suggested_value: g.suggested,
      });
      onReverted(g.original, g.suggested);
      toast.success(`${res.reverted_count} correção(ões) revertida(s)`);
    } catch { toast.error("Erro ao reverter correções C190"); }
    finally { setReverting(null); }
  }

  return (
    <div className="border-t">
      <div className="px-4 py-2 bg-blue-50/40">
        <p className="text-xs font-semibold text-blue-700">
          Correções C190×C100 — {groups.length} grupo(s) com divergência de vl_opr
        </p>
      </div>
      {groups.map((g, idx) => {
        const key = `${g.original}|${g.suggested}`;
        const isExpanded = expanded[idx] ?? false;
        const pending = g.items.filter(s => s.status === "pending");
        const approvedCount = g.items.filter(s => s.status === "approved").length;
        const allChecked = pending.every(s => checked[s.id]);
        const checkedIds = pending.filter(s => checked[s.id]).map(s => s.id);

        return (
          <div key={idx} className="border-b last:border-b-0">
            <div
              className="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-muted/20"
              onClick={() => setExpanded(e => ({ ...e, [idx]: !isExpanded }))}
            >
              <div className="flex items-center gap-2">
                {isExpanded ? <ChevronDownIcon className="w-3.5 h-3.5" /> : <ChevronRightIcon className="w-3.5 h-3.5" />}
                <input
                  type="checkbox"
                  checked={allChecked && pending.length > 0}
                  onChange={() => toggleGroup(idx, allChecked)}
                  onClick={e => e.stopPropagation()}
                  className="h-3.5 w-3.5"
                />
                <span className="text-xs font-medium">
                  CFOP {g.cfop ?? "?"} / CST {g.cst ?? "?"}
                </span>
                <span className="text-xs text-muted-foreground">
                  {pending.length} pendente(s)
                  {approvedCount > 0 && ` · ${approvedCount} aprovada(s)`}
                </span>
                <span className="text-xs text-destructive font-mono">
                  R$ {parseFloat(g.original).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </span>
                <span className="text-xs">→</span>
                <span className="text-xs text-green-700 font-mono">
                  R$ {parseFloat(g.suggested).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                <Button size="sm" variant="outline" className="h-6 text-xs px-2"
                  disabled={!checkedIds.length || approving === key}
                  onClick={() => confirmGroup(idx)}>
                  {approving === key ? "..." : "Confirmar"}
                </Button>
                <Button size="sm" variant="ghost" className="h-6 text-xs px-2 text-muted-foreground"
                  disabled={!approvedCount || reverting === key}
                  onClick={() => revertGroup(idx)}>
                  {reverting === key ? "..." : "Reverter"}
                </Button>
              </div>
            </div>

            {isExpanded && (
              <div className="px-10 pb-2 space-y-1">
                {g.items.map(s => (
                  <div key={s.id} className="flex items-center gap-2 text-xs py-0.5">
                    <input
                      type="checkbox"
                      checked={!!checked[s.id]}
                      disabled={s.status !== "pending"}
                      onChange={() => setChecked(c => ({ ...c, [s.id]: !c[s.id] }))}
                      className="h-3 w-3"
                    />
                    <span className="font-mono text-muted-foreground">linha {s.line_number}</span>
                    <Badge variant={s.status === "approved" ? "default" : "outline"} className="text-xs py-0">
                      {s.status === "approved" ? "Aprovado" : "Pendente"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
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

// ─── Aba Relatório CFOP ───────────────────────────────────────────────────────

interface CfopC190Row { cfop: string; vl_opr: number; vl_bc_icms: number; vl_icms: number; vl_icms_st: number; vl_ipi: number }
interface CfopC170Row { cfop: string; vl_item: number; vl_opr: number; vl_bc_icms: number; vl_icms: number }
interface CfopD190Row { cfop: string; vl_opr: number; vl_bc_icms: number; vl_icms: number }

function fmtCfop(cfop: string): string {
  return cfop.length === 4 ? `${cfop[0]}.${cfop.slice(1)}` : cfop;
}

function fmtBRL(v: number): string {
  return v === 0 ? "—" : v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function sum(rows: { [k: string]: number }[], key: string): number {
  return rows.reduce((acc, r) => acc + (r[key] ?? 0), 0);
}

function CfopSectionRows({ rows, keys }: {
  rows: Record<string, number>[];
  keys: { field: string; label: string }[];
}) {
  const entradas = rows.filter(r => ["1","2","3"].includes((r.cfop as string)?.[0]));
  const saidas   = rows.filter(r => ["5","6","7"].includes((r.cfop as string)?.[0]));

  function subtotalRow(label: string, subset: Record<string, number>[]) {
    return (
      <TableRow key={label} className="bg-blue-50 dark:bg-blue-950/20 font-semibold">
        <TableCell className="text-blue-700 dark:text-blue-400">{label}</TableCell>
        {keys.map(k => (
          <TableCell key={k.field} className="text-right font-mono text-blue-700 dark:text-blue-400">
            {fmtBRL(sum(subset, k.field))}
          </TableCell>
        ))}
      </TableRow>
    );
  }

  return (
    <>
      {/* Entradas */}
      {entradas.length > 0 && (
        <TableRow className="bg-muted/30">
          <TableCell colSpan={keys.length + 1} className="text-xs font-semibold text-muted-foreground uppercase tracking-wide py-1">
            Entradas (1xx / 2xx / 3xx)
          </TableCell>
        </TableRow>
      )}
      {entradas.map(r => (
        <TableRow key={r.cfop as string}>
          <TableCell className="font-mono font-medium">{fmtCfop(r.cfop as string)}</TableCell>
          {keys.map(k => (
            <TableCell key={k.field} className="text-right font-mono">{fmtBRL(r[k.field])}</TableCell>
          ))}
        </TableRow>
      ))}
      {entradas.length > 0 && subtotalRow("Subtotal Entradas", entradas)}

      {/* Saídas */}
      {saidas.length > 0 && (
        <TableRow className="bg-muted/30">
          <TableCell colSpan={keys.length + 1} className="text-xs font-semibold text-muted-foreground uppercase tracking-wide py-1">
            Saídas (5xx / 6xx / 7xx)
          </TableCell>
        </TableRow>
      )}
      {saidas.map(r => (
        <TableRow key={r.cfop as string}>
          <TableCell className="font-mono font-medium">{fmtCfop(r.cfop as string)}</TableCell>
          {keys.map(k => (
            <TableCell key={k.field} className="text-right font-mono">{fmtBRL(r[k.field])}</TableCell>
          ))}
        </TableRow>
      ))}
      {saidas.length > 0 && subtotalRow("Subtotal Saídas", saidas)}

      {/* Total geral */}
      {rows.length > 0 && (
        <TableRow className="bg-muted/60 font-bold border-t-2">
          <TableCell>Total Geral</TableCell>
          {keys.map(k => (
            <TableCell key={k.field} className="text-right font-mono">{fmtBRL(sum(rows, k.field))}</TableCell>
          ))}
        </TableRow>
      )}
    </>
  );
}

function RelatorioCfopTab({ period }: { period: FiscalPeriod }) {
  const [files, setFiles] = useState<EfdFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string>("");
  const [c190, setC190] = useState<CfopC190Row[]>([]);
  const [c170, setC170] = useState<CfopC170Row[]>([]);
  const [d190, setD190] = useState<CfopD190Row[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [view, setView] = useState<"c190" | "c170" | "d190">("c190");

  useEffect(() => {
    api.get<EfdFile[]>(`/api/v1/fiscal-periods/${period.id}/efd-files`)
      .then(fs => {
        setFiles(fs);
        const active = fs.find(f => f.parse_status === "parsed") ?? fs[0];
        if (active) setSelectedFileId(active.id);
      })
      .finally(() => setLoadingFiles(false));
  }, [period.id]);

  useEffect(() => {
    if (!selectedFileId) return;
    setLoading(true);
    api.get<{ c190: CfopC190Row[]; c170: CfopC170Row[] }>(
      `/api/v1/efd-files/${selectedFileId}/relatorio/cfop-totals`
    )
      .then(d => { setC190(d.c190); setC170(d.c170); setD190(d.d190 ?? []); })
      .catch(() => toast.error("Erro ao carregar relatório"))
      .finally(() => setLoading(false));
  }, [selectedFileId]);

  if (loadingFiles) return <p className="text-muted-foreground text-sm">Carregando...</p>;
  if (files.length === 0) return <p className="text-muted-foreground text-sm">Nenhum arquivo EFD processado.</p>;

  const c190Keys = [
    { field: "vl_opr",      label: "Operação (R$)" },
    { field: "vl_bc_icms",  label: "Base Calc. ICMS (R$)" },
    { field: "vl_icms",     label: "ICMS (R$)" },
    { field: "vl_icms_st",  label: "ST (R$)" },
    { field: "vl_ipi",      label: "IPI (R$)" },
  ];
  const c170Keys = [
    { field: "vl_item",    label: "Valor Item (R$)" },
    { field: "vl_opr",     label: "Operação (R$)" },
    { field: "vl_bc_icms", label: "Base Calc. ICMS (R$)" },
    { field: "vl_icms",    label: "ICMS (R$)" },
  ];

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Botões C190 / C170 */}
        <div className="flex rounded-md border overflow-hidden">
          <button
            onClick={() => setView("c190")}
            className={`px-4 py-1.5 text-sm font-medium transition-colors ${view === "c190" ? "bg-primary text-primary-foreground" : "bg-background hover:bg-muted"}`}
          >
            C190 — Analítico
          </button>
          <button
            onClick={() => setView("c170")}
            className={`px-4 py-1.5 text-sm font-medium transition-colors border-l ${view === "c170" ? "bg-primary text-primary-foreground" : "bg-background hover:bg-muted"}`}
          >
            C170 — Itens
          </button>
          <button
            onClick={() => setView("d190")}
            className={`px-4 py-1.5 text-sm font-medium transition-colors border-l ${view === "d190" ? "bg-primary text-primary-foreground" : "bg-background hover:bg-muted"}`}
          >
            D190 — CT-e
          </button>
        </div>

        {/* Seletor de arquivo */}
        {files.length > 1 && (
          <select
            className="border rounded px-2 py-1.5 text-sm bg-background"
            value={selectedFileId}
            onChange={e => setSelectedFileId(e.target.value)}
          >
            {files.map(f => (
              <option key={f.id} value={f.id}>{f.original_filename}</option>
            ))}
          </select>
        )}

        {loading && <span className="text-muted-foreground text-sm">Carregando...</span>}
      </div>

      {/* Tabela C190 */}
      {view === "c190" && (
        <div>
          <h3 className="font-semibold mb-2 text-sm">Registros C190 — Analítico por CFOP</h3>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">CFOP</TableHead>
                  {c190Keys.map(k => (
                    <TableHead key={k.field} className="text-right">{k.label}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {c190.length === 0 && !loading
                  ? <TableRow><TableCell colSpan={6} className="text-center text-muted-foreground">Sem registros C190</TableCell></TableRow>
                  : <CfopSectionRows rows={c190 as never[]} keys={c190Keys} />
                }
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {/* Tabela C170 */}
      {view === "c170" && (
        <div>
          <h3 className="font-semibold mb-2 text-sm">Registros C170 — Itens por CFOP</h3>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">CFOP</TableHead>
                  {c170Keys.map(k => (
                    <TableHead key={k.field} className="text-right">{k.label}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {c170.length === 0 && !loading
                  ? <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground">Sem registros C170 (re-parse necessário se o arquivo for antigo)</TableCell></TableRow>
                  : <CfopSectionRows rows={c170 as never[]} keys={c170Keys} />
                }
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {/* Tabela D190 — CT-e */}
      {view === "d190" && (
        <div>
          <h3 className="font-semibold mb-2 text-sm">Registros D190 — CT-e por CFOP</h3>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">CFOP</TableHead>
                  <TableHead className="text-right">Operação (R$)</TableHead>
                  <TableHead className="text-right">Base Calc. ICMS (R$)</TableHead>
                  <TableHead className="text-right">ICMS (R$)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {d190.length === 0 && !loading
                  ? <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground">Sem registros D190 (arquivo sem CT-e ou re-parse necessário)</TableCell></TableRow>
                  : <CfopSectionRows rows={d190 as never[]} keys={[
                      { field: "vl_opr",     label: "Operação (R$)" },
                      { field: "vl_bc_icms", label: "Base Calc. ICMS (R$)" },
                      { field: "vl_icms",    label: "ICMS (R$)" },
                    ]} />
                }
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Findings agrupados ───────────────────────────────────────────────────────

const RULE_LABELS: Record<string, string> = {
  "CONF-C190-C100":             "C190 × C100 — Totalizadores divergentes",
  "CONF-C190-VL-OPR":          "C190 × Referência — Valor contábil",
  "CONF-C190-BC-ICMS":         "C190 × Referência — Base ICMS",
  "CONF-C190-ICMS":            "C190 × Referência — ICMS",
  "CONF-C190-ICMS-ST":         "C190 × Referência — ICMS-ST",
  "CONF-C190-IPI":             "C190 × Referência — IPI",
  "CONF-C190-AUSENCIA-EFD":    "C190 — CFOP/CST sem registro no TXT",
  "CONF-C190-SEM-REFERENCIA":  "C190 — CFOP/CST sem referência de apuração",
  "CONF-CFOP-CST":             "CFOP × CST — Combinação incompatível",
  "CONF-E110-VL_ICMS_RECOLHER":"E110 — ICMS a recolher divergente",
  "CONF-E110-VL_TOT_DEBITOS":  "E110 — Total débitos divergente",
  "CONF-E110-AUSENTE":         "E110 — Registro ausente no TXT",
  "CONF-E110-SEM-REFERENCIA":  "E110 — Sem referência de apuração",
  "CONF-E520-SALDO":           "E520 — Saldo IPI divergente",
  "CONF-E520-DEBITOS":         "E520 — Débitos IPI divergentes",
  "CONF-E520-AUSENTE":         "E520 — Registro ausente no TXT",
  "CONF-E510-IPI":             "E510 — Consolidação IPI divergente",
  "CONF-REF-PENDENTE":         "Referências não revisadas",
  "REGRA-PR-001":              "PR — Código de ajuste inexistente",
  "REGRA-PR-002":              "PR — Código fora do período de vigência",
  "REGRA-PR-003":              "PR — Register E111 incorreto",
  "REGRA-PR-004":              "PR — E112 exigido mas ausente",
  "REGRA-PR-005":              "PR — E113 exigido mas ausente",
  "REGRA-PR-006":              "PR — Processo exigido mas ausente",
  "REGRA-PR-007":              "PR — Documento fiscal não encontrado em C100",
  "REGRA-PR-008":              "PR — E113 sem dados mínimos",
  "REGRA-PR-009":              "PR — IE auxiliar exigida mas não cadastrada",
  "REGRA-PR-010":              "PR — Valor de ajuste zero",
  "CONF-PR-SEM-TABELA":        "PR — Tabela 5.1.1 não carregada",
  "REGRA-CAD-001":             "Participante sem cadastro em 0150",
  "REGRA-PART-001":            "Item sem cadastro em 0200 (via E113)",
  "REGRA-ITEM-C170":           "Item de NF (C170) sem cadastro no 0200",
  "REGRA-H-001":               "Bloco H — Inventário sem itens H010",
  "REGRA-H-002":               "Bloco H — Total H005 diverge dos itens H010",
  "STRUCT-K":                  "Estrutural — Bloco K obrigatório ausente",
  "STRUCT-H":                  "Estrutural — Bloco H obrigatório ausente",
  "STRUCT-G":                  "Estrutural — Bloco G obrigatório ausente",
  "CONF-C170-SEQ":             "C170 — NUM_ITEM fora de sequência",
  "REGRA-DF02A":               "DF02A — NF papel de emissão própria",
  "REGRA-DF02B":               "DF02B — NF papel entrada (emitente PR)",
  "REGRA-DF02C":               "DF02C — NF papel entrada (outro estado)",
  "REGRA-DF02D":               "DF02D — NF energia elétrica modelo 06",
  "REGRA-DF08":                "DF08 — Chave NF-e duplicada no arquivo",
  "REGRA-DF03A":               "DF03A — Autorizada na EFD, cancelada na SEFAZ",
  "REGRA-DF03B":               "DF03B — Cancelada na EFD, autorizada na SEFAZ",
  "REGRA-DF06A":               "DF06A — Destinatário divergente EFD × NF-e",
  "REGRA-AJDF01":              "AJDF01 — Ajuste sem documentos E113",
  "REGRA-AJCP01":              "AJCP01 — Ajuste PR020021 sem CIAP (Bloco G)",
  "REGRA-CFOP-CST-001":        "Matriz CFOP×CST — Combinação sem regra",
  "REGRA-CFOP-CST-002":        "Matriz CFOP×CST — Alerta de combinação",
  "REGRA-CFOP-CST-003":        "Matriz CFOP×CST — Combinação bloqueada",
};

const SEV_ORDER: Record<string, number> = {
  critico: 4, divergencia_monetaria: 3, alerta: 2, observacao: 1,
};

interface FindingGroup {
  rule_code: string;
  label: string;
  severity: string;
  count: number;
  openCount: number;
  findings: ValidationFinding[];
}

function groupFindingsByRule(findings: ValidationFinding[]): FindingGroup[] {
  const map = new Map<string, FindingGroup>();
  for (const f of findings) {
    if (!map.has(f.rule_code)) {
      map.set(f.rule_code, {
        rule_code: f.rule_code,
        label: RULE_LABELS[f.rule_code] ?? f.rule_code,
        severity: f.severity,
        count: 0,
        openCount: 0,
        findings: [],
      });
    }
    const g = map.get(f.rule_code)!;
    g.count++;
    if (f.status === "open") g.openCount++;
    g.findings.push(f);
    if ((SEV_ORDER[f.severity] ?? 0) > (SEV_ORDER[g.severity] ?? 0)) g.severity = f.severity;
  }
  return Array.from(map.values()).sort((a, b) => {
    const d = (SEV_ORDER[b.severity] ?? 0) - (SEV_ORDER[a.severity] ?? 0);
    return d !== 0 ? d : b.count - a.count;
  });
}

function FindingGroups({
  groups,
  expandedGroups,
  toggleGroup,
  updateStatus,
}: {
  groups: FindingGroup[];
  expandedGroups: Set<string>;
  toggleGroup: (code: string) => void;
  updateStatus: (id: string, status: "acknowledged" | "resolved") => void;
}) {
  return (
    <div className="space-y-2">
      {groups.map(g => {
        const isOpen = expandedGroups.has(g.rule_code);
        const sev = SEVERITY_CONFIG[g.severity] ?? { label: g.severity, variant: "outline" as const, color: "" };
        return (
          <div key={g.rule_code} className="border rounded-lg overflow-hidden">
            {/* Group header */}
            <button
              onClick={() => toggleGroup(g.rule_code)}
              className="w-full flex items-center justify-between px-4 py-2.5 bg-muted/30 hover:bg-muted/50 transition-colors text-left"
            >
              <div className="flex items-center gap-3 min-w-0">
                {isOpen
                  ? <ChevronDownIcon className="w-4 h-4 shrink-0 text-muted-foreground" />
                  : <ChevronRightIcon className="w-4 h-4 shrink-0 text-muted-foreground" />
                }
                <Badge variant={sev.variant} className="text-xs shrink-0">{sev.label}</Badge>
                <span className="text-sm font-medium truncate">{g.label}</span>
                <span className="text-xs text-muted-foreground font-mono shrink-0">{g.rule_code}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-4">
                {g.openCount > 0 && (
                  <span className="text-xs bg-primary/10 text-primary font-semibold px-2 py-0.5 rounded-full">
                    {g.openCount} abertos
                  </span>
                )}
                <span className="text-xs text-muted-foreground">{g.count} total</span>
              </div>
            </button>

            {/* Group rows */}
            {isOpen && (
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/10">
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
                  {g.findings.map(f => {
                    const fs = SEVERITY_CONFIG[f.severity] ?? { label: f.severity, variant: "outline" as const, color: "" };
                    return (
                      <TableRow key={f.id} className={f.status === "resolved" ? "opacity-50" : ""}>
                        <TableCell>
                          <Badge variant={fs.variant} className="text-xs">{fs.label}</Badge>
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
                                onClick={() => updateStatus(f.id, "acknowledged")}>Ciente</Button>
                              <Button size="sm" variant="ghost" className="h-6 text-xs px-2"
                                onClick={() => updateStatus(f.id, "resolved")}>Resolver</Button>
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
            )}
          </div>
        );
      })}
    </div>
  );
}

function ConferenciaTab({ period }: { period: FiscalPeriod }) {
  const [runs, setRuns] = useState<ValidationRun[]>([]);
  const [activeRun, setActiveRun] = useState<ValidationRun | null>(null);
  const [findings, setFindings] = useState<ValidationFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState("");
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  function toggleGroup(code: string) {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      next.has(code) ? next.delete(code) : next.add(code);
      return next;
    });
  }

  function expandAll(codes: string[]) {
    setExpandedGroups(new Set(codes));
  }

  function collapseAll() {
    setExpandedGroups(new Set());
  }

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

  const groups = groupFindingsByRule(filteredFindings);

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

      {/* Achados agrupados */}
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
        <div className="space-y-2">
          {/* Barra de controle dos grupos */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {groups.length} tipo(s) de verificação · {filteredFindings.length} achado(s)
              {filterSeverity && <> · filtro: <strong>{SEVERITY_CONFIG[filterSeverity]?.label}</strong> <button onClick={() => setFilterSeverity("")} className="underline hover:text-foreground ml-1">limpar</button></>}
            </span>
            <div className="flex gap-2">
              <button onClick={() => expandAll(groups.map(g => g.rule_code))} className="hover:text-foreground underline">
                Expandir tudo
              </button>
              <span>·</span>
              <button onClick={collapseAll} className="hover:text-foreground underline">
                Recolher tudo
              </button>
            </div>
          </div>

          <FindingGroups
            groups={groups}
            expandedGroups={expandedGroups}
            toggleGroup={toggleGroup}
            updateStatus={updateFindingStatus}
          />
        </div>
      )}

      {/* Sugestões de Correção */}
      {activeRun && (
        <SugestoesSection run={activeRun} efdFileId={activeRun.efd_file_id} />
      )}
    </div>
  );
}

// ─── Aba NF-e XML ─────────────────────────────────────────────────────────────

const NFE_SEVERITY_BADGE: Record<string, string> = {
  critico: "destructive",
  alerta: "warning",
  divergencia_monetaria: "secondary",
  observacao: "outline",
};

function nfeSeverityLabel(s: string): string {
  const map: Record<string, string> = {
    critico: "Crítico", alerta: "Alerta",
    divergencia_monetaria: "Monetário", observacao: "Observação",
  };
  return map[s] ?? s;
}

function groupNfeByRuleAndCst(findings: NfeFinding[]) {
  const groups: Record<string, { rule_code: string; original_value: string; suggested_value: string; count: number }> = {};
  for (const f of findings) {
    if (f.rule_code !== "CONF-NFE-CST-DIVERGENTE") continue;
    const orig = f.efd_value != null ? String(Math.round(f.efd_value)) : "";
    const sugg = f.reference_value != null ? String(Math.round(f.reference_value)) : "";
    const key = `${f.rule_code}|${orig}|${sugg}`;
    if (!groups[key]) groups[key] = { rule_code: f.rule_code, original_value: orig, suggested_value: sugg, count: 0 };
    groups[key].count += 1;
  }
  return Object.values(groups);
}

function NfeTab({ period }: { period: FiscalPeriod }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<NfeUploadResponse | null>(null);
  const [findings, setFindings] = useState<NfeFinding[]>([]);
  const [approvingKey, setApprovingKey] = useState<string | null>(null);

  const loadFindings = useCallback(async () => {
    try {
      const found = await api.get<NfeFinding[]>(`/api/v1/fiscal-periods/${period.id}/nfe/findings`);
      setFindings(found);
    } catch { /* silently */ }
  }, [period.id]);

  useEffect(() => { loadFindings(); }, [loadFindings]);

  const handleUpload = useCallback(async () => {
    const files = fileInputRef.current?.files;
    if (!files || files.length === 0) { toast.error("Selecione um ou mais arquivos XML ou ZIP."); return; }
    setUploading(true);
    try {
      const form = new FormData();
      for (const file of Array.from(files)) form.append("files", file);
      const result = await api.upload<NfeUploadResponse>(`/api/v1/fiscal-periods/${period.id}/nfe/upload`, form);
      setSummary(result);
      toast.success(`Upload concluído: ${result.autorizadas} autorizadas, ${result.canceladas} canceladas.`);
      await loadFindings();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro no upload.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }, [period.id, loadFindings]);

  const handleRerun = useCallback(async () => {
    try {
      await api.post(`/api/v1/fiscal-periods/${period.id}/nfe/run-crosscheck`, {});
      await loadFindings();
      toast.success("Cross-check re-executado.");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro ao re-executar.");
    }
  }, [period.id, loadFindings]);

  const handleBatchApprove = useCallback(async (rule_code: string, original_value: string, suggested_value: string) => {
    const key = `${rule_code}|${original_value}|${suggested_value}`;
    setApprovingKey(key);
    try {
      const result = await api.post<{ approved_count: number }>(
        `/api/v1/fiscal-periods/${period.id}/nfe/apply-suggestions-batch`,
        { rule_code, original_value, suggested_value }
      );
      toast.success(`${result.approved_count} sugestão(ões) aprovada(s) em lote.`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro na aprovação em lote.");
    } finally {
      setApprovingKey(null);
    }
  }, [period.id]);

  const cstGroups = groupNfeByRuleAndCst(findings);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Cruzamento de XMLs autorizados pela SEFAZ com os lançamentos da EFD.
        </p>
        <Button variant="outline" size="sm" onClick={handleRerun}>
          <PlayIcon className="mr-2 h-4 w-4" />
          Re-executar cross-check
        </Button>
      </div>

      <div className="rounded-lg border p-4 space-y-3">
        <p className="text-sm font-medium">Upload de XMLs ou ZIP</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xml,.zip"
          multiple
          className="block text-sm text-muted-foreground file:mr-3 file:rounded file:border file:px-3 file:py-1 file:text-sm"
        />
        <Button onClick={handleUpload} disabled={uploading}>
          <UploadIcon className="mr-2 h-4 w-4" />
          {uploading ? "Enviando..." : "Enviar e conferir"}
        </Button>
      </div>

      {summary && (
        <div className="grid grid-cols-5 gap-3 text-center">
          {[
            { label: "Total", value: summary.total },
            { label: "Autorizadas", value: summary.autorizadas },
            { label: "Canceladas", value: summary.canceladas },
            { label: "Denegadas", value: summary.denegadas },
            { label: "Erros", value: summary.parsed_error },
          ].map(({ label, value }) => (
            <div key={label} className="rounded border p-3">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-xl font-semibold">{value}</p>
            </div>
          ))}
        </div>
      )}

      {cstGroups.length > 0 && (
        <div className="rounded-lg border p-4 space-y-3">
          <p className="text-sm font-medium">Aprovação em lote — CST divergente</p>
          <div className="space-y-2">
            {cstGroups.map((g) => {
              const key = `${g.rule_code}|${g.original_value}|${g.suggested_value}`;
              return (
                <div key={key} className="flex items-center justify-between rounded border px-3 py-2">
                  <span className="text-sm">
                    CST {g.original_value} → {g.suggested_value}
                    <span className="ml-2 text-muted-foreground">({g.count} ocorrência(s))</span>
                  </span>
                  <Button size="sm" variant="outline" disabled={approvingKey === key}
                    onClick={() => handleBatchApprove(g.rule_code, g.original_value, g.suggested_value)}>
                    <CheckIcon className="mr-1 h-4 w-4" />
                    {approvingKey === key ? "Aprovando..." : "Aprovar lote"}
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {findings.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">{findings.length} finding(s) NF-e encontrado(s)</p>
          <div className="rounded-lg border overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Severidade</TableHead>
                  <TableHead>Regra</TableHead>
                  <TableHead>Título</TableHead>
                  <TableHead>Operação</TableHead>
                  <TableHead>Descrição</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {findings.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell>
                      <Badge variant={(NFE_SEVERITY_BADGE[f.severity] ?? "outline") as "default" | "destructive" | "outline" | "secondary"}>
                        {nfeSeverityLabel(f.severity)}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{f.rule_code}</TableCell>
                    <TableCell className="text-sm">{f.title}</TableCell>
                    <TableCell className="text-xs capitalize">{f.operation_type ?? "—"}</TableCell>
                    <TableCell className="text-xs text-muted-foreground max-w-xs truncate">{f.description ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {findings.length === 0 && (
        <div className="border-2 border-dashed rounded-lg p-10 text-center text-muted-foreground text-sm">
          Nenhum finding NF-e. Envie os XMLs da competência para iniciar o cruzamento.
        </div>
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
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">
            {MESES[period.month - 1]} / {period.year}
          </h1>
          <Link href={`/competencias/${period.id}/correcoes`}>
            <Button variant="outline" size="sm">
              <FileCheckIcon className="mr-2 h-4 w-4" />
              TXT Corrigido
            </Button>
          </Link>
        </div>
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
          <TabsTrigger value="nfe">NF-e XML</TabsTrigger>
          <TabsTrigger value="relatorio">Relatório CFOP</TabsTrigger>
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

        <TabsContent value="nfe" className="mt-4">
          <NfeTab period={period} />
        </TabsContent>

        <TabsContent value="relatorio" className="mt-4">
          <RelatorioCfopTab period={period} />
        </TabsContent>
      </Tabs>
    </main>
  );
}
