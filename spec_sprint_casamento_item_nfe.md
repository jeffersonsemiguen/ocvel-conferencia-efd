# Spec de Sprint — Casamento de item NF-e × SPED

> **Status:** em execução — entregas 1 e 2 concluídas, ver seção 7.
> **Prioridade:** alta — pré-requisito para corrigir falso positivo já em produção.
> **Origem:** leitura do `nfe_crosscheck` + `efd_icms_ipi_enfoque_declarante_cfop_cst.md`, 06/08/2026.

## Histórico de revisões

| Data | Mudança |
|---|---|
| 06/08/2026 | Versão inicial a partir do cruzamento com o descritor do PVA |
| 06/08/2026 | **Correções de domínio (Jefferson):** valor do item deixou de ser igualdade e virou pertinência a conjunto (5.1); `tipo_item` invertido de validador para validado (4.2); unidade rebaixada a sinal fraco + registros 0190/0220 (5.2) |
| 06/08/2026 | **Correção da âncora (Jefferson):** removida a regra que somava C170 contra o total do documento. O invariante é `Σ C190.VL_OPR`, não `Σ C170.VL_ITEM` (5.1) |
| 06/08/2026 | Entregas 1 e 2 implementadas e testadas |

---

## 1. Problema

Hoje o cruzamento NF-e × SPED acontece **só em nível de documento**
(`services/nfe_crosscheck/matcher.py`). Não há conferência de item. O caso motivador:
o XML do fornecedor traz "parafuso" e o SPED escritura "piscina" para o que deveria ser
o mesmo produto — códigos de item diferentes dos dois lados, ninguém percebe.

Além da lacuna, há um **falso positivo ativo**: a `CONF-NFE-CST-DIVERGENTE` compara
`nfe_documents.cst_first_item` (CST do *primeiro* item do XML) contra o CST *predominante*
dos C190 (`_resolve_c100_predominant_cst`). São duas aproximações distintas do mesmo
documento — em nota multi-item com CST misto, diverge sem existir erro fiscal.

---

## 2. ⚠️ Restrição de projeto: enfoque do declarante

**CFOP e CST não podem ser usados como chave de casamento.** Eles divergem por desenho
entre o XML do fornecedor e a escrituração do declarante. Ver
[efd_icms_ipi_enfoque_declarante_cfop_cst.md](efd_icms_ipi_enfoque_declarante_cfop_cst.md).

| XML do fornecedor | Entrada no SPED | Motivo |
|---|---|---|
| CFOP `6102`, CST `000` | CFOP `2102`, CST `000` | saída interestadual → entrada interestadual |
| CFOP `6102` | CFOP `2403`, CST `060` | mercadoria com ST sem protocolo na UF do declarante |
| CFOP `6102` | CFOP `2551`, CST `090` | destinada a ativo imobilizado |
| CFOP `6102` | CFOP `2556`, CST `090` | destinada a uso e consumo |
| CST final `10`/`30`/`70` | CST final `60` | declarante vê ICMS retido anteriormente por ST |

Consequência de arquitetura: **separar sinais de casamento de alvos de validação.**
Se CFOP for usado para casar, ele não pode mais ser validado. CFOP e CST são alvo, nunca sinal.

---

## 3. O que já existe no banco

**Lado SPED — melhor do que parece.** O cadastro 0200 está persistido em
`EfdBloco0Item` (`efd_bloco0_items`) e traz, por `cod_item`:

| Campo | Uso |
|---|---|
| `cod_barra` | **GTIN/EAN** — sinal de casamento mais forte que existe |
| `cod_ncm` | NCM |
| `descr_item` | descrição |
| `unid_inv` | unidade |
| `tipo_item` | destinação declarada (00 revenda, 07 uso/consumo, 08 imobilizado...) |
| `cod_ant_item` | código anterior — às vezes guarda o código do fornecedor |
| `cest` | CEST |

`EfdC170Item` traz `num_item`, `cod_item`, `cfop`, `cst_icms`, `vl_item`, `vl_opr`,
`vl_bc_icms`, `vl_icms`.

**Lado NF-e — vazio.** `NfeDocument` guarda apenas `xml_path`, `cst_first_item` e
`cfop_first_item`. **Não existe tabela de itens.** É o bloqueio real.

