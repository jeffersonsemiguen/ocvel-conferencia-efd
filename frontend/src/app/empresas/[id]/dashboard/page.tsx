"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { ArrowRightIcon, BuildingIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

const MESES = [
  "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
  "Jul", "Ago", "Set", "Out", "Nov", "Dez",
];

interface CompanyInfo {
  id: string;
  name: string;
  cnpj: string;
}

interface PeriodSummary {
  id: string;
  year: number;
  month: number;
  status: string;
  score: number;
  risk_level: string;
  critical_count: number;
  alert_count: number;
  last_run_at: string | null;
}

interface CompanyDashboard {
  company: CompanyInfo;
  summary: {
    total_periods: number;
    open_periods: number;
    periods_with_criticals: number;
    total_criticals: number;
    average_score: number;
  };
  periods: PeriodSummary[];
}

function formatCnpj(cnpj: string) {
  return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

function riskColor(risk: string): string {
  switch (risk) {
    case "low":      return "text-green-600";
    case "moderate": return "text-yellow-600";
    case "high":     return "text-orange-500";
    case "critical": return "text-destructive";
    default:         return "text-muted-foreground";
  }
}

const RISK_LABELS: Record<string, string> = {
  low: "Baixo", moderate: "Moderado", high: "Alto", critical: "Crítico",
};

const STATUS_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  pending:                    { label: "Pendente",          variant: "secondary" },
  processing:                 { label: "Processando",       variant: "outline" },
  completed:                  { label: "Concluído",         variant: "default" },
  error:                      { label: "Erro",              variant: "destructive" },
  open:                       { label: "Aberta",            variant: "secondary" },
  files_uploaded:             { label: "Arquivos enviados", variant: "outline" },
  efd_processed:              { label: "EFD processada",    variant: "outline" },
  apuracao_ready:             { label: "Apuração pronta",   variant: "outline" },
  validated_with_issues:      { label: "Com problemas",     variant: "destructive" },
  validated_without_critical: { label: "Validada",          variant: "default" },
  suggestions_pending:        { label: "Sugestões pendentes", variant: "secondary" },
  correction_generated:       { label: "Correção gerada",   variant: "default" },
  ready_for_pva:              { label: "Pronta para PVA",   variant: "default" },
  closed:                     { label: "Encerrada",         variant: "secondary" },
};

export default function EmpresaDashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [dashboard, setDashboard] = useState<CompanyDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<CompanyDashboard>(`/api/v1/companies/${id}/dashboard`)
      .then(setDashboard)
      .catch(() => toast.error("Erro ao carregar dashboard da empresa"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="max-w-5xl mx-auto px-6 py-8">
        <p className="text-sm text-muted-foreground">Carregando dashboard...</p>
      </main>
    );
  }

  if (!dashboard) {
    return (
      <main className="max-w-5xl mx-auto px-6 py-8">
        <p className="text-sm text-muted-foreground">Empresa não encontrada.</p>
      </main>
    );
  }

  const { company, summary, periods } = dashboard;

  return (
    <main className="max-w-5xl mx-auto px-6 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <a href="/empresas" className="hover:text-foreground">Empresas</a>
        <span>/</span>
        <a href={`/empresas/${company.id}`} className="hover:text-foreground">{company.name}</a>
        <span>/</span>
        <span className="text-foreground">Dashboard</span>
      </div>

      {/* Cabeçalho */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-lg border bg-muted flex items-center justify-center shrink-0">
          <BuildingIcon className="w-5 h-5 text-muted-foreground" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{company.name}</h1>
          <p className="text-sm text-muted-foreground font-mono">{formatCnpj(company.cnpj)}</p>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="border rounded-lg p-4 text-center">
          <p className="text-3xl font-bold">{summary.total_periods}</p>
          <p className="text-xs text-muted-foreground mt-1">Total de competências</p>
        </div>
        <div className="border rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-blue-600">{summary.open_periods}</p>
          <p className="text-xs text-muted-foreground mt-1">Competências abertas</p>
        </div>
        <div className="border rounded-lg p-4 text-center">
          <p className={`text-3xl font-bold ${summary.periods_with_criticals > 0 ? "text-destructive" : "text-green-600"}`}>
            {summary.periods_with_criticals}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Com achados críticos</p>
        </div>
        <div className="border rounded-lg p-4 text-center">
          <p className={`text-3xl font-bold ${
            summary.average_score <= 20 ? "text-green-600" :
            summary.average_score <= 50 ? "text-yellow-600" :
            summary.average_score <= 80 ? "text-orange-500" : "text-destructive"
          }`}>
            {summary.average_score}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Score médio de risco</p>
        </div>
      </div>

      {/* Tabela de competências */}
      <div className="border rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b bg-muted/30">
          <h2 className="text-sm font-semibold">Competências</h2>
        </div>
        {periods.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            Nenhuma competência cadastrada.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/10 text-xs text-muted-foreground">
                <th className="px-4 py-2 text-left font-medium">Competência</th>
                <th className="px-4 py-2 text-left font-medium">Status</th>
                <th className="px-4 py-2 text-center font-medium">Score</th>
                <th className="px-4 py-2 text-center font-medium">Nível</th>
                <th className="px-4 py-2 text-center font-medium">Críticos</th>
                <th className="px-4 py-2 text-center font-medium">Alertas</th>
                <th className="px-4 py-2 text-left font-medium">Última conferência</th>
                <th className="px-4 py-2 w-10" />
              </tr>
            </thead>
            <tbody>
              {periods.map(p => {
                const statusInfo = STATUS_CONFIG[p.status] ?? { label: p.status, variant: "secondary" as const };
                return (
                  <tr key={p.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 font-semibold">
                      {MESES[p.month - 1]} / {p.year}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={statusInfo.variant} className="text-xs">
                        {statusInfo.label}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`font-bold tabular-nums ${riskColor(p.risk_level)}`}>
                        {p.score}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-xs font-medium ${riskColor(p.risk_level)}`}>
                        {RISK_LABELS[p.risk_level] ?? p.risk_level}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {p.critical_count > 0 ? (
                        <span className="text-destructive font-bold">{p.critical_count}</span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {p.alert_count > 0 ? (
                        <span className="text-orange-500 font-medium">{p.alert_count}</span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      {p.last_run_at
                        ? new Date(p.last_run_at).toLocaleDateString("pt-BR")
                        : "Nunca"}
                    </td>
                    <td className="px-4 py-3">
                      <a href={`/competencias/${p.id}`}>
                        <ArrowRightIcon className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors" />
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
