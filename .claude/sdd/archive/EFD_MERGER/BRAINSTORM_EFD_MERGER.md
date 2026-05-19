---
feature: EFD_MERGER
phase: 0-brainstorm
status: ✅ Confirmed
date: 2026-05-19
author: brainstorm-agent
---

# BRAINSTORM — EFD Merger: SPED Empresa + SPED Contábil

## Ideia Original

> Suporte a dois arquivos SPED por competência (SPED Empresa + SPED Contábil) com merge de blocos configurável, gerando um Arquivo SPED ativo para a conferência fiscal.

---

## Discovery Questions & Respostas

| # | Pergunta | Resposta |
|---|---|---|
| 1 | Caso de uso principal? | SPED Empresa (gestão/estoque, tem Bloco K) + SPED Contábil (ERP, tem C/E corretos e Bloco G/CIAP). Nenhum está completo sozinho. |
| 2 | Nomenclatura dos dois arquivos? | **SPED Empresa** e **SPED Contábil** |
| 3 | Qual arquivo é usado para conferência? | Merged (Arquivo SPED) é parseado e vira o EFD ativo. Os dois originais ficam armazenados para cross-check futuro. |
| 4 | Onde fica a UI? | Botão "Mesclar EFDs" dentro da aba "Arquivo EFD" existente — abre modal de configuração |

---

## Contexto Técnico — O que já existe

### Motor de merge (HTML tool fornecida pelo usuário)
Lógica completa em JavaScript que será portada para Python:
- Parse de arquivos EFD linha a linha (pipe-split)
- Seleção de origem por bloco (A ou B) com toggle
- Resolução de dependências do Bloco 0:
  - Bloco K → importa 0200, 0190 (e unidades) do arquivo B
  - Bloco G → importa 0300, 0305, 0500, 0600 do arquivo B
- Política de conflito para 0200 (mesmo COD_ITEM, descrição/unidade diferente)
- Recálculo do Bloco 9 (9900, 9990, 9999) com totalizadores corretos
- Validação de CNPJ e período compatíveis antes de permitir merge

### Backend existente
- `EfdFile` model: `stored_path`, `parse_status`, `fiscal_period_id`, `original_filename`
- Upload endpoint: `POST /fiscal-periods/{id}/efd-files/upload`
- Parser: `run_full_parse(db, efd_record, stored_path)` — reutilizado sem mudança
- Um `EfdFile` por período hoje → será expandido para N com roles

### Frontend existente
- Aba "Arquivo EFD" em `competencias/[id]/page.tsx` com lista de arquivos + botão upload
- Screenshot mostra UI pronta para receber botão "Mesclar EFDs"

---

## Arquitetura — Três Entidades por Competência

```
Competência
├── EfdFile (role='empresa')   → armazenado, cross-check futuro
├── EfdFile (role='contabil')  → armazenado, cross-check futuro
└── EfdFile (role='merged')    → resultado do merge, parseado,
                                  vira o EFD ativo para conferência
                                  (substitui o arquivo "direto" atual)
```

### Compatibilidade com fluxo atual
- Upload direto de 1 arquivo continua funcionando → role='merged' (sem distinção)
- Upload de 2 arquivos + merge → roles explícitos
- `run_full_parse` não muda — só recebe o `EfdFile` de role='merged'

---

## Abordagem Selecionada: A — Merger integrado, Python backend

### Fluxo do usuário

```
Aba "Arquivo EFD"
  ├── [Enviar EFD (.txt)]  → upload direto (fluxo atual, role='merged')
  └── [Mesclar EFDs]       → abre modal:
        ├── Upload SPED Empresa  (role='empresa')
        ├── Upload SPED Contábil (role='contabil')
        ├── Validação: mesmo CNPJ + mesmo período
        ├── Configuração de blocos: toggle A/B por bloco
        │   Padrão: Bloco K → Empresa, Bloco G → Contábil, demais → Contábil
        ├── [Gerar Arquivo SPED]
        └── Resultado: EfdFile role='merged' → parse → conferência
```

### Novos componentes backend

| Componente | Propósito |
|---|---|
| `EfdFile.file_role` enum | `empresa` / `contabil` / `merged` |
| `services/efd_merger/merger.py` | Motor de merge portado do HTML para Python |
| `services/efd_merger/dependency_resolver.py` | Resolve 0200/0190/0300/0305/0500/0600 |
| `services/efd_merger/bloco9_calculator.py` | Recalcula totalizadores do Bloco 9 |
| `POST /fiscal-periods/{id}/efd-files/merge` | Recebe os dois files + block_config JSON |

### Novo componente frontend

| Componente | Propósito |
|---|---|
| `MergerModal` (inline no EfdTab) | Modal com uploads + toggles de bloco + merge |
| Badge de role na lista de arquivos | Mostra "Empresa", "Contábil" ou "Ativo" |

---

## Configuração de blocos — padrão sugerido

| Bloco | Padrão | Motivo |
|---|---|---|
| Bloco 0 | Mesclado automaticamente | Dependências resolvidas pelo merger |
| Bloco B | Contábil | Apuração do ISSQN |
| Bloco C | Contábil | Documentos fiscais com valores corretos |
| Bloco D | Contábil | Serviços de transporte |
| Bloco E | Contábil | Apuração ICMS/IPI com valores corretos |
| Bloco G | Contábil | CIAP — vem do ERP contábil |
| Bloco H | Empresa | Inventário — vem do sistema de estoque |
| Bloco K | Empresa | Controle de estoque — vem do sistema da empresa |
| Bloco 1 | Contábil | Informações complementares |

---

## Nota sobre Bloco G (CIAP)

Quando Bloco G vem do SPED Contábil, o merger deve importar automaticamente:
- `0300` (bens do ativo imobilizado) + `0305` (filhos)
- `0500` (plano de contas contábeis) referenciado pelo 0300
- `0600` (centros de custo) — todos do Contábil não presentes no Empresa

Essa lógica já está implementada na ferramenta HTML e será portada 1:1.

---

## YAGNI — Fora do escopo

| Feature | Motivo |
|---|---|
| Cross-check cruzado Empresa × Contábil | Feature futura — armazenar os originais já prepara o terreno |
| Política de conflito configurável por UI | Default "preferir SPED Contábil" cobre 90% dos casos |
| Merge de 3+ arquivos | Sem caso de uso identificado |
| Reprocessar merge ao editar config | MVP: gerar novo merge se precisar alterar |
| Diff visual antes/depois do merge | Complexidade alta, não pedido |

---

## Pendência: Correção automática C190×C100

Feature identificada na sessão mas guardada para depois:
- Quando CONF-C190-C100 dispara com 1 filho C190 → gerar sugestão automática de `update_field` em `vl_opr`
- Quando N filhos → mostrar todos para seleção manual

---

## Próximo passo

```bash
/define .claude/sdd/features/BRAINSTORM_EFD_MERGER.md
```
