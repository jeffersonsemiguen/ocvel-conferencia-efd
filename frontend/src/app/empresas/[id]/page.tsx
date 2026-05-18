"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { PlusIcon, ArrowRightIcon, BuildingIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import type { Company, FiscalPeriod } from "@/lib/types";

const MESES = [
  "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
  "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro",
];
const ANOS = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - i);

const STATUS_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  pending:    { label: "Pendente",     variant: "secondary" },
  processing: { label: "Processando", variant: "outline" },
  completed:  { label: "Concluído",   variant: "default" },
  error:      { label: "Erro",        variant: "destructive" },
};

function formatCnpj(cnpj: string) {
  return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

function NovaCompetenciaDialog({
  companyId,
  onCreated,
}: {
  companyId: string;
  onCreated: (p: FiscalPeriod) => void;
}) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [month, setMonth] = useState(String(new Date().getMonth() + 1));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const period = await api.post<FiscalPeriod>("/api/v1/fiscal-periods", {
        company_id: companyId,
        year: Number(year),
        month: Number(month),
      });
      onCreated(period);
      setOpen(false);
      toast.success("Competência criada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao criar competência");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={
        <Button size="sm">
          <PlusIcon className="w-4 h-4 mr-1" />Nova competência
        </Button>
      } />
      <DialogContent>
        <DialogHeader><DialogTitle>Nova competência</DialogTitle></DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Mês *</Label>
              <select
                value={month}
                onChange={e => setMonth(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                {MESES.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Ano *</Label>
              <select
                value={year}
                onChange={e => setYear(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                {ANOS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" disabled={loading}>{loading ? "Criando..." : "Criar"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function EmpresaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [company, setCompany] = useState<Company | null>(null);
  const [periods, setPeriods] = useState<FiscalPeriod[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<Company>(`/api/v1/companies/${id}`),
      api.get<FiscalPeriod[]>(`/api/v1/fiscal-periods?company_id=${id}`),
    ])
      .then(([c, p]) => { setCompany(c); setPeriods(p); })
      .catch(() => toast.error("Erro ao carregar empresa"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <main className="max-w-4xl mx-auto px-6 py-8"><p className="text-sm text-muted-foreground">Carregando...</p></main>;
  }

  if (!company) {
    return <main className="max-w-4xl mx-auto px-6 py-8"><p className="text-sm text-muted-foreground">Empresa não encontrada.</p></main>;
  }

  const grouped = periods.reduce<Record<number, FiscalPeriod[]>>((acc, p) => {
    (acc[p.year] = acc[p.year] ?? []).push(p);
    return acc;
  }, {});
  const years = Object.keys(grouped).map(Number).sort((a, b) => b - a);

  return (
    <main className="max-w-4xl mx-auto px-6 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <a href="/empresas" className="hover:text-foreground">Empresas</a>
        <span>/</span>
        <span className="text-foreground">{company.name}</span>
      </div>

      {/* Cabeçalho da empresa */}
      <div className="flex items-start gap-4 mb-8">
        <div className="w-12 h-12 rounded-lg border bg-muted flex items-center justify-center shrink-0">
          <BuildingIcon className="w-5 h-5 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold truncate">{company.name}</h1>
          {company.trade_name && (
            <p className="text-sm text-muted-foreground">{company.trade_name}</p>
          )}
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <span className="text-sm font-mono text-muted-foreground">
              {formatCnpj(company.cnpj)}
            </span>
            {company.state && (
              <Badge variant="outline" className="text-xs">{company.state}</Badge>
            )}
            {company.state_registration && (
              <span className="text-xs text-muted-foreground">IE: {company.state_registration}</span>
            )}
            <Badge variant={company.is_active ? "default" : "secondary"} className="text-xs">
              {company.is_active ? "Ativa" : "Inativa"}
            </Badge>
          </div>
        </div>
      </div>

      {/* Link para dashboard */}
      <div className="mb-6">
        <a
          href={`/empresas/${company.id}/dashboard`}
          className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
        >
          Ver Dashboard de Risco
          <ArrowRightIcon className="w-4 h-4" />
        </a>
      </div>

      {/* Competências */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Competências</h2>
        <NovaCompetenciaDialog
          companyId={company.id}
          onCreated={p => setPeriods(prev => [p, ...prev])}
        />
      </div>

      {periods.length === 0 ? (
        <div className="border-2 border-dashed rounded-lg p-12 text-center text-muted-foreground">
          <p className="text-sm">Nenhuma competência cadastrada.</p>
          <p className="text-sm mt-1">Clique em &quot;Nova competência&quot; para começar.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {years.map(year => (
            <div key={year}>
              <p className="text-sm font-semibold text-muted-foreground mb-2">{year}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {grouped[year]
                  .sort((a, b) => b.month - a.month)
                  .map(period => {
                    const statusInfo = STATUS_CONFIG[period.status] ?? { label: period.status, variant: "outline" as const };
                    return (
                      <a
                        key={period.id}
                        href={`/competencias/${period.id}`}
                        className="group block border rounded-lg p-4 hover:bg-accent hover:border-accent-foreground/20 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">
                            {MESES[period.month - 1]}
                          </span>
                          <ArrowRightIcon className="w-4 h-4 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
                        </div>
                        <Badge variant={statusInfo.variant} className="text-xs">
                          {statusInfo.label}
                        </Badge>
                      </a>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
