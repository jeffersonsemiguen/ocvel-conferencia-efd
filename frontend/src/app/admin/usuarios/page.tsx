"use client";

import { useEffect, useState } from "react";
import { UserPlus, ShieldCheck, User, Ban } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface UserRow {
  id: string;
  name: string;
  email: string;
  role: "admin" | "analyst";
  is_active: boolean;
}

interface CreateForm {
  name: string;
  email: string;
  password: string;
  role: "admin" | "analyst";
}

const EMPTY_FORM: CreateForm = { name: "", email: "", password: "", role: "analyst" };

export default function UsuariosPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CreateForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  async function load() {
    try {
      const data = await api.get<UserRow[]>("/auth/users");
      setUsers(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    setCreating(true);
    try {
      await api.post<UserRow>("/auth/users", form);
      setForm(EMPTY_FORM);
      setShowForm(false);
      await load();
    } catch (e: unknown) {
      setFormError(e instanceof Error ? e.message : String(e));
    } finally {
      setCreating(false);
    }
  }

  async function handleDeactivate(userId: string) {
    if (!confirm("Desativar este usuário?")) return;
    try {
      await api.patch(`/auth/users/${userId}/deactivate`, {});
      await load();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-6 pt-10 pb-20">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Usuários</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Gerencie quem tem acesso ao FiscalCheck
          </p>
        </div>
        <Button onClick={() => setShowForm((v) => !v)} size="sm">
          <UserPlus className="w-4 h-4 mr-1.5" />
          Novo usuário
        </Button>
      </div>

      {/* Formulário de criação */}
      {showForm && (
        <Card className="mb-6 border-primary/30">
          <CardHeader className="pb-3">
            <p className="text-sm font-semibold">Novo usuário</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="name">Nome</Label>
                <Input
                  id="name"
                  placeholder="João Silva"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="joao@empresa.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Senha</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Mínimo 6 caracteres"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                  minLength={6}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="role">Perfil</Label>
                <Select
                  value={form.role}
                  onValueChange={(v) => setForm({ ...form, role: v as "admin" | "analyst" })}
                >
                  <SelectTrigger id="role">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="analyst">Analista</SelectItem>
                    <SelectItem value="admin">Administrador</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formError && (
                <p className="sm:col-span-2 text-sm text-destructive">{formError}</p>
              )}

              <div className="sm:col-span-2 flex gap-2">
                <Button type="submit" disabled={creating} size="sm">
                  {creating ? "Criando..." : "Criar usuário"}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => { setShowForm(false); setForm(EMPTY_FORM); setFormError(null); }}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Lista de usuários */}
      {loading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : error ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : (
        <Card>
          <CardContent className="p-0">
            {users.length === 0 ? (
              <p className="px-5 py-8 text-sm text-muted-foreground text-center">
                Nenhum usuário cadastrado.
              </p>
            ) : (
              <ul className="divide-y">
                {users.map((u) => (
                  <li
                    key={u.id}
                    className="flex items-center gap-4 px-5 py-4"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                      u.is_active ? "bg-primary/20" : "bg-muted"
                    }`}>
                      {u.role === "admin"
                        ? <ShieldCheck className="w-4 h-4 text-foreground/70" />
                        : <User className="w-4 h-4 text-foreground/70" />}
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${!u.is_active && "line-through text-muted-foreground"}`}>
                        {u.name}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">{u.email}</p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        u.role === "admin"
                          ? "bg-primary/20 text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                        style={u.role === "admin" ? { color: "oklch(0.2178 0 0)" } : {}}>
                        {u.role === "admin" ? "Admin" : "Analista"}
                      </span>

                      {!u.is_active && (
                        <span className="text-xs text-muted-foreground">inativo</span>
                      )}

                      {u.is_active && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 px-2 text-muted-foreground hover:text-destructive"
                          onClick={() => handleDeactivate(u.id)}
                        >
                          <Ban className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      <div className="mt-8">
        <a href="/admin" className="text-sm text-muted-foreground hover:underline">
          ← Administração
        </a>
      </div>
    </main>
  );
}
