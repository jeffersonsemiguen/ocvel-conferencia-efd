"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { ChevronDownIcon, ChevronRightIcon, XIcon, PlusIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

interface RuleConfig {
  id: string;
  rule_code: string;
  label: string | null;
  group: string;
  is_active: boolean;
  severity_override: string | null;
  cfop_exclusions: string[];
  description: string | null;
  updated_at: string | null;
}

const GROUP_LABELS: Record<string, string> = {
  nfe_crosscheck: "NF-e × EFD — Cross-check XML",
  conferencia:    "Conferência Fiscal",
  pr_rules:       "Receita Estadual PR",
  estrutural:     "Estrutural",
};

const SEVERITY_OPTIONS = [
  { value: "", label: "Padrão (engine)" },
  { value: "critico", label: "Crítico" },
  { value: "alerta", label: "Alerta" },
  { value: "divergencia_monetaria", label: "Monetário" },
  { value: "observacao", label: "Observação" },
];

export default function ValidationRulesPage() {
  const [configs, setConfigs] = useState<RuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [editing, setEditing] = useState<Record<string, Partial<RuleConfig>>>({});
  const [saving, setSaving] = useState<Set<string>>(new Set());
  const [newCfop, setNewCfop] = useState<Record<string, string>>({});

  useEffect(() => {
    api.get<RuleConfig[]>("/api/v1/validation-rule-configs/")
      .then(setConfigs)
      .catch(() => toast.error("Erro ao carregar configurações"))
      .finally(() => setLoading(false));
  }, []);

  function toggleGroup(code: string) {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(code) ? next.delete(code) : next.add(code);
      return next;
    });
    if (!editing[code]) {
      const cfg = configs.find(c => c.rule_code === code);
      if (cfg) setEditing(prev => ({ ...prev, [code]: { ...cfg } }));
    }
  }

  function setField(code: string, field: keyof RuleConfig, value: unknown) {
    setEditing(prev => ({
      ...prev,
      [code]: { ...prev[code], [field]: value },
    }));
  }

  function addCfop(code: string) {
    const cfop = (newCfop[code] || "").trim();
    if (!cfop) return;
    const current = (editing[code]?.cfop_exclusions ?? configs.find(c => c.rule_code === code)?.cfop_exclusions ?? []);
    if (!current.includes(cfop)) {
      setField(code, "cfop_exclusions", [...current, cfop]);
    }
    setNewCfop(prev => ({ ...prev, [code]: "" }));
  }

  function removeCfop(code: string, cfop: string) {
    const current = editing[code]?.cfop_exclusions ?? [];
    setField(code, "cfop_exclusions", current.filter(c => c !== cfop));
  }

  async function save(code: string) {
    const changes = editing[code];
    if (!changes) return;
    setSaving(prev => new Set(prev).add(code));
    try {
      const updated = await api.patch<RuleConfig>(`/api/v1/validation-rule-configs/${code}`, {
        is_active: changes.is_active,
        severity_override: changes.severity_override || null,
        cfop_exclusions: changes.cfop_exclusions ?? [],
      });
      setConfigs(prev => prev.map(c => c.rule_code === code ? updated : c));
      toast.success(`Regra ${code} salva`);
    } catch {
      toast.error("Erro ao salvar");
    } finally {
      setSaving(prev => { const next = new Set(prev); next.delete(code); return next; });
    }
  }

  const byGroup = configs.reduce<Record<string, RuleConfig[]>>((acc, c) => {
    (acc[c.group] ??= []).push(c);
    return acc;
  }, {});

  if (loading) return <div className="p-8 text-muted-foreground text-sm">Carregando...</div>;

  return (
    <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Regras de Validação</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Configure quais regras estão ativas, a severidade e quais CFOPs devem ser ignorados por cada regra.
        </p>
      </div>

      {Object.entries(byGroup).map(([group, rules]) => (
        <div key={group} className="space-y-1">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide px-1 mb-2">
            {GROUP_LABELS[group] ?? group}
          </p>

          {rules.map(cfg => {
            const isOpen = expanded.has(cfg.rule_code);
            const draft = editing[cfg.rule_code] ?? cfg;
            const isSaving = saving.has(cfg.rule_code);
            const isDirty = JSON.stringify(draft) !== JSON.stringify(cfg);

            return (
              <div key={cfg.rule_code} className={`border rounded-lg overflow-hidden transition-colors ${draft.is_active ? "" : "opacity-60"}`}>
                {/* Header */}
                <div
                  className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-colors"
                  onClick={() => toggleGroup(cfg.rule_code)}
                >
                  {isOpen
                    ? <ChevronDownIcon className="w-4 h-4 shrink-0 text-muted-foreground" />
                    : <ChevronRightIcon className="w-4 h-4 shrink-0 text-muted-foreground" />
                  }

                  {/* Toggle ativo */}
                  <button
                    onClick={e => { e.stopPropagation(); setField(cfg.rule_code, "is_active", !draft.is_active); }}
                    className={`relative w-9 h-5 rounded-full transition-colors shrink-0 ${draft.is_active ? "bg-primary" : "bg-muted-foreground/30"}`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${draft.is_active ? "translate-x-4" : ""}`} />
                  </button>

                  <span className="font-mono text-xs text-muted-foreground shrink-0 w-52">{cfg.rule_code}</span>
                  <span className="text-sm font-medium flex-1 truncate">{cfg.label ?? cfg.rule_code}</span>

                  {cfg.cfop_exclusions.length > 0 && (
                    <Badge variant="secondary" className="text-xs shrink-0">
                      {cfg.cfop_exclusions.length} CFOP excluído(s)
                    </Badge>
                  )}
                  {!cfg.is_active && (
                    <Badge variant="outline" className="text-xs shrink-0 text-muted-foreground">Inativa</Badge>
                  )}
                </div>

                {/* Detalhes editáveis */}
                {isOpen && (
                  <div className="px-4 pb-4 pt-2 border-t bg-muted/10 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      {/* Ativo */}
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-muted-foreground">Status</label>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setField(cfg.rule_code, "is_active", !draft.is_active)}
                            className={`relative w-9 h-5 rounded-full transition-colors ${draft.is_active ? "bg-primary" : "bg-muted-foreground/30"}`}
                          >
                            <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${draft.is_active ? "translate-x-4" : ""}`} />
                          </button>
                          <span className="text-sm">{draft.is_active ? "Ativa" : "Inativa"}</span>
                        </div>
                      </div>

                      {/* Severidade */}
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-muted-foreground">Severidade</label>
                        <select
                          value={draft.severity_override ?? ""}
                          onChange={e => setField(cfg.rule_code, "severity_override", e.target.value || null)}
                          className="flex h-8 w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
                        >
                          {SEVERITY_OPTIONS.map(o => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* CFOPs excluídos */}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-muted-foreground">
                        CFOPs excluídos desta regra
                        <span className="ml-1 font-normal">(documentos com esses CFOPs não geram este achado)</span>
                      </label>

                      <div className="flex flex-wrap gap-1 min-h-6">
                        {(draft.cfop_exclusions ?? []).map(cfop => (
                          <span key={cfop} className="inline-flex items-center gap-1 bg-muted px-2 py-0.5 rounded text-xs font-mono">
                            {cfop}
                            <button onClick={() => removeCfop(cfg.rule_code, cfop)}>
                              <XIcon className="w-3 h-3 text-muted-foreground hover:text-destructive" />
                            </button>
                          </span>
                        ))}
                        {(draft.cfop_exclusions ?? []).length === 0 && (
                          <span className="text-xs text-muted-foreground">Nenhum CFOP excluído</span>
                        )}
                      </div>

                      <div className="flex gap-2 max-w-xs">
                        <Input
                          placeholder="ex: 1556"
                          value={newCfop[cfg.rule_code] ?? ""}
                          onChange={e => setNewCfop(prev => ({ ...prev, [cfg.rule_code]: e.target.value }))}
                          onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addCfop(cfg.rule_code))}
                          className="h-8 text-sm font-mono"
                          maxLength={4}
                        />
                        <Button size="sm" variant="outline" className="h-8 px-2" onClick={() => addCfop(cfg.rule_code)}>
                          <PlusIcon className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>

                    {/* Salvar */}
                    {isDirty && (
                      <div className="flex gap-2 justify-end">
                        <Button
                          size="sm" variant="outline"
                          onClick={() => setEditing(prev => ({ ...prev, [cfg.rule_code]: { ...cfg } }))}
                        >
                          Descartar
                        </Button>
                        <Button size="sm" disabled={isSaving} onClick={() => save(cfg.rule_code)}>
                          {isSaving ? "Salvando..." : "Salvar"}
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ))}
    </main>
  );
}
