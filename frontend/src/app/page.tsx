export default function Home() {
  return (
    <main className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto pt-16">
        <h1 className="text-3xl font-bold mb-2">FiscalCheck EFD ICMS/IPI</h1>
        <p className="text-muted-foreground mb-10">
          Plataforma de conferência e ajuste assistido da EFD ICMS/IPI
        </p>

        <div className="space-y-3">
          <a
            href="/empresas"
            className="flex items-center justify-between p-5 border rounded-lg hover:bg-accent transition-colors group"
          >
            <div>
              <h2 className="text-base font-semibold">Empresas</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Cadastre empresas e acesse as competências de cada uma
              </p>
            </div>
            <span className="text-muted-foreground group-hover:translate-x-0.5 transition-transform text-lg">→</span>
          </a>
        </div>

        <div className="mt-12 text-xs text-muted-foreground">
          <p className="font-medium mb-2">Fluxo de trabalho</p>
          <ol className="space-y-1 list-decimal list-inside">
            <li>Cadastre a empresa</li>
            <li>Crie uma competência (mês/ano)</li>
            <li>Faça upload do arquivo TXT da EFD</li>
            <li>Faça upload do PDF de apuração ou importe planilha</li>
            <li>Execute a conferência e revise os achados</li>
          </ol>
        </div>
      </div>
    </main>
  );
}
