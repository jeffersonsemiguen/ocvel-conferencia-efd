"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { PlusIcon } from "lucide-react";
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
import type { Company } from "@/lib/types";

const ESTADOS = [
  "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
  "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO",
];

function formatCnpj(cnpj: string) {
  return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

function NovaEmpresaDialog({ onCreated }: { onCreated: (c: Company) => void }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    cnpj: "",
    name: "",
    trade_name: "",
    state_registration: "",
    state: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const company = await api.post<Company>("/api/v1/companies", {
        ...form,
        trade_name: form.trade_name || null,
        state_registration: form.state_registration || null,
        state: form.state || null,
      });
      onCreated(company);
      setOpen(false);
      setForm({ cnpj: "", name: "", trade_name: "", state_registration: "", state: "" });
      toast.success("Empresa cadastrada com sucesso");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao cadastrar empresa");
    } finally {
      setLoading(false);
    }
  }

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button size="sm"><PlusIcon className="w-4 h-4 mr-1" />Nova empresa</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova empresa</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-1">
            <Label htmlFor="cnpj">CNPJ *</Label>
            <Input
              id="cnpj"
              placeholder="00000000000000"
              maxLength={14}
              required
              value={form.cnpj}
              onChange={set("cnpj")}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="name">Razão social *</Label>
            <Input
              id="name"
              placeholder="Nome da empresa"
              required
              value={form.name}
              onChange={set("name")}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="trade_name">Nome fantasia</Label>
            <Input
              id="trade_name"
              placeholder="Nome fantasia (opcional)"
              value={form.trade_name}
              onChange={set("trade_name")}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="state">UF</Label>
              <select
                id="state"
                value={form.state}
                onChange={set("state")}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                <option value="">Selecione</option>
                {ESTADOS.map((uf) => (
                  <option key={uf} value={uf}>{uf}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="ie">Inscrição estadual</Label>
              <Input
                id="ie"
                placeholder="IE"
                value={form.state_registration}
                onChange={set("state_registration")}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Salvando..." : "Salvar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function EmpresasPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<Company[]>("/api/v1/companies")
      .then(setCompanies)
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
        <NovaEmpresaDialog onCreated={(c) => setCompanies((prev) => [...prev, c])} />
      </div>

      {loading ? (
        <p className="text-muted-foreground text-sm">Carregando...</p>
      ) : companies.length === 0 ? (
        <div className="border rounded-lg p-12 text-center text-muted-foreground">
          <p className="text-sm">Nenhuma empresa cadastrada.</p>
          <p className="text-sm">Clique em &quot;Nova empresa&quot; para começar.</p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>CNPJ</TableHead>
                <TableHead>Razão social</TableHead>
                <TableHead>Nome fantasia</TableHead>
                <TableHead>UF</TableHead>
                <TableHead>IE</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-28" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {companies.map((company) => (
                <TableRow key={company.id} className="cursor-pointer hover:bg-muted/40">
                  <TableCell className="font-mono text-sm">
                    {formatCnpj(company.cnpj)}
                  </TableCell>
                  <TableCell className="font-medium">{company.name}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {company.trade_name ?? "—"}
                  </TableCell>
                  <TableCell>{company.state ?? "—"}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {company.state_registration ?? "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={company.is_active ? "default" : "secondary"}>
                      {company.is_active ? "Ativa" : "Inativa"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <a href={`/empresas/${company.id}`}>
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
