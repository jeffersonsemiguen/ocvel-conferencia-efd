"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { UploadIcon, SearchIcon } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface CfopCstRule {
  id: string;
  cfop: string;
  cst_icms: string | null;
  csosn: string | null;
  operation_type: string | null;
  rule_behavior: string;
  severity: string;
  valid_from: string | null;
  valid_to: string | null;
  description: string | null;
  is_active: boolean;
}

interface ImportResult {
  inserted: number;
  updated: number;
  skipped: number;
  errors: string[];
}

const BEHAVIOR_LABELS: Record<string, string> = {
  allowed: "Permitido",
  warning: "Atenção",
  blocked: "Bloqueado",
  expected: "Esperado",
};

const BEHAVIOR_VARIANTS: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  allowed: "default",
  warning: "secondary",
  blocked: "destructive",
  expected: "outline",
};

const SEVERITY_LABELS: Record<string, string> = {
  critico: "Crítico",
  critical: "Crítico",
  alerta: "Alerta",
  warning: "Alerta",
  observacao: "Observação",
  info: "Info",
};

const OPERATION_LABELS: Record<string, string> = {
  entrada: "Entrada",
  saida: "Saída",
  ambos: "Ambos",
};

export default function FiscalMatrixPage() {
  const [rules, setRules] = useState<CfopCstRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);

  const [filterCfop, setFilterCfop] = useState("");
  const [filterOperationType, setFilterOperationType] = useState<string>("all");
  const [filterRuleBehavior, setFilterRuleBehavior] = useState<string>("all");

  const fileInputRef = useRef<HTMLInputElement>(null);

  async function fetchRules() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterCfop) params.set("cfop", filterCfop);
      if (filterOperationType && filterOperationType !== "all") params.set("operation_type", filterOperationType);
      if (filterRuleBehavior && filterRuleBehavior !== "all") params.set("rule_behavior", filterRuleBehavior);

      const token = getToken();
      const res = await fetch(
        `${API_BASE}/api/v1/fiscal-matrix/cfop-cst-rules?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      setRules(data);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Erro ao carregar regras");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchRules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleImport(file: File) {
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/fiscal-matrix/cfop-cst/import`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data: ImportResult = await res.json();

      if (!res.ok) {
        toast.error(`Erro na importação: ${JSON.stringify(data)}`);
        return;
      }

      if (data.errors && data.errors.length > 0) {
        toast.warning(
          `Importado com erros: ${data.inserted} inseridos, ${data.updated} atualizados. Erros: ${data.errors.length}`
        );
      } else {
        toast.success(
          `Importação concluída: ${data.inserted} inseridos, ${data.updated} atualizados.`
        );
      }

      fetchRules();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Erro na importação");
    } finally {
      setImporting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleImport(file);
  }

  function formatVigencia(from: string | null, to: string | null): string {
    if (!from && !to) return "Sempre";
    if (from && !to) return `A partir de ${from}`;
    if (!from && to) return `Até ${to}`;
    return `${from} — ${to}`;
  }

  return (
    <main className="max-w-6xl mx-auto px-6 pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Matriz Fiscal CFOP × CST</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Gerencie as regras de compatibilidade entre CFOP e CST ICMS importadas via planilha.
        </p>
      </div>

      {/* Card de importação */}
      <Card className="mb-6">
        <CardHeader className="pb-2">
          <p className="text-sm font-semibold">Importar Planilha XLSX</p>
          <p className="text-xs text-muted-foreground">
            Colunas esperadas: cfop, cst_icms, csosn, operation_type, rule_behavior, severity,
            valid_from, valid_to, description, orientation_text, source_name, source_version, is_active
          </p>
        </CardHeader>
        <CardContent className="pt-0">
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
            className="gap-2"
          >
            <UploadIcon className="w-4 h-4" />
            {importing ? "Importando..." : "Selecionar arquivo .xlsx"}
          </Button>
        </CardContent>
      </Card>

      {/* Filtros */}
      <Card className="mb-4">
        <CardContent className="py-3 px-5">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[150px]">
              <label className="text-xs text-muted-foreground block mb-1">CFOP</label>
              <div className="relative">
                <SearchIcon className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-muted-foreground" />
                <Input
                  placeholder="Ex: 1102"
                  value={filterCfop}
                  onChange={(e) => setFilterCfop(e.target.value)}
                  className="pl-8 h-8 text-sm"
                />
              </div>
            </div>

            <div className="min-w-[160px]">
              <label className="text-xs text-muted-foreground block mb-1">Tipo de Operação</label>
              <Select value={filterOperationType} onValueChange={(v) => setFilterOperationType(v ?? "all")}>
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="entrada">Entrada</SelectItem>
                  <SelectItem value="saida">Saída</SelectItem>
                  <SelectItem value="ambos">Ambos</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="min-w-[160px]">
              <label className="text-xs text-muted-foreground block mb-1">Comportamento</label>
              <Select value={filterRuleBehavior} onValueChange={(v) => setFilterRuleBehavior(v ?? "all")}>
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="allowed">Permitido</SelectItem>
                  <SelectItem value="warning">Atenção</SelectItem>
                  <SelectItem value="blocked">Bloqueado</SelectItem>
                  <SelectItem value="expected">Esperado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button size="sm" onClick={fetchRules} disabled={loading} className="gap-2 bg-primary">
              <SearchIcon className="w-3.5 h-3.5" />
              {loading ? "Buscando..." : "Buscar"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de regras */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">CFOP</TableHead>
                  <TableHead className="w-24">CST/CSOSN</TableHead>
                  <TableHead className="w-28">Operação</TableHead>
                  <TableHead className="w-32">Comportamento</TableHead>
                  <TableHead className="w-28">Severidade</TableHead>
                  <TableHead>Vigência</TableHead>
                  <TableHead className="w-16">Ativo</TableHead>
                  <TableHead>Descrição</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-sm text-muted-foreground">
                      Carregando regras...
                    </TableCell>
                  </TableRow>
                ) : rules.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-sm text-muted-foreground">
                      Nenhuma regra encontrada. Importe uma planilha XLSX para começar.
                    </TableCell>
                  </TableRow>
                ) : (
                  rules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-mono text-sm font-medium">{rule.cfop}</TableCell>
                      <TableCell className="font-mono text-sm">
                        {rule.cst_icms ?? rule.csosn ?? "—"}
                      </TableCell>
                      <TableCell className="text-sm">
                        {rule.operation_type
                          ? OPERATION_LABELS[rule.operation_type] ?? rule.operation_type
                          : "—"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={BEHAVIOR_VARIANTS[rule.rule_behavior] ?? "outline"}>
                          {BEHAVIOR_LABELS[rule.rule_behavior] ?? rule.rule_behavior}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {SEVERITY_LABELS[rule.severity] ?? rule.severity}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {formatVigencia(rule.valid_from, rule.valid_to)}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-block w-2 h-2 rounded-full ${
                            rule.is_active ? "bg-green-500" : "bg-gray-300"
                          }`}
                        />
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground max-w-xs truncate">
                        {rule.description ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
          {rules.length > 0 && (
            <div className="px-4 py-2 border-t text-xs text-muted-foreground">
              {rules.length} regra{rules.length !== 1 ? "s" : ""} exibida{rules.length !== 1 ? "s" : ""}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-10">
        <a href="/admin" className="text-sm text-muted-foreground hover:underline">
          ← Administração
        </a>
      </div>
    </main>
  );
}