---

## 4. Duas descobertas que mudam o desenho

### 4.1 GTIN é chave quase perfeita

O 0200 tem `cod_barra` e o XML tem `cEAN` / `cEANTrib` em cada `det/prod`. Quando ambos
estão preenchidos e não são `SEM GTIN`, o casamento é **determinístico** — dispensa
pontuação por similaridade. Vale tentar primeiro, sempre.

### 4.2 TIPO_ITEM: usar na direção inversa

O `tipo_item` do 0200 declara a destinação da mercadoria, que é o que determina o CFOP
correto sob enfoque do declarante. **Mas na prática o campo é preenchido como `00` em
quase todo cadastro**, independente da destinação real.

Portanto **não** use `tipo_item` para validar CFOP — geraria falso positivo em massa.
A relação de confiança é a inversa: **o CFOP é o dado confiável, o `tipo_item` é o suspeito.**

Regra útil, com severidade baixa e natureza cadastral:

| Situação | Leitura |
|---|---|
| C170 com CFOP `x551`/`x406` e 0200 com `tipo_item` `00` | cadastro do item errado — é imobilizado |
| C170 com CFOP `x556`/`x407` e 0200 com `tipo_item` `00` | cadastro do item errado — é uso e consumo |

Isso vira achado de **qualidade de cadastro** (`CONF-CAD-TIPO-ITEM`), não erro de
escrituração. Não é prioridade e não deve rodar antes do casamento de item.

---

## 5. Sinais de casamento (com pesos propostos)

Aplicados em cascata, dentro de um par (NF-e, C100) **já casado no nível de documento**:

| # | Sinal | Fonte XML | Fonte SPED | Peso |
|---|---|---|---|---|
| 1 | GTIN | `prod/cEAN`, `cEANTrib` | `0200.cod_barra` | determinístico |
| 2 | Sequência do item | `det/@nItem` | `C170.num_item` | alto |
| 3 | NCM | `prod/NCM` | `0200.cod_ncm` | alto |
| 4 | Valor do item | `prod/vProd` | `C170.vl_item` | médio — ver 5.1 |
| 5 | Quantidade | `prod/qCom` | `C170.qtd` ⚠️ | médio — ver 5.2 |
| 5b | Unidade | `prod/uCom` | `C170.unid` ⚠️ | fraco — ver 5.2 |
| 6 | Similaridade de descrição | `prod/xProd` | `0200.descr_item` | médio |
| 7 | Código do fornecedor | `prod/cProd` | `0200.cod_ant_item` | baixo |

**Sobre a sequência (sinal 2):** você está certo de que na prática o SPED é gerado por
importação do XML, então a ordem costuma se preservar. Mas é heurística, não garantia —
notas editadas à mão, itens excluídos ou reordenados quebram. Proposta: usar sequência
como sinal forte quando a **contagem de itens bate dos dois lados**, e rebaixá-la a
desempate quando não bate.

⚠️ **`C170.qtd` e `C170.unid` não existem no modelo atual.** O registro C170 tem QTD,
UNID, DESCR_COMPL e VL_DESC no leiaute, mas o parser não os persiste. Estender é
pré-requisito dos sinais 5 e 5b.

### 5.1 Valor do item não é comparação de igualdade

O valor do item **diverge legitimamente** entre XML e SPED quando há ST e IPI, porque na
entrada o declarante sem direito a crédito costuma incorporar esses tributos ao custo.

Exemplo real:

```
XML  : CFOP 5403, CST 010, vProd 10,00, vICMSST 2,00, vIPI 1,00   → nota 13,00
SPED : CFOP 1403, CST 060, vl_item 13,00, ST 0,00, IPI 0,00       → nota 13,00
  ou : CFOP 1403, CST 060, vl_item 10,00, ST 0,00, IPI 0,00       → nota 13,00
```

**As duas escriturações são aceitáveis.** Logo, `vl_item` deve ser testado contra um
**conjunto de valores admissíveis**, não contra igualdade:

```
vl_item ∈ { vProd,
            vProd + vICMSST,
            vProd + vIPI,
            vProd + vICMSST + vIPI }        tolerância R$ 0,02
```

**O invariante estável é o total do documento**, que fecha nos dois lados em qualquer das
composições. Ele deve ser a âncora da conferência — o valor do item é sinal de apoio.

