# EFD Block Overview — Visao Geral dos Blocos

> **MCP Validated**: 2026-05-18
> **Fonte**: Guia Pratico EFD-ICMS/IPI — SPED/RFB (versao 3.x)

## Os 10 Blocos do EFD-ICMS/IPI

O arquivo EFD e organizado em blocos logicos. Cada bloco possui registros de abertura (X001), registros de movimento e encerramento (X990).

---

## Bloco 0 — Abertura, Identificacao e Referencias

**Obrigatorio**: Sim (sempre presente)

| Registro | Descricao | Obrigatorio |
|----------|-----------|-------------|
| 0000 | Abertura do arquivo e identificacao da entidade | Sim |
| 0001 | Abertura do Bloco 0 | Sim |
| 0002 | Classificacao do estabelecimento | Condicional |
| 0005 | Dados complementares da entidade | Sim |
| 0015 | Dados do contribuinte substituto / terceiro | Condicional |
| 0100 | Dados do contabilista | Condicional |
| 0150 | Tabela de cadastro do participante | Condicional |
| 0175 | Alteracao da tabela de cadastro de participantes | Condicional |
| 0190 | Identificacao das unidades de medida | Condicional |
| 0200 | Tabela de identificacao do item (produto/servico) | Condicional |
| 0205 | Alteracoes do item | Condicional |
| 0206 | Codigo de produto conforme ANVISA | Condicional |
| 0210 | Consumo especifico padronizado | Condicional |
| 0220 | Fatores de conversao de unidades | Condicional |
| 0300 | Cadastro de bens ou componentes do ativo imobilizado | Condicional |
| 0305 | Informacoes do bem | Condicional |
| 0400 | Tabela de natureza da operacao/prestacao | Condicional |
| 0450 | Tabela de informacoes complementares do documento | Condicional |
| 0460 | Tabela de observacoes do lancamento fiscal | Condicional |
| 0500 | Plano de contas contabeis | Condicional |
| 0600 | Centro de custos | Condicional |
| 0990 | Encerramento do Bloco 0 | Sim |

---

## Bloco A — Documentos Fiscais de Servicos (NFS-e)

**Obrigatorio**: Condicional — apenas contribuintes com prestacao/tomada de servicos com NFS-e

Registros principais:
- A001: Abertura
- A010: Identificacao do estabelecimento
- A100: Nota Fiscal de Servicos Eletronicas — cabecalho
- A110: Informacoes complementares dos documentos
- A111: Processo referenciado
- A120: Resumo diario dos documentos emitidos NFS-e
- A170: Itens do documento
- A990: Encerramento

---

## Bloco B — Reservado

**Obrigatorio**: Nao. Bloco reservado para uso futuro pela RFB. Nao deve conter registros de movimento.

---

## Bloco C — Documentos Fiscais de Mercadorias

**Obrigatorio**: Sim (para contribuintes com operacoes de mercadorias)

Abrange: NF-e (modelo 55), NF (modelo 1/1A), CT-e de carga (quando transportador).

| Registro | Descricao |
|----------|-----------|
| C001 | Abertura do Bloco C |
| C010 | Identificacao do estabelecimento |
| C100 | Nota fiscal — cabecalho |
| C101 | Informacao complementar da NF-e (devolucao) |
| C105 | Operacoes com ICMS ST (combustiveis) |
| C110 | Informacoes complementares da NF |
| C111 | Processo referenciado |
| C112 | Documento de arrecadacao referenciado |
| C113 | Documento fiscal referenciado |
| C114 | Cupom fiscal referenciado |
| C115 | Local de coleta e entrega |
| C120 | Complemento da NF de importacao |
| C130 | ISSQN, IRRF e INSS |
| C140 | Fatura/duplicata |
| C141 | Vencimentos da fatura |
| C160 | Volumes transportados |
| C165 | Informacoes sobre combustiveis (CIDE) |
| C170 | Itens da nota fiscal |
| C171 | Armazenamento de combustiveis |
| C172 | Credito de PIS/COFINS |
| C173 | Operacoes com medicamentos |
| C174 | Operacoes com armas de fogo |
| C175 | Operacoes com veiculos novos |
| C176 | Ressarcimento ICMS ST |
| C177 | Codigo de produto conforme ANVISA |
| C178 | Informacoes de embalagens |
| C179 | Complemento de informacoes ST |
| C190 | Registro analitico do documento (CST+CFOP+Aliq) |
| C191 | Informacoes de PIS/COFINS da NF |
| C195 | Observacoes do lancamento fiscal |
| C197 | Outras obrigacoes tributarias, ajustes e informacoes de valores provenientes de doc fiscal |
| C990 | Encerramento do Bloco C |

