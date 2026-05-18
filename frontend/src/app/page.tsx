import Link from "next/link";
import { LayoutDashboard, Building2, Settings, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const shortcuts = [
  {
    href: "/dashboard",
    icon: LayoutDashboard,
    label: "Dashboard",
    description: "Visão geral das conferências — alertas e críticos por empresa",
  },
  {
    href: "/empresas",
    icon: Building2,
    label: "Empresas",
    description: "Cadastre empresas e acesse as competências de cada uma",
  },
  {
    href: "/admin",
    icon: Settings,
    label: "Administração",
    description: "Seeds de tabelas de referência (códigos de ajuste, CFOP×CST)",
  },
];

const steps = [
  "Cadastre a empresa",
  "Crie uma competência (mês/ano)",
  "Faça upload do arquivo TXT da EFD",
  "Faça upload do PDF de apuração ou importe planilha",
  "Execute a conferência e revise os achados",
];

export default function Home() {
  return (
    <main className="max-w-2xl mx-auto px-6 pt-14 pb-20">
      <div className="mb-10">
        <h1 className="text-2xl font-bold tracking-tight">FiscalCheck EFD</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Conferência e ajuste assistido da EFD ICMS/IPI
        </p>
      </div>

      <div className="space-y-2 mb-12">
        {shortcuts.map(({ href, icon: Icon, label, description }) => (
          <Link key={href} href={href}>
            <Card className="hover:bg-accent transition-colors cursor-pointer group">
              <CardContent className="flex items-center gap-4 py-4 px-5">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <Icon className="w-4 h-4 text-primary-foreground" style={{ color: "oklch(0.2178 0 0)" }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold">{label}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0 group-hover:translate-x-0.5 transition-transform" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="border rounded-lg p-5">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Fluxo de trabalho
        </p>
        <ol className="space-y-2">
          {steps.map((step, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-primary/20 text-primary-foreground text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5"
                style={{ color: "oklch(0.2178 0 0)" }}>
                {i + 1}
              </span>
              <span className="text-sm text-muted-foreground">{step}</span>
            </li>
          ))}
        </ol>
      </div>
    </main>
  );
}