Consequência: uma regra do tipo "valor do item difere" **não pode existir isolada**. O que
existe é `CONF-ITEM-VALOR-FORA-COMPOSICAO` — o valor não bate com **nenhuma** composição
admissível, aí sim é erro.

#### A cadeia de ancoragem correta

Independente de como o item foi composto, o total da nota **não muda**. Quem carrega esse
invariante é o **C190**, não o C170:

```
XML vNF  ==  C100.VL_DOC  ==  Σ C190.VL_OPR          ← sempre fecha
Σ C170.VL_ITEM                                        ← NÃO fecha necessariamente
```

No exemplo acima, `Σ C170.VL_ITEM` pode ser 10,00 ou 13,00 e a nota continua 13,00 nos dois
casos. Portanto:

> ⚠️ **Nunca somar C170 para comparar com o total do documento.** Seria falso positivo em
> toda nota com ST ou IPI escriturada sem incorporação ao item.

A conferência do total já existe e está correta:

| Elo | Regra | Situação |
|---|---|---|
| `Σ C190.VL_OPR` vs `C100.VL_DOC` | `CONF-C190-C100` (`engine.py:281`) | ✅ implementada |
| `C100.VL_DOC` vs XML `vNF` | `CONF-NFE-VL-DOC` | ✅ implementada |
| `Σ C170.VL_ITEM` vs total | — | ❌ **não deve existir** |

O C170 serve para conferência **item a item** (produto, quantidade, CFOP, CST). O
fechamento de valor do documento é território do C190.

### 5.2 Unidade de medida é o sinal mais sujo

Dois problemas distintos, que precisam de tratamentos distintos:

**(a) Divergência legítima de unidade.** Compra em `CX` e venda/consumo em `UN` é normal.
O EFD tem mecanismo oficial para isso e **o parser atual ignora os dois registros**:

| Registro | Conteúdo | Status |
|---|---|---|
| `0190` | tabela de unidades de medida usadas (UNID, DESCR) | ❌ não parseado |
| `0220` | fatores de conversão por item (UNID_CONV, FAT_CONV) | ❌ não parseado |

Persistir 0190 e 0220 transforma a conversão CX↔UN de impossível em determinística.
**Isto entra nas entregas.**

**(b) Caos de cadastro.** `UN`, `UN1`, `UND`, `UNI`, `UN12` convivendo para a mesma coisa.
Aqui não há solução automática confiável — proposta:

- normalizar por tabela canônica (maiúsculas, remover dígitos finais, mapear
  `UND`/`UNI`/`UN1` → `UN`, `CX`/`CAIXA` → `CX`, etc.);
- usar unidade **apenas como corroboração**, nunca para reprovar um casamento;
- gerar achado separado `CONF-CAD-UNID-NAO-CANONICA` listando as variantes encontradas no
  0190 — é problema de cadastro do cliente, e mostrar a lista já tem valor por si.

Unidade **nunca** deve, sozinha, quebrar um casamento nem gerar divergência fiscal.

---

## 6. Validações habilitadas depois do casamento

| Código | Verificação |
|---|---|
| `CONF-ITEM-PRODUTO-DIVERGENTE` | NCM incompatível ou descrição sem relação — o caso parafuso × piscina |
| `CONF-ITEM-VALOR-FORA-COMPOSICAO` | `vl_item` não bate com nenhuma composição admissível (seção 5.1) |
| `CONF-ITEM-QTD` | quantidade divergente após aplicar fator de conversão do 0220 |
| `CONF-CAD-TIPO-ITEM` | CFOP indica imobilizado/uso e consumo mas 0200 diz `00` (seção 4.2) — cadastral, severidade baixa |
| `CONF-CAD-UNID-NAO-CANONICA` | variantes de unidade no 0190 (`UN`/`UND`/`UNI`/`UN1`) — cadastral |
| `CONF-ITEM-CST-ST` | CST `10`/`30`/`70` no XML sem virar `60` na entrada |
| `CONF-ITEM-CST-ORIGEM` | dígito de origem do CST incoerente entre XML e SPED |
| `CONF-ITEM-NAO-CASADO` | item do XML sem correspondente no C170 e vice-versa |

