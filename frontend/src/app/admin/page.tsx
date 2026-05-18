"use client";

import { useState } from "react";
import Link from "next/link";
import { Users, ArrowRight, Table2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface SeedResult {
  inserted: number;
  updated: number;
  total: number;
}

function SeedCard({
  title,
  description,
  endpoint,
}: {
  title: string;
  description: string;
  endpoint: string;
}) {
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [result, setResult] = useState<SeedResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSeed() {
    setStatus("loading");
    setError(null);
    try {
      const data = await api.post<SeedResult>(endpoint, null);
      setResult(data);
      setStatus("ok");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("error");
    }
  }

  return (
    <Card>
      <CardContent className="py-4 px-5 space-y-3">
        <div>
          <p className="text-sm font-semibold">{title}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        </div>
        <Button size="sm" onClick={handleSeed} disabled={status === "loading"}>
          {status === "loading" ? "Carregando..." : "Executar Seed"}
        </Button>
        {status === "ok" && result && (
          <p className="text-xs text-green-700 dark:text-green-400">
            Concluído — {result.inserted} inseridos, {result.updated} atualizados ({result.total} total)
          </p>
        )}
        {status === "error" && (
          <p className="text-xs text-destructive">Erro: {error}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  return (
    <main className="max-w-2xl mx-auto px-6 pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Administração</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Configurações e seeds do sistema
        </p>
      </div>

      {/* Acesso rápido */}
      <div className="mb-8">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Acesso rápido
        </p>
        <Link href="/admin/usuarios">
          <Card className="hover:bg-accent transition-colors cursor-pointer group">
            <CardContent className="flex items-center gap-4 py-4 px-5">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <Users className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold">Usuários</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Criar e gerenciar usuários com acesso ao sistema
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0 group-hover:translate-x-0.5 transition-transform" />
            </CardContent>
          </Card>
        </Link>
        <Link href="/settings/pr-adjustment-codes">
          <Card className="hover:bg-accent transition-colors cursor-pointer group">
            <CardContent className="flex items-center gap-4 py-4 px-5">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <Table2 className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold">Tabela de Códigos de Ajuste PR</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Visualizar, importar e gerenciar a Tabela 5.1.1 do Paraná
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0 group-hover:translate-x-0.5 transition-transform" />
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Seeds */}
      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Seeds de tabelas de referência
        </p>
        <div className="space-y-3">
          <SeedCard
            title="Tabela de Códigos de Ajuste PR (Tabela 5.1.1)"
            description="Carrega ou atualiza os 230 códigos de ajuste do Paraná com flags de E112/E113."
            endpoint="/api/v1/pr-adjustment-codes/seed"
          />
          <SeedCard
            title="Matriz CFOP × CST"
            description="Carrega as regras de compatibilidade entre CFOP e CST ICMS (entradas, saídas, ST)."
            endpoint="/api/v1/cfop-cst-rules/seed"
          />
        </div>
      </div>

      <div className="mt-10">
        <a href="/" className="text-sm text-muted-foreground hover:underline">← Início</a>
      </div>
    </main>
  );
}
