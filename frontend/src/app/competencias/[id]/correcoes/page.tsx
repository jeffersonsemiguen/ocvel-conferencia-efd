"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeftIcon, DownloadIcon, WandSparklesIcon } from "lucide-react";
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
import type { CorrectionsPreview, CorrectedFile } from "@/lib/types";


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
    } catch {
      toast.error("Erro ao carregar prévia de correções.");
    } finally {
      setLoading(false);
    }
  }, [periodId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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

  if (loading) {
    return <div className="p-6 text-sm text-muted-foreground">Carregando...</div>;
  }

  const affectedRegisters = new Set(preview?.groups.map((g) => g.register_code)).size;
  const sources = new Set(preview?.groups.map((g) => g.source ?? "efd")).size;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Voltar
        </Button>
        <h1 className="text-2xl font-semibold">TXT Corrigido</h1>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Correções aprovadas", value: preview?.total_approved ?? 0 },
          { label: "Registros afetados", value: affectedRegisters },
          { label: "Fontes", value: sources },
        ].map(({ label, value }) => (
          <div key={label} className="rounded border p-4 text-center">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="text-2xl font-semibold">{value}</p>
          </div>
        ))}
      </div>

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
                        <Badge variant="outline" className="text-xs whitespace-nowrap">
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

      <div className="space-y-1">
        <Button onClick={handleGenerate} disabled={!canGenerate}>
          <WandSparklesIcon className="mr-2 h-4 w-4" />
          {generating ? "Gerando..." : "Gerar TXT Corrigido"}
        </Button>
        {!canGenerate && !generating && (
          <p className="text-xs text-muted-foreground">
            Nenhuma correção aprovada para aplicar.
          </p>
        )}
      </div>

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
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          api.download(
                            `/api/v1/corrected-files/${cf.id}/download`,
                            cf.generated_filename
                          ).catch(() => toast.error("Erro ao baixar arquivo."))
                        }
                      >
                        <DownloadIcon className="h-4 w-4 mr-1" />
                        Baixar
                      </Button>
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