A `CONF-NFE-CST-DIVERGENTE` atual deve ser **substituída** pelas de item — hoje ela
compara aproximações e gera ruído.

---

## 7. Entregas

| # | Entrega | Status |
|---|---|---|
| 1 | Modelo `NfeItem` + migration `a7b8c9d0e1f2` | ✅ feito, migration aplicada |
| 2 | Parser de XML populando `nfe_items` | ✅ feito e testado |
| 3 | Parser de C170 para `qtd`, `unid`, `descr_compl`, `vl_desc` | ✅ feito e testado |
| 4 | Modelos e parser dos registros `0190` e `0220` | ✅ feito e testado |
| 5 | `nfe_crosscheck/item_matcher.py` — cascata da seção 5 + score | ⬜ pendente |
| 6 | Regras da seção 6 em `rules/itens.py` | ⬜ pendente |
| 7 | Reprocessamento dos XMLs já persistidos | ⬜ pendente |

Detalhes das entregas concluídas:

**1 — `NfeItem`** ([`app/models/nfe_item.py`](backend/app/models/nfe_item.py)). 29 colunas.
Guarda `u_com`/`q_com` e `u_trib`/`q_trib` separados (a unidade tributável é a ponte quando
o comercial vem em caixa), e `v_bc_icms_st`/`v_icms_st`/`cst_ipi`/`v_ipi` — sem estes não
se monta as composições admissíveis da seção 5.1. `cst_icms` é `String(4)` para acomodar
CSOSN. Índice único em `(nfe_document_id, n_item)` e composto em `(c_ean, ncm)`.

**2 — parser** ([`nfe_xml_parser.py`](backend/app/services/nfe_parser/nfe_xml_parser.py)).
`_extract_items` percorre os `<det>` preservando a ordem do XML (sinal de sequência).
`_icms_values` achata o grupo `<ICMS>`, cujo filho concreto varia (`ICMS00`, `ICMS10`,
`ICMSSN101`...), lendo CSOSN no mesmo campo do CST. `_ipi_values` trata `<IPITrib>` e
`<IPINT>`. `_gtin` normaliza `SEM GTIN` para `None` — sem isso dois produtos sem código de
barras casariam entre si por "GTIN igual".
Persistência em [`nfe_persist_service.py`](backend/app/services/nfe_parser/nfe_persist_service.py).

**3 e 4 — lado da EFD** (migration `b8c9d0e1f2a3`).
Modelos `EfdBloco0Unit` (0190) e `EfdBloco0ItemConv` (0220) em
[`efd_bloco0.py`](backend/app/models/efd_bloco0.py). O 0220 é filho do 0200, então o parser
passou a manter o contexto do item corrente (`current_0200_cod_item`) para vincular a
conversão ao `COD_ITEM` certo — sem isso o fator ficaria órfão.

C170 ganhou `descr_compl`, `qtd`, `unid` e `vl_desc` (posições 4, 5, 6 e 8 do leiaute), e
`cst_icms` foi para `String(4)`, fechando a mesma lacuna de CSOSN que a migration
`9f3e7c21ab54` já havia corrigido no C190 e D190.

Validado com um trecho de EFD contendo `0190` com quatro variantes de unidade
(`UN`/`CX`/`UND`/`UNI`), um `0220` de `CX` com fator 12, e um C170 de 1 CX — a conversão
resulta em 12 UN, batendo com o `qTrib` do XML.

**Nota sobre dados existentes:** NF-e importadas antes desta mudança não têm itens. O
`xml_path` está guardado, então dá para repopular sem novo upload (entrega 7). EFDs já
processadas também precisam ser reprocessadas para popular 0190/0220 e os campos novos
do C170.

## 8. Fora de escopo

Casamento de item em notas de **saída** (o cliente é o emitente, códigos batem por
construção); NF-e de serviço; CT-e.

## 9. Achado lateral

`matcher.py:95-112` — `_days_nfe` e `_days_c100` calculam `ano*365 + mês*31 + dia`, que
não é diferença real de datas. Entre 31/12 e 01/01 a conta resulta em 24 "dias" para um
intervalo de 1 dia. Afeta só o desempate do fallback, mas pode escolher o candidato errado
na virada de ano. Trocar por `datetime.date` e subtração real.