---

## Bloco D — Documentos Fiscais de Servicos de Transporte (CT-e)

**Obrigatorio**: Condicional — empresas prestadoras de servicos de transporte

Abrange: CT-e (modelo 57), CT-e OS (modelo 67), NF de Servico de Transporte (modelo 7), etc.

Estrutura similar ao Bloco C: D001, D100, D110, D130, D140, D150, D160, D161, D162, D170, D180, D190, D195, D197, D990.

---

## Bloco E — Apuracao do ICMS e do IPI

**Obrigatorio**: Sim

| Registro | Descricao |
|----------|-----------|
| E001 | Abertura do Bloco E |
| E010 | Identificacao do estabelecimento |
| E100 | Periodo de apuracao do ICMS |
| E110 | Apuracao do ICMS — operacoes proprias |
| E111 | Ajuste/beneficio/deducao da apuracao do ICMS |
| E112 | Informacoes adicionais dos ajustes da apuracao do ICMS |
| E113 | Documentos do ajuste da apuracao do ICMS |
| E115 | Informacoes adicionais da apuracao do ICMS |
| E116 | Obrigacoes do ICMS a recolher |
| E200 | Periodo de apuracao do ICMS ST |
| E210 | Apuracao do ICMS ST |
| E220 | Ajuste da apuracao do ICMS ST |
| E230 | Informacoes adicionais dos ajustes do ICMS ST |
| E240 | Documentos do ajuste da apuracao do ICMS ST |
| E250 | Obrigacoes do ICMS ST a recolher |
| E300 | Periodo de apuracao do ICMS — substituicao tributaria |
| E310 | Apuracao do ICMS — contribuicao do substituto tributario |
| E500 | Periodo de apuracao do IPI |
| E510 | Consolidacao dos valores do IPI por CFOP e CST |
| E520 | Apuracao do IPI |
| E530 | Ajustes da apuracao do IPI |
| E531 | Informacoes adicionais dos ajustes da apuracao do IPI |
| E990 | Encerramento do Bloco E |

---

## Bloco G — CIAP (Controle de Credito ICMS — Ativo Permanente)

**Obrigatorio**: Condicional — contribuintes com apropriacao de credito ICMS sobre ativo imobilizado

Registros: G001, G005, G010, G020, G025, G030, G035, G040, G050, G070, G990.

---

## Bloco H — Inventario Fisico

**Obrigatorio**: Condicional — obrigatorio quando ha inventario no periodo

| Registro | Descricao |
|----------|-----------|
| H001 | Abertura do Bloco H |
| H005 | Totais do inventario e dados dos estoques escriturados |
| H010 | Inventario — itens individuais |
| H020 | Informacoes sobre o item inventariado |
| H030 | Informacoes sobre os itens fabricados pelo proprio estabelecimento |
| H990 | Encerramento do Bloco H |

---

## Bloco K — Controle de Producao e Estoque

**Obrigatorio**: Condicional — perfil A obrigatorio para industriais; perfis B/C opcional

Registros: K001, K010, K100, K200, K210, K215, K220, K230, K235, K250, K255, K260, K265, K270, K275, K280, K290, K291, K292, K300, K301, K302, K990.

---

## Bloco 9 — Controle e Encerramento do Arquivo

**Obrigatorio**: Sim (sempre presente)

| Registro | Descricao |
|----------|-----------|
| 9001 | Abertura do Bloco 9 |
| 9900 | Registros do arquivo — listagem por tipo e quantidade |
| 9990 | Encerramento do Bloco 9 |
| 9999 | Encerramento do arquivo (total de linhas) |

O registro 9900 e repetido para cada tipo de registro presente no arquivo, informando a contagem de linhas.

---

## See Also

- [concepts/file-structure.md](file-structure.md) — formato pipe, encoding, hierarquia
- [patterns/register-c100.md](../patterns/register-c100.md) — layout completo do C100
- [patterns/register-e110.md](../patterns/register-e110.md) — layout completo do E110
