"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const MONTHS = [
  "", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
  "Jul", "Ago", "Set", "Out", "Nov", "Dez",
];

interface RunSummary {
  id: string;
  total_findings: number;
  critical_count: number;
  alert_count: number;
  monetary_count: number;
  observation_count: number;
  started_at: string | null;
}

interface PeriodRow {
  id: string;
  year: number;
  month: number;
  status: string;
  has_efd: boolean;
  efd_parse_status: string | null;
  latest_run: RunSummary | null;
}

interface CompanyRow {
  id: string;
  name: string;
  trade_name: string | null;
  cnpj: string;
  state: string | null;
  periods: PeriodRow[];
  period_count: number;
  critical_count: number;
  alert_count: number;
}

interface DashboardData {
  summary: {
    total_companies: number;
    total_periods: number;
    total_critical: number;
    total_alert: number;
  };
  companies: CompanyRow[];
}

function SummaryCard({
  label,
  value,
  variant = "default",
}: {
  label: string;
  value: number;
  variant?: "default" | "critical" | "alert" | "ok";
}) {
  const colors = {
    default: "bg-card border text-card-foreground",
    critical: "bg-destructive text-destructive-foreground",
    alert: "bg-primary text-primary-foreground",
    ok: "bg-card border text-card-foreground",
  };
  return (
    <div className={`rounded-lg p-5 ${colors[variant]}`}>
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}

function SeverityBadge({ count, variant }: { count: number; variant: "critical" | "alert" | "monetary" | "obs" }) {
  if (count === 0) return null;
  const styles = {
    critical: "bg-destructive text-destructive-foreground",
    alert: "bg-primary text-primary-foreground",
    monetary: "bg-muted text-muted-foreground border",
    obs: "bg-muted text-muted-foreground border",
  };
  const labels = { critical: "crítico", alert: "alerta", monetary: "monetário", obs: "observação" };
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${styles[variant]}`}>
      {count} {labels[variant]}{count > 1 && variant !== "obs" ? "s" : ""}
    </span>
  );
}

function PeriodStatus({ period }: { period: PeriodRow }) {
  if (!period.has_efd) {
    return <span className="text-xs text-muted-foreground">sem EFD</span>;
  }
  if (period.efd_parse_status !== "parsed") {
    return <span className="text-xs text-muted-foreground">aguardando parse</span>;
  }
  if (!period.latest_run) {
    return <span className="text-xs text-muted-foreground">não conferido</span>;
  }
  const r = period.latest_run;
  if (r.total_findings === 0) {
    return <span className="text-xs text-green-600 font-medium">sem achados</span>;
  }
  return (
    <div className="flex flex-wrap gap-1">
      <SeverityBadge count={r.critical_count} variant="critical" />
      <SeverityBadge count={r.alert_count} variant="alert" />
      <SeverityBadge count={r.monetary_count} variant="monetary" />
      <SeverityBadge count={r.observation_count} variant="obs" />
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<DashboardData>("/api/v1/dashboard/")
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-background p-8">
        <div className="max-w-5xl mx-auto pt-10">
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-background p-8">
        <div className="max-w-5xl mx-auto pt-10">
          <p className="text-destructive">Erro ao carregar dashboard: {error}</p>
        </div>
      </main>
    );
  }

  const { summary, companies } = data;

  return (
    <main className="min-h-screen bg-background p-8">
      <div className="max-w-5xl mx-auto pt-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Visão geral das conferências por empresa
            </p>
          </div>
          <a href="/empresas" className="text-sm text-muted-foreground hover:underline">
            Gerenciar empresas →
          </a>
        </div>

        {/* Cartões de resumo */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <SummaryCard label="Empresas" value={summary.total_companies} />
          <SummaryCard label="Competências" value={summary.total_periods} />
          <SummaryCard
            label="Achados Críticos"
            value={summary.total_critical}
            variant={summary.total_critical > 0 ? "critical" : "ok"}
          />
          <SummaryCard
            label="Alertas"
            value={summary.total_alert}
            variant={summary.total_alert > 0 ? "alert" : "ok"}
          />
        </div>

        {/* Lista de empresas */}
        {companies.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <p className="text-base">Nenhuma empresa cadastrada ainda.</p>
            <a href="/empresas" className="text-sm underline mt-2 inline-block">
              Cadastrar empresa
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {companies.map((company) => (
              <div key={company.id} className="bg-card border rounded-lg overflow-hidden">
                {/* Cabeçalho da empresa */}
                <div className="flex items-center justify-between px-5 py-4 border-b bg-muted/40">
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="font-semibold text-sm">{company.trade_name || company.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {company.cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}
                        {company.state && ` · ${company.state}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {company.critical_count > 0 && (
                      <SeverityBadge count={company.critical_count} variant="critical" />
                    )}
                    {company.alert_count > 0 && (
                      <SeverityBadge count={company.alert_count} variant="alert" />
                    )}
                    <a
                      href={`/empresas/${company.id}`}
                      className="text-xs text-muted-foreground hover:underline ml-2"
                    >
                      ver →
                    </a>
                  </div>
                </div>

                {/* Competências */}
                {company.periods.length === 0 ? (
                  <div className="px-5 py-4 text-sm text-muted-foreground">
                    Nenhuma competência cadastrada.
                  </div>
                ) : (
                  <div className="divide-y">
                    {company.periods.map((period) => (
                      <div
                        key={period.id}
                        className="flex items-center justify-between px-5 py-3 hover:bg-muted/20 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium w-20">
                            {MONTHS[period.month]}/{period.year}
                          </span>
                          <PeriodStatus period={period} />
                        </div>
                        <a
                          href={`/competencias/${period.id}`}
                          className="text-xs text-muted-foreground hover:underline"
                        >
                          abrir →
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-10">
          <a href="/" className="text-sm text-muted-foreground hover:underline">
            ← Início
          </a>
        </div>
      </div>
    </main>
  );
}
