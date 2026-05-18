"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { UploadIcon, SearchIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
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
import { getToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface PrCode {
  id: string;
  code: string;
  table_type: string;
  description: string;
  short_description: string | null;
  requires_e112: boolean;
  requires_e113: boolean;
  requires_fiscal_document: boolean;
  requires_process: boolean;
  valid_from: string | null;
  valid_to: string | null;
  is_active: boolean;
}

interface ImportResult {
  batch_id: string;
  status: string;
  records_total: number;
  records_imported: number;
  records_failed: number;
  errors: string[];
}

const TABLE_TYPE_LABELS: Record<string, string> = {
  ajuste_apuracao: "Ajuste Apuração",
  ajuste_documento: "Ajuste Documento",
  beneficio: "Benefício Fiscal",
};

export default function PrAdjustmentCodesPage() {
  const [codes, setCodes] = useState<PrCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);

  // Filters
  const [filterCode, setFilterCode] = useState("");
  const [filterTableType, setFilterTableType] = useState("");
  const [filterValidOn, setFilterValidOn] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  async function fetchCodes() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterCode) params.set("code", filterCode);
      if (filterTableType) params.set("table_type", filterTableType);
      if (filterValidOn) params.set("valid_on", filterValidOn);

      const token = getToken();
      const res = await fetch(
        `${API_BASE}/api/v1/pr-adjustment-codes/?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      setCodes(data);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Erro ao carregar códigos");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchCodes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleImport(file: File) {
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/pr-adjustment-codes/import`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data: ImportResult = await res.json();

      if (!res.ok) {
        toast.error(`Erro na importação: ${JSON.stringify(data)}`);
        return;
      }

      if (data.records_failed > 0) {
        toast.warning(
          `Importado com erros: ${data.records_imported} de ${data.records_total} registros. ` +
            `Falhas: ${data.records_failed}`
        );
      } else {
        toast.success(
          `Importação concluída: ${data.records_imported} registros importados.`
        );
      }

      await fetchCodes();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Erro ao importar arquivo");
    } finally {
      setImporting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleImport(file);
  }

  function formatDate(d: string | null) {
    if (!d) return "—";
    return new Date(d).toLocaleDateString("pt-BR");
  }

  const filtered = codes.filter((c) => {
    if (filterCode && !c.code.toLowerCase().includes(filterCode.toLowerCase()))
      return false;
    if (filterTableType && c.table_type !== filterTableType) return false;
    return true;
  });

  return (
    <main className="max-w-7xl mx-auto px-6 pt-10 pb-20">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">
          Tabela de Códigos de Ajuste PR
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Tabela 5.1.1 — Paraná. Gerencie e importe os códigos usados na
          validação dos registros E111.
        </p>
      </div>

      {/* Toolbar */}
      <Card className="mb-6">
        <CardContent className="py-4 px-5">
          <div className="flex flex-wrap gap-3 items-end">
            {/* Code filter */}
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Código</span>
              <div className="relative">
                <SearchIcon className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  placeholder="Filtrar código..."
                  value={filterCode}
                  onChange={(e) => setFilterCode(e.target.value)}
                  className="pl-8 h-9 w-44 text-sm"
                />
              </div>
            </div>

            {/* Table type filter */}
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Tipo de Tabela</span>
              <select
                value={filterTableType}
                onChange={(e) => setFilterTableType(e.target.value)}
                className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Todos</option>
                {Object.entries(TABLE_TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>

            {/* Valid on date */}
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Vigente em</span>
              <Input
                type="date"
                value={filterValidOn}
                onChange={(e) => setFilterValidOn(e.target.value)}
                className="h-9 w-40 text-sm"
              />
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={fetchCodes}
              disabled={loading}
              className="self-end"
            >
              {loading ? "Buscando..." : "Buscar"}
            </Button>

            <div className="flex-1" />

            {/* Import XLSX */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              className="hidden"
              onChange={onFileChange}
            />
            <Button
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={importing}
              className="bg-primary text-primary-foreground self-end"
            >
              <UploadIcon className="w-4 h-4 mr-1.5" />
              {importing ? "Importando..." : "Importar XLSX"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <p className="text-xs text-muted-foreground mb-3">
        {loading
          ? "Carregando..."
          : `${filtered.length} código(s) encontrado(s)`}
      </p>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-24">Código</TableHead>
                  <TableHead className="w-36">Tipo</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead className="w-28">Vigência início</TableHead>
                  <TableHead className="w-28">Vigência fim</TableHead>
                  <TableHead className="w-20 text-center">E112</TableHead>
                  <TableHead className="w-20 text-center">E113</TableHead>
                  <TableHead className="w-20 text-center">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                      Carregando...
                    </TableCell>
                  </TableRow>
                ) : filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground text-sm">
                      Nenhum código encontrado. Importe um arquivo XLSX ou use o
                      seed para carregar os dados.
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell className="font-mono font-semibold text-sm">
                        {c.code}
                      </TableCell>
                      <TableCell>
                        <span className="text-xs text-muted-foreground">
                          {TABLE_TYPE_LABELS[c.table_type] ?? c.table_type}
                        </span>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <p className="text-sm leading-snug truncate">
                          {c.short_description || c.description}
                        </p>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(c.valid_from)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(c.valid_to)}
                      </TableCell>
                      <TableCell className="text-center">
                        {c.requires_e112 ? (
                          <Badge variant="default" className="text-xs">Sim</Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        {c.requires_e113 ? (
                          <Badge variant="default" className="text-xs">Sim</Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        {c.is_active ? (
                          <Badge variant="secondary" className="text-xs">Ativo</Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">Inativo</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <div className="mt-8">
        <a href="/admin" className="text-sm text-muted-foreground hover:underline">
          ← Administração
        </a>
      </div>
    </main>
  );
}
