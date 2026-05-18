"use client";

import { useState } from "react";
import { api } from "@/lib/api";

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
    <div className="border rounded-lg p-5 space-y-3">
      <div>
        <h2 className="font-semibold text-base">{title}</h2>
        <p className="text-sm text-muted-foreground mt-0.5">{description}</p>
      </div>
      <button
        onClick={handleSeed}
        disabled={status === "loading"}
        className="px-4 py-2 text-sm rounded bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        {status === "loading" ? "Carregando..." : "Executar Seed"}
      </button>
      {status === "ok" && result && (
        <p className="text-sm text-green-600">
          Concluído — {result.inserted} inseridos, {result.updated} atualizados ({result.total} total)
        </p>
      )}
      {status === "error" && (
        <p className="text-sm text-red-600">Erro: {error}</p>
      )}
    </div>
  );
}

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto pt-10">
        <h1 className="text-2xl font-bold mb-1">Administração</h1>
        <p className="text-muted-foreground text-sm mb-8">
          Seeds e configurações do sistema (somente administradores)
        </p>

        <div className="space-y-4">
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

        <div className="mt-10">
          <a href="/" className="text-sm text-muted-foreground hover:underline">
            ← Voltar ao início
          </a>
        </div>
      </div>
    </main>
  );
}
