"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { PlusIcon, UploadIcon, Trash2Icon, PencilIcon } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { BlocoKTipo, Company, InscricaoAuxiliar, InventarioRef } from "@/lib/types";

const ESTADOS = [
  "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
  "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO",
];

const MESES = [
  "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
  "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro",
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function formatCnpj(cnpj: string) {
  return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

interface FormState {
  cnpj: string;
  name: string;
  trade_name: string;
  state_registration: string;
  state: string;
  uses_ciap: boolean;
  bloco_k_tipo: BlocoKTipo;
  inventario_mes: string;
  inventario_competencia_ref: InventarioRef | "";
  inscricoes_auxiliares: InscricaoAuxiliar[];
}

const EMPTY_FORM: FormState = {
  cnpj: "",
  name: "",
  trade_name: "",
  state_registration: "",
  state: "",
  uses_ciap: false,
  bloco_k_tipo: "nao_aplica",
  inventario_mes: "",
  inventario_competencia_ref: "",
  inscricoes_auxiliares: [],
};

function NovaEmpresaDialog({ onCreated }: { onCreated: (c: Company) => void }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        cnpj: form.cnpj,
        name: form.name,
        trade_name: form.trade_name || null,
        state_registration: form.state_registration || null,
        state: form.state || null,
        uses_ciap: form.uses_ciap,
        bloco_k_tipo: form.bloco_k_tipo,
        inventario_mes: form.inventario_mes ? Number(form.inventario_mes) : null,
        inventario_competencia_ref: form.inventario_competencia_ref || null,
        inscricoes_auxiliares: form.inscricoes_auxiliares.filter((i) => i.uf && i.ie),
      };
      const company = await api.post<Company>("/api/v1/companies/", payload);
      onCreated(company);
      setOpen(false);
      setForm(EMPTY_FORM);
      toast.success("Empresa cadastrada com sucesso");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao cadastrar empresa");
    } finally {
      setLoading(false);
    }
  }

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function addInscricao() {
    update("inscricoes_auxiliares", [...form.inscricoes_auxiliares, { uf: "", ie: "" }]);
  }
  function removeInscricao(idx: number) {
    update("inscricoes_auxiliares", form.inscricoes_auxiliares.filter((_, i) => i !== idx));
  }
  function setInscricao(idx: number, field: "uf" | "ie", value: string) {
    update(
      "inscricoes_auxiliares",
      form.inscricoes_auxiliares.map((it, i) =>
        i === idx ? { ...it, [field]: field === "uf" ? value.toUpperCase() : value } : it
      )
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm"><PlusIcon className="w-4 h-4 mr-1" />Nova empresa</Button>} />
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nova empresa</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          {/* Identificação */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="cnpj">CNPJ *</Label>
              <Input
                id="cnpj"
                placeholder="00000000000000"
                maxLength={14}
                required
                value={form.cnpj}
                onChange={(e) => update("cnpj", e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="state">UF</Label>
              <select
                id="state"
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                <option value="">Selecione</option>
                {ESTADOS.map((uf) => (<option key={uf} value={uf}>{uf}</option>))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <Label htmlFor="name">Razão social *</Label>
            <Input id="name" required value={form.name} onChange={(e) => update("name", e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="trade_name">Nome fantasia</Label>
              <Input id="trade_name" value={form.trade_name} onChange={(e) => update("trade_name", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="ie">Inscrição estadual</Label>
              <Input id="ie" value={form.state_registration} onChange={(e) => update("state_registration", e.target.value)} />
            </div>
          </div>

          {/* Perfil fiscal */}
          <div className="border-t pt-4 space-y-3">
            <p className="text-sm font-semibold">Perfil fiscal (usado para validações)</p>

            <div className="flex items-center gap-2">
              <input
                id="uses_ciap"
                type="checkbox"
                checked={form.uses_ciap}
                onChange={(e) => update("uses_ciap", e.target.checked)}
                className="h-4 w-4"
              />
              <Label htmlFor="uses_ciap" className="text-sm font-normal cursor-pointer">
                Utiliza CIAP (Crédito do ICMS do Ativo Permanente) — exige Bloco G
              </Label>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Bloco K</Label>
                <select
                  value={form.bloco_k_tipo}
                  onChange={(e) => update("bloco_k_tipo", e.target.value as BlocoKTipo)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="nao_aplica">Não se aplica</option>
                  <option value="simplificado">Simplificado (K200/K280)</option>
                  <option value="completo">Completo (K100/K200/K220/K230…)</option>
                </select>
              </div>
              <div className="space-y-1">
                <Label>Mês do inventário (Bloco H)</Label>
                <select
                  value={form.inventario_mes}
                  onChange={(e) => update("inventario_mes", e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="">Não declara</option>
                  {MESES.map((m, i) => (<option key={i + 1} value={i + 1}>{m}</option>))}
                </select>
              </div>
            </div>

            {form.inventario_mes && (
              <div className="space-y-1">
                <Label>Referência do inventário</Label>
                <select
                  value={form.inventario_competencia_ref}
                  onChange={(e) => update("inventario_competencia_ref", e.target.value as InventarioRef | "")}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="">Selecione</option>
                  <option value="mes_anterior">Mês anterior</option>
                  <option value="dezembro_ano_anterior">Dezembro do ano anterior</option>
                  <option value="customizado">Customizado</option>
                </select>
              </div>
            )}

            {/* Inscrições auxiliares */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Inscrições estaduais auxiliares (ST em outros estados — registro 0015)</Label>
                <Button type="button" size="sm" variant="outline" onClick={addInscricao}>
                  <PlusIcon className="w-3 h-3 mr-1" /> Adicionar
                </Button>
              </div>
              {form.inscricoes_auxiliares.length === 0 ? (
                <p className="text-xs text-muted-foreground">Nenhuma inscrição auxiliar cadastrada.</p>
              ) : (
                <div className="space-y-2">
                  {form.inscricoes_auxiliares.map((insc, idx) => (
                    <div key={idx} className="flex gap-2 items-end">
                      <div className="w-20">
                        <Label className="text-xs">UF</Label>
                        <select
                          value={insc.uf}
                          onChange={(e) => setInscricao(idx, "uf", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-2 py-1 text-sm"
                        >
                          <option value="">--</option>
                          {ESTADOS.map((uf) => (<option key={uf} value={uf}>{uf}</option>))}
                        </select>
                      </div>
                      <div className="flex-1">
                        <Label className="text-xs">Inscrição estadual</Label>
                        <Input
                          value={insc.ie}
                          onChange={(e) => setInscricao(idx, "ie", e.target.value)}
                          placeholder="IE auxiliar"
                        />
                      </div>
                      <Button type="button" size="sm" variant="ghost" onClick={() => removeInscricao(idx)}>
                        <Trash2Icon className="w-3.5 h-3.5 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" disabled={loading}>{loading ? "Salvando..." : "Salvar"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── Dialog de edição de empresa ────────────────────────────────────────────

function EditarEmpresaDialog({ company, onUpdated }: { company: Company; onUpdated: (c: Company) => void }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<FormState>({
    cnpj: company.cnpj,
    name: company.name,
    trade_name: company.trade_name ?? "",
    state_registration: company.state_registration ?? "",
    state: company.state ?? "",
    uses_ciap: company.uses_ciap,
    bloco_k_tipo: company.bloco_k_tipo,
    inventario_mes: company.inventario_mes ? String(company.inventario_mes) : "",
    inventario_competencia_ref: (company.inventario_competencia_ref as InventarioRef | "") ?? "",
    inscricoes_auxiliares: company.inscricoes_auxiliares ?? [],
  });

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }
  function addInscricao() {
    update("inscricoes_auxiliares", [...form.inscricoes_auxiliares, { uf: "", ie: "" }]);
  }
  function removeInscricao(idx: number) {
    update("inscricoes_auxiliares", form.inscricoes_auxiliares.filter((_, i) => i !== idx));
  }
  function setInscricao(idx: number, field: "uf" | "ie", value: string) {
    update("inscricoes_auxiliares", form.inscricoes_auxiliares.map((it, i) =>
      i === idx ? { ...it, [field]: field === "uf" ? value.toUpperCase() : value } : it
    ));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        name: form.name,
        trade_name: form.trade_name || null,
        state_registration: form.state_registration || null,
        state: form.state || null,
        uses_ciap: form.uses_ciap,
        bloco_k_tipo: form.bloco_k_tipo,
        inventario_mes: form.inventario_mes ? Number(form.inventario_mes) : null,
        inventario_competencia_ref: form.inventario_competencia_ref || null,
        inscricoes_auxiliares: form.inscricoes_auxiliares.filter((i) => i.uf && i.ie),
      };
      const updated = await api.patch<Company>(`/api/v1/companies/${company.id}`, payload);
      onUpdated(updated);
      setOpen(false);
      toast.success("Empresa atualizada com sucesso");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao atualizar empresa");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={
        <Button size="sm" variant="ghost" className="h-7 px-2">
          <PencilIcon className="w-3.5 h-3.5" />
        </Button>
      } />
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar empresa</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>CNPJ</Label>
              <Input value={formatCnpj(form.cnpj)} disabled className="text-muted-foreground" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="edit_state">UF</Label>
              <select
                id="edit_state"
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              >
                <option value="">Selecione</option>
                {ESTADOS.map((uf) => (<option key={uf} value={uf}>{uf}</option>))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <Label htmlFor="edit_name">Razão social *</Label>
            <Input id="edit_name" required value={form.name} onChange={(e) => update("name", e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="edit_trade">Nome fantasia</Label>
              <Input id="edit_trade" value={form.trade_name} onChange={(e) => update("trade_name", e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="edit_ie">Inscrição estadual</Label>
              <Input id="edit_ie" value={form.state_registration} onChange={(e) => update("state_registration", e.target.value)} />
            </div>
          </div>

          <div className="border-t pt-4 space-y-3">
            <p className="text-sm font-semibold">Perfil fiscal (usado para validações)</p>

            <div className="flex items-center gap-2">
              <input
                id="edit_ciap"
                type="checkbox"
                checked={form.uses_ciap}
                onChange={(e) => update("uses_ciap", e.target.checked)}
                className="h-4 w-4"
              />
              <Label htmlFor="edit_ciap" className="text-sm font-normal cursor-pointer">
                Utiliza CIAP — exige Bloco G no arquivo EFD
              </Label>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Bloco K</Label>
                <select
                  value={form.bloco_k_tipo}
                  onChange={(e) => update("bloco_k_tipo", e.target.value as BlocoKTipo)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="nao_aplica">Não se aplica</option>
                  <option value="simplificado">Simplificado</option>
                  <option value="completo">Completo</option>
                </select>
              </div>
              <div className="space-y-1">
                <Label>Mês do inventário (Bloco H)</Label>
                <select
                  value={form.inventario_mes}
                  onChange={(e) => update("inventario_mes", e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="">Não declara</option>
                  {MESES.map((m, i) => (<option key={i + 1} value={i + 1}>{m}</option>))}
                </select>
              </div>
            </div>

            {form.inventario_mes && (
              <div className="space-y-1">
                <Label>Referência do inventário</Label>
                <select
                  value={form.inventario_competencia_ref}
                  onChange={(e) => update("inventario_competencia_ref", e.target.value as InventarioRef | "")}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                >
                  <option value="">Selecione</option>
                  <option value="mes_anterior">Mês anterior</option>
                  <option value="dezembro_ano_anterior">Dezembro do ano anterior</option>
                  <option value="customizado">Customizado</option>
                </select>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Inscrições estaduais auxiliares</Label>
                <Button type="button" size="sm" variant="outline" onClick={addInscricao}>
                  <PlusIcon className="w-3 h-3 mr-1" /> Adicionar
                </Button>
              </div>
              {form.inscricoes_auxiliares.length === 0 ? (
                <p className="text-xs text-muted-foreground">Nenhuma inscrição auxiliar cadastrada.</p>
              ) : (
                <div className="space-y-2">
                  {form.inscricoes_auxiliares.map((insc, idx) => (
                    <div key={idx} className="flex gap-2 items-end">
                      <div className="w-20">
                        <Label className="text-xs">UF</Label>
                        <select
                          value={insc.uf}
                          onChange={(e) => setInscricao(idx, "uf", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-2 py-1 text-sm"
                        >
                          <option value="">--</option>
                          {ESTADOS.map((uf) => (<option key={uf} value={uf}>{uf}</option>))}
                        </select>
                      </div>
                      <div className="flex-1">
                        <Label className="text-xs">Inscrição estadual</Label>
                        <Input
                          value={insc.ie}
                          onChange={(e) => setInscricao(idx, "ie", e.target.value)}
                          placeholder="IE auxiliar"
                        />
                      </div>
                      <Button type="button" size="sm" variant="ghost" onClick={() => removeInscricao(idx)}>
                        <Trash2Icon className="w-3.5 h-3.5 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" disabled={loading}>{loading ? "Salvando..." : "Salvar"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── Modal de conflito CNPJ ─────────────────────────────────────────────────

interface ConflictInfo {
  existing_company_id: string;
  existing_company_name: string;
  existing_company_state: string | null;
  parsed_header: {
    cnpj: string;
    company_name: string;
    state: string;
    year: number;
    month: number;
  };
  file: File;
}

function ConflictDialog({
  conflict,
  onClose,
  onConfirmed,
}: {
  conflict: ConflictInfo | null;
  onClose: () => void;
  onConfirmed: (companyId: string, periodId: string) => void;
}) {
  const [loading, setLoading] = useState(false);

  async function confirmUseExisting() {
    if (!conflict) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", conflict.file);
      formData.append("confirm_existing_company", "true");
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/efd-files/upload-auto`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Erro ao reenviar arquivo");
      }
      const data = await res.json();
      onConfirmed(data.company_id, data.fiscal_period_id);
      toast.success("Arquivo importado para empresa existente");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={!!conflict} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>CNPJ já cadastrado</DialogTitle>
        </DialogHeader>
        {conflict && (
          <div className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              O CNPJ <span className="font-mono">{formatCnpj(conflict.parsed_header.cnpj)}</span>{" "}
              do arquivo SPED já existe no sistema.
            </p>
            <div className="border rounded-lg p-3 bg-muted/30">
              <p className="text-xs text-muted-foreground">Empresa existente:</p>
              <p className="font-medium">{conflict.existing_company_name}</p>
              <p className="text-xs text-muted-foreground">UF: {conflict.existing_company_state ?? "—"}</p>
            </div>
            <div className="border rounded-lg p-3">
              <p className="text-xs text-muted-foreground">No arquivo SPED:</p>
              <p className="font-medium">{conflict.parsed_header.company_name}</p>
              <p className="text-xs text-muted-foreground">
                UF: {conflict.parsed_header.state} ·
                Competência: {conflict.parsed_header.month.toString().padStart(2, "0")}/{conflict.parsed_header.year}
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              Deseja usar a empresa existente para importar este SPED?
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
              <Button onClick={confirmUseExisting} disabled={loading}>
                {loading ? "Importando..." : "Usar empresa existente"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

// ─── Botão de importação direta ─────────────────────────────────────────────

function ImportarSpedButton({ onImported }: { onImported: (companyId: string, periodId: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [conflict, setConflict] = useState<ConflictInfo | null>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/v1/efd-files/upload-auto`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (res.status === 409) {
        const data = await res.json();
        setConflict({ ...data, file });
        return;
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Erro ao importar arquivo");
      }

      const data = await res.json();
      const msg =
        data.company_created && data.fiscal_period_created
          ? "Empresa e competência criadas, arquivo processado"
          : data.fiscal_period_created
          ? "Competência criada e arquivo processado"
          : "Arquivo processado";
      toast.success(msg);
      onImported(data.company_id, data.fiscal_period_id);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <>
      <input ref={inputRef} type="file" accept=".txt" className="hidden" onChange={handleFile} />
      <Button size="sm" variant="outline" onClick={() => inputRef.current?.click()} disabled={loading}>
        <UploadIcon className="w-4 h-4 mr-1" />
        {loading ? "Importando..." : "Importar SPED (auto)"}
      </Button>
      <ConflictDialog
        conflict={conflict}
        onClose={() => setConflict(null)}
        onConfirmed={(c, p) => {
          setConflict(null);
          onImported(c, p);
        }}
      />
    </>
  );
}

export default function EmpresasPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  async function reload() {
    const data = await api.get<Company[]>("/api/v1/companies/");
    setCompanies(data);
  }

  useEffect(() => {
    reload()
      .catch(() => toast.error("Erro ao carregar empresas"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Empresas</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {companies.length} empresa{companies.length !== 1 ? "s" : ""} cadastrada{companies.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex gap-2">
          <ImportarSpedButton
            onImported={async (_company, periodId) => {
              await reload();
              router.push(`/competencias/${periodId}`);
            }}
          />
          <NovaEmpresaDialog onCreated={(c) => setCompanies((prev) => [...prev, c])} />
        </div>
      </div>

      {loading ? (
        <p className="text-muted-foreground text-sm">Carregando...</p>
      ) : companies.length === 0 ? (
        <div className="border rounded-lg p-12 text-center text-muted-foreground">
          <p className="text-sm">Nenhuma empresa cadastrada.</p>
          <p className="text-sm">Use &quot;Importar SPED (auto)&quot; ou &quot;Nova empresa&quot; para começar.</p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>CNPJ</TableHead>
                <TableHead>Razão social</TableHead>
                <TableHead>UF</TableHead>
                <TableHead>CIAP</TableHead>
                <TableHead>Bloco K</TableHead>
                <TableHead>Inv.</TableHead>
                <TableHead>IE aux.</TableHead>
                <TableHead className="w-28" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {companies.map((company) => (
                <TableRow key={company.id} className="hover:bg-muted/40">
                  <TableCell className="font-mono text-sm">{formatCnpj(company.cnpj)}</TableCell>
                  <TableCell className="font-medium">{company.name}</TableCell>
                  <TableCell>{company.state ?? "—"}</TableCell>
                  <TableCell>
                    {company.uses_ciap
                      ? <Badge variant="default" className="text-xs">Sim</Badge>
                      : <span className="text-xs text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <span className="text-xs">
                      {company.bloco_k_tipo === "completo" ? "Completo"
                        : company.bloco_k_tipo === "simplificado" ? "Simplificado"
                        : <span className="text-muted-foreground">—</span>}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {company.inventario_mes ? MESES[company.inventario_mes - 1].slice(0, 3) : "—"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {company.inscricoes_auxiliares?.length ?? 0}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1 items-center">
                      <EditarEmpresaDialog
                        company={company}
                        onUpdated={(updated) =>
                          setCompanies((prev) => prev.map((c) => c.id === updated.id ? updated : c))
                        }
                      />
                      <a href={`/empresas/${company.id}`}>
                        <Button size="sm" variant="outline">Abrir</Button>
                      </a>
                    </div>
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
