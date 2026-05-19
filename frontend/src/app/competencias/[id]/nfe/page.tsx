"use client";

import { useCallback, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { UploadIcon, PlayIcon, CheckCheckIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import type { NfeUploadResponse, NfeFinding } from "@/lib/types";

const SEVERITY_BADGE: Record<string, string> = {
  critico: "destructive",
  alerta: "warning",
  divergencia_monetaria: "secondary",
  observacao: "outline",
};

function severityLabel(s: string): string {
  const map: Record<string, string> = {
    critico: "Critico",
    alerta: "Alerta",
    divergencia_monetaria: "Monetario",
    observacao: "Observacao",
  };
  return map[s] ?? s;
}

function groupByRuleAndCst(findings: NfeFinding[]) {
  const groups: Record<
    string,
    { rule_code: string; original_value: string; suggested_value: string; count: number }
  > = {};

  for (const f of findings) {
    if (f.rule_code !== "CONF-NFE-CST-DIVERGENTE") continue;
    const orig = f.efd_value != null ? String(Math.round(f.efd_value)) : "";
    const sugg = f.reference_value != null ? String(Math.round(f.reference_value)) : "";
    const key = `${f.rule_code}|${orig}|${sugg}`;
    if (!groups[key]) {
      groups[key] = { rule_code: f.rule_code, original_value: orig, suggested_value: sugg, count: 0 };
    }
    groups[key].count += 1;
  }
  return Object.values(groups);
}

export default function NfePage() {
  const { id: periodId } = useParams<{ id: string }>();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<NfeUploadResponse | null>(null);
  const [findings, setFindings] = useState<NfeFinding[]>([]);
  const [approvingKey, setApprovingKey] = useState<string | null>(null);

  const handleUpload = useCallback(async () => {
    const files = fileInputRef.current?.files;
    if (!files || files.length === 0) {
      toast.error("Selecione um ou mais arquivos XML ou ZIP.");
      return;
    }

    setUploading(true);
    try {
      const form = new FormData();
      for (const file of Array.from(files)) {
        form.append("files", file);
      }

      const result = await api.upload<NfeUploadResponse>(
        `/api/v1/fiscal-periods/${periodId}/nfe/upload`,
        form
      );
      setSummary(result);
      toast.success(`Upload concluido: ${result.autorizadas} autorizadas, ${result.canceladas} canceladas.`);

      const found = await api.get<NfeFinding[]>(
        `/api/v1/fiscal-periods/${periodId}/nfe/findings`
      );
      setFindings(found);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro no upload.");
    } finally {
      setUploading(false);
    }
  }, [periodId]);

  const handleRerun = useCallback(async () => {
    try {
      await api.post(`/api/v1/fiscal-periods/${periodId}/nfe/run-crosscheck`, {});
      const found = await api.get<NfeFinding[]>(
        `/api/v1/fiscal-periods/${periodId}/nfe/findings`
      );
      setFindings(found);
      toast.success("Cross-check re-executado.");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Erro ao re-executar.");
    }
  }, [periodId]);

  const handleBatchApprove = useCallback(
    async (rule_code: string, original_value: string, suggested_value: string) => {
      const key = `${rule_code}|${original_value}|${suggested_value}`;
      setApprovingKey(key);
      try {
        const result = await api.post<{ approved_count: number }>(
          `/api/v1/fiscal-periods/${periodId}/nfe/apply-suggestions-batch`,
          { rule_code, original_value, suggested_value }
        );
        toast.success(`${result.approved_count} sugestao(oes) aprovada(s) em lote.`);
      } catch (err: unknown) {
        toast.error(err instanceof Error ? err.message : "Erro na aprovacao em lote.");
      } finally {
        setApprovingKey(null);
      }
    },
    [periodId]
  );

  const cstGroups = groupByRuleAndCst(findings);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">NF-e XML — Conferencia</h1>
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
          <p className="text-sm font-medium">Aprovacao em lote — CST divergente</p>
          <div className="space-y-2">
            {cstGroups.map((g) => {
              const key = `${g.rule_code}|${g.original_value}|${g.suggested_value}`;
              return (
                <div key={key} className="flex items-center justify-between rounded border px-3 py-2">
                  <span className="text-sm">
                    CST {g.original_value} → {g.suggested_value}
                    <span className="ml-2 text-muted-foreground">({g.count} ocorrencia(s))</span>
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={approvingKey === key}
                    onClick={() =>
                      handleBatchApprove(g.rule_code, g.original_value, g.suggested_value)
                    }
                  >
                    <CheckCheckIcon className="mr-1 h-4 w-4" />
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
          <p className="text-sm font-medium">{findings.length} finding(s) encontrado(s)</p>
          <div className="rounded-lg border overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Severidade</TableHead>
                  <TableHead>Regra</TableHead>
                  <TableHead>Titulo</TableHead>
                  <TableHead>Operacao</TableHead>
                  <TableHead>Descricao</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {findings.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell>
                      <Badge variant={SEVERITY_BADGE[f.severity] as "default" | "destructive" | "outline" | "secondary" ?? "outline"}>
                        {severityLabel(f.severity)}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{f.rule_code}</TableCell>
                    <TableCell className="text-sm">{f.title}</TableCell>
                    <TableCell className="text-xs capitalize">{f.operation_type ?? "—"}</TableCell>
                    <TableCell className="text-xs text-muted-foreground max-w-xs truncate">
                      {f.description ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      {findings.length === 0 && summary && (
        <p className="text-sm text-muted-foreground">Nenhum finding NF-e encontrado para esta competencia.</p>
      )}
    </div>
  );
}
