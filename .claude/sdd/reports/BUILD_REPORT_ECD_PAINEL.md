# BUILD REPORT — Painel ECD/ECF

**Feature:** ECD_PAINEL  
**Data:** 2026-05-07  
**DESIGN:** [DESIGN_ECD_PAINEL.md](../features/DESIGN_ECD_PAINEL.md)  
**Status:** ✅ Concluído

---

## Resumo

| Item | Status |
|------|--------|
| Migrações Supabase (15) | ✅ Aplicadas |
| Tabelas no banco | ✅ 12 tabelas + triggers + RLS |
| Bucket Storage `anexos` | ✅ Criado (privado, 50MB, PDF only) |
| Seed BASSO 2025 | ✅ Inserido |
| Código TypeScript | ✅ 0 erros (`pnpm typecheck`) |
| Testes unitários | ✅ 13/13 passando |
| Edge Functions | ✅ 2 funções criadas |
| n8n Workflow | ✅ JSON exportado |

---

## Arquivos criados

### Bootstrap / Config (13 arquivos)
- `package.json`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`
- `vite.config.ts`, `vitest.config.ts`, `postcss.config.js`
- `index.html`, `.env.example`, `.gitignore`, `components.json`
- `public/favicon.svg`, `supabase/config.toml`

### Styles (1)
- `src/index.css` — Tailwind v4 + tokens OCVEL light/dark

### Lib / Infra (4)
- `src/lib/supabase.ts`, `src/lib/utils.ts`, `src/lib/query-client.ts`, `src/lib/format.ts`

### Tipos / Constantes (4)
- `src/types/database.ts`, `src/types/domain.ts`
- `src/constants/status.ts`, `src/constants/periodos.ts`

### Auth (3)
- `src/contexts/AuthContext.tsx`
- `src/components/auth/RequireAuth.tsx`, `src/components/auth/LoginForm.tsx`

### Hooks (13)
- `useTheme.ts`, `useAuth.ts`, `useEmpresas.ts`
- `useFechamentos.ts`, `useFechamento.ts`
- `useDeclaracoes.ts`, `useDeclaracao.ts`
- `useObservacoes.ts`, `useAnexos.ts`, `useHistorico.ts`
- `useUpdateStatus.ts`, `useCriarObservacao.ts`
- `useUploadAnexo.ts`, `useSignedUrl.ts`, `useCriarFechamentoManual.ts`

### shadcn UI Primitives (13)
- `button`, `card`, `table`, `badge`, `dialog`, `input`, `form`, `select`, `skeleton`, `tabs`, `textarea`, `dropdown-menu`, `label`

### Layout (4)
- `AppShell.tsx`, `Sidebar.tsx`, `TopBar.tsx`, `ThemeToggle.tsx`

### Componentes domínio (20)
- Fechamento: `FechamentoStatusBadge`, `FechamentosTable`, `FechamentoDetailCard`, `FechamentoVersoesList`, `MudarStatusDialog`, `CriarFechamentoManualDialog`
- Declaração: `DeclaracaoStatusBadge`, `DeclaracoesTable`, `DeclaracaoDetailCard`
- Anexo: `AnexosList`, `UploadAnexoDialog`, `AnexoDownloadButton`
- Observação: `ObservacoesList`, `ObservacaoForm`
- Histórico: `HistoricoTimeline`
- Carteira: `CarteiraTable`
- Shared: `EmptyState`, `LoadingSkeleton`, `ErrorState`

### Pages + Roteamento (8)
- `App.tsx`, `main.tsx`
- `LoginPage`, `DashboardFechamentosPage`, `DashboardDeclaracoesPage`
- `FechamentoDetailPage`, `DeclaracaoDetailPage`, `CarteiraPage`, `NotFoundPage`

### Supabase Migrations (15)
1. `extensions` — pgcrypto, citext
2. `empresas` — tabelas `empresas` + `empresa_periodicidade`
3. `usuarios_perfis` — tabela + trigger `on_auth_user_created`
4. `carteira_empresas` — tabela + índices parciais
5. `fechamentos` — `fechamentos` + `fechamento_versoes`
6. `declaracoes` — `declaracoes` + `declaracao_versoes`
7. `anexos` — tabela com `tipo_documento CHECK`
8. `observacoes` — tabela com soft-delete
9. `historico_status` — tabela + `_transicoes_validas` seed
10. `execucoes_integracao` — tabela com idempotência
11. `helper_functions` — `usuario_tem_empresa()`, `auth_perfil()`
12. `rls_policies` — RLS em todas as 12 tabelas
13. `triggers_imutabilidade` — `trg_versao_imutavel`, `trg_validar_transicao_status`
14. `storage_bucket_anexos` — bucket privado + policies
15. `seed_basso_2025` — empresa BASSO + periodicidade ANUAL

### Edge Functions (5)
- `supabase/functions/_shared/supabase-admin.ts`
- `supabase/functions/_shared/idempotency.ts`
- `supabase/functions/_shared/fechamento-creator.ts`
- `supabase/functions/manual-fechamento/index.ts`
- `supabase/functions/signed-url/index.ts`

### n8n (2)
- `n8n/workflows/zeramento_v1.json`
- `n8n/workflows/README.md`

### Testes (3)
- `tests/setup.ts`
- `tests/unit/format.test.ts` (8 testes)
- `tests/unit/status.test.ts` (5 testes)

---

## Desvios em relação ao DESIGN

| Item | Desvio | Motivo |
|------|--------|--------|
| `pnpm-lock.yaml` | Gerado automaticamente | Normal — gerado pelo `pnpm install` |
| Componentes shadcn em `@/` | Movidos para `src/components/ui/` | Bug do shadcn CLI no Windows interpretando alias como path literal |
| `src/lib/format.ts` | `formatDataPt` aceita `null/undefined` | Necessário para colunas opcionais no banco |
| n8n workflow | JSON manual (MCP n8n desconectado) | MCP n8n ficou indisponível; JSON válido pronto para importar |
| RLS SQL tests | Não criados | Requerem `supabase test db` local — documentado no README |

---

## Próximos passos

1. **Deploy Edge Functions:**
   ```bash
   supabase functions deploy manual-fechamento
   supabase functions deploy signed-url
   ```

2. **Configurar variáveis no Supabase:**
   - `SUPABASE_SERVICE_ROLE_KEY` nas secrets das Edge Functions

3. **Importar n8n workflow:**
   - Seguir `n8n/workflows/README.md`
   - Configurar `SUPABASE_FUNCTIONS_URL` e `SUPABASE_SERVICE_ROLE_KEY` no n8n

4. **Iniciar dev local:**
   ```bash
   pnpm dev
   ```

5. **Criar primeiro usuário admin** via Supabase Dashboard → Auth → Users

6. **Testes RLS SQL** (Sprint 2):
   - `tests/rls/carteira.spec.sql`
   - `tests/rls/versao_imutavel.spec.sql`
   - `tests/rls/transicao_status.spec.sql`
