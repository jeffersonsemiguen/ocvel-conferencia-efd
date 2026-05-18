"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { PlusIcon, UploadIcon, FileTextIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Company, EfdFile, FiscalPeriod } from "@/lib/types";

const MESES = [
  "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
  "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro",
];

const ANOS = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - i);

function parseStatusBadge(status: string) {
  const map: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
    uploaded:   { label: "Aguardando parse", variant: "secondary" },
    parsing:    { label: "Processando",      variant: "outline" },
    parsed:     { label: "Processado",       variant: "default" },
    error:      { label: "Erro",             variant: "destructive" },
  };
  const info = map[status] ?? { label: status, variant: "outline" as const };
  return <Badge variant={info.variant}>{info.label}</Badge>;
}

function periodStatusBadge(status: string) {
  const map: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
    pending:    { label: "Pendente",     variant: "secondary" },
    processing: { label: "Processando", variant: "outline" },
    completed:  { label: "Concluído",   variant: "default" },
    error:      { label: "Erro",        variant: "destructive" },
  };
  const info = map[status] ?? { label: status, variant: "outline" as const };
  return <Badge variant={info.variant}>{info.label}</Badge>;
}

function UploadEfdDialog({
  period,
  onUploaded,
}: {
  period: FiscalPeriod;
  onUploaded: (file: EfdFile) => void;
}) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const efdFile = await api.upload<EfdFile>(`/api/v1/fiscal-periods/${period.id}/efd-files`, formData);
      onUploaded(efdFile);
      setOpen(false);

      if (efdFile.parse_status === "parsed") {
        toast.success(`Arquivo processado — ${efdFile.total_lines?.toLocaleString()} linhas`);
      } else if (efdFile.parse_status === "error") {
        toast.error(`Parse falhou: ${efdFile.parse_error}`);
      } else {
        toast.success("Arquivo enviado");
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro no upload");
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm" variant="outline"><UploadIcon className="w-3.5 h-3.5 mr-1" />Enviar EFD</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Upload EFD — {MESES[period.month - 1]}/{period.year}
          </DialogTitle>
        </DialogHeader>
        <div className="mt-4 space-y-4">
          <p className="text-sm text-muted-foreground">
            Selecione o arquivo TXT da EFD ICMS/IPI para esta competência.
          </p>
          <div
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-accent transition-colors"
            onClick={() => inputRef.current?.click()}
          >
            <FileTextIcon className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm font-medium">
              {loading ? "Enviando e processando..." : "Clique para selecionar o arquivo .txt"}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Somente arquivos .txt</p>
            <input
              ref={inputRef}
              type="file"
              accept=".txt"
              className="hidden"
              onChange={handleUpload}
              disabled={loading}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function NovaCompetenciaDialog({
  companies,
  onCreated,
}: {
  companies: Company[];
  onCreated: (p: FiscalPeriod) => void;
}) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [companyId, setCompanyId] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [month, setMonth] = useState(String(new Date().getMonth() + 1));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!companyId) { toast.error("Selecione uma empresa"); return; }
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
      <DialogTrigger render={<Button size="sm"><PlusIcon className="w-4 h-4 mr-1" />Nova competência</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova competência</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1">
            <Label>Empresa *</Label>
            <select
              required
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
            >
              <option value="">Selecione uma empresa</option>
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Mês *</Label>
              <select
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                {MESES.map((m, i) => (
                  <option key={i + 1} value={i + 1}>{m}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Ano *</Label>
              <select
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                {ANOS.map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Criando..." : "Criar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EfdFilesRow({ period }: { period: FiscalPeriod }) {
  const [files, setFiles] = useState<EfdFile[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api.get<EfdFile[]>(`/api/v1/fiscal-periods/${period.id}/efd-files`)
      .then(setFiles)
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, [period.id]);

  if (!loaded) return null;

  return (
    <>
      {files.map((f) => (
        <TableRow key={f.id} className="bg-muted/30">
          <TableCell />
          <TableCell className="pl-8">
            <div className="flex items-center gap-2">
              <FileTextIcon className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-sm font-mono">{f.original_filename}</span>
            </div>
          </TableCell>
          <TableCell className="text-sm text-muted-foreground">
            {f.efd_cnpj ?? "—"}
          </TableCell>
          <TableCell className="text-sm text-muted-foreground">
            {f.total_lines?.toLocaleString() ?? "—"} linhas
          </TableCell>
          <TableCell>{parseStatusBadge(f.parse_status)}</TableCell>
          <TableCell className="text-sm text-muted-foreground">
            {f.efd_start_date && f.efd_end_date
              ? `${f.efd_start_date} → ${f.efd_end_date}`
              : "—"}
          </TableCell>
        </TableRow>
      ))}
    </>
  );
}

export default function CompetenciasPage() {
  const [periods, setPeriods] = useState<FiscalPeriod[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [companyMap, setCompanyMap] = useState<Record<string, Company>>({});

  useEffect(() => {
    Promise.all([
      api.get<FiscalPeriod[]>("/api/v1/fiscal-periods"),
      api.get<Company[]>("/api/v1/companies"),
    ])
      .then(([p, c]) => {
        setPeriods(p);
        setCompanies(c);
        setCompanyMap(Object.fromEntries(c.map((co) => [co.id, co])));
      })
      .catch(() => toast.error("Erro ao carregar dados"))
      .finally(() => setLoading(false));
  }, []);

  function handleEfdUploaded(periodId: string, _file: EfdFile) {
    // Refresh period status visual — simplest approach: reload all
    api.get<FiscalPeriod[]>("/api/v1/fiscal-periods").then(setPeriods).catch(() => {});
  }

  return (
    <main className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Competências</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Períodos fiscais e arquivos EFD
          </p>
        </div>
        <NovaCompetenciaDialog
          companies={companies}
          onCreated={(p) => setPeriods((prev) => [p, ...prev])}
        />
      </div>

      {loading ? (
        <p className="text-muted-foreground text-sm">Carregando...</p>
      ) : periods.length === 0 ? (
        <div className="border rounded-lg p-12 text-center text-muted-foreground">
          <p className="text-sm">Nenhuma competência cadastrada.</p>
          <p className="text-sm">
            {companies.length === 0
              ? "Cadastre uma empresa primeiro."
              : "Clique em \"Nova competência\" para começar."}
          </p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-36">Competência</TableHead>
                <TableHead>Empresa</TableHead>
                <TableHead>UF</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-28" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {periods.map((period) => (
                <TableRow key={period.id}>
                  <TableCell className="font-medium">
                    {MESES[period.month - 1].slice(0, 3)}/{period.year}
                  </TableCell>
                  <TableCell>{companyMap[period.company_id]?.name ?? "—"}</TableCell>
                  <TableCell>{companyMap[period.company_id]?.state ?? "—"}</TableCell>
                  <TableCell>{periodStatusBadge(period.status)}</TableCell>
                  <TableCell>
                    <a href={`/competencias/${period.id}`}>
                      <Button size="sm" variant="outline">Abrir</Button>
                    </a>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </main>
  );
}
