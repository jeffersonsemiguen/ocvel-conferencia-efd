# EFD ICMS/IPI — Regras de Enfoque do Declarante para CFOP e CST_ICMS

> **Objetivo**: orientar a parametrização de entradas no EFD ICMS/IPI quando o documento fiscal recebido foi emitido com CFOP/CST de saída pelo fornecedor, mas a escrituração deve refletir a operação sob a ótica do declarante/destinatário.

> **Atenção**: este material é uma orientação de parametrização. A regra final deve observar a legislação da UF, o regime tributário do declarante, o direito ao crédito, a destinação da mercadoria e eventuais regimes especiais.

---

## 1. Conceito central: enfoque do declarante

No EFD ICMS/IPI, o documento fiscal de entrada deve ser escriturado **sob o enfoque do declarante**.

Isso significa que o destinatário **não deve copiar automaticamente** o CFOP, CST ou CSOSN da NF-e do fornecedor. O destinatário deve avaliar:

1. **Tipo da operação**: entrada ou saída.
2. **Origem/localidade da operação**: interna, interestadual ou exterior.
3. **Destinação da mercadoria no estabelecimento**:
   - industrialização ou produção rural;
   - comercialização/revenda;
   - ativo imobilizado;
   - uso ou consumo;
   - prestação de serviço;
   - devolução, remessa, retorno, bonificação, etc.
4. **Tratamento tributário sob a ótica do declarante**:
   - há direito a crédito?
   - houve ICMS-ST retido anteriormente?
   - o declarante é substituto ou substituído?
   - a operação é isenta, não tributada, suspensa, diferida ou outras?
5. **Origem da mercadoria para CST_ICMS**:
   - o primeiro dígito do CST pode mudar conforme a posição do declarante.
   - Exemplo: mercadoria importada comprada no mercado interno pode ser escriturada com origem `2`, e não com origem `1`, se o declarante não foi o importador direto.

---

## 2. Regra-base para CFOP de entrada

O CFOP da NF-e do fornecedor é um CFOP de **saída**. Na entrada do EFD, o declarante deve informar um CFOP de **entrada**.

| Situação | CFOP de entrada |
|---|---|
| Remetente da mesma UF | CFOP iniciado por `1` |
| Remetente de outra UF | CFOP iniciado por `2` |
| Operação de entrada do exterior | CFOP iniciado por `3` |

A conversão **não é mecânica**. O primeiro dígito é apenas o ponto de partida. O código completo deve ser definido pela **destinação da mercadoria** e pelo **tratamento tributário**.

Exemplo:

| NF-e do fornecedor | Destinação no declarante | Entrada no EFD |
|---|---|---|
| `5.403` | compra para revenda com ICMS-ST retido | `1.403` |
| `5.403` | compra para uso/consumo com ICMS-ST retido | `1.407` |
| `5.403` | compra para ativo imobilizado com ICMS-ST retido | `1.406` |

---

## 3. Regra-base para CST_ICMS

O CST_ICMS possui três dígitos na forma `ABB`:

- `A` = origem da mercadoria;
- `BB` = tributação pelo ICMS.

Exemplo:

| CST | Interpretação |
|---|---|
| `010` | origem `0` + tributada com ICMS-ST |
| `060` | origem `0` + ICMS cobrado anteriormente por ST ou antecipação com encerramento |
| `090` | origem `0` + outras |
| `260` | origem `2` + ICMS cobrado anteriormente por ST ou antecipação com encerramento |

Na entrada, o CST deve refletir a situação tributária **do declarante**. Por isso, em muitas operações de ST, a NF-e de saída pode vir com CST final `10`, `30` ou `70`, mas a entrada do destinatário deve ser escriturada com CST final `60`.

---

## 4. Regra principal para ICMS-ST

Quando o fornecedor emite a NF-e como **contribuinte substituto**, normalmente com CST final:

- `10` — tributada com ICMS devido por substituição tributária;
- `30` — isenta/não tributada com ICMS devido por substituição tributária;
- `70` — redução de base com ICMS devido por substituição tributária;

e o destinatário recebe a mercadoria com ICMS-ST já retido/cobrado, o declarante passa a enxergar a mercadoria como **ICMS cobrado anteriormente por substituição tributária**.

Assim, na entrada:

```text
CST final 10 / 30 / 70 na saída do fornecedor
→ CST final 60 na entrada do destinatário, quando houver ST retida/cobrada anteriormente
```

### Exemplo clássico

```text
Fornecedor:
CFOP 5.403
CST 010

Declarante:
Compra interna para revenda de mercadoria sujeita à ST, com imposto retido

Entrada no EFD:
CFOP 1.403
CST 060
```

---

## 5. Matriz prática: operações com ICMS-ST

### 5.1 Entrada interna — remetente da mesma UF

| NF-e do fornecedor | Condição da mercadoria | Destinação no declarante | CFOP de entrada | CST_ICMS de entrada |
|---|---|---|---|---|
| `5.401`, `5.403` | ST como substituto | industrialização ou produção rural | `1.401` | `x60` |
| `5.401`, `5.403` | ST como substituto | comercialização/revenda | `1.403` | `x60` |
| `5.401`, `5.403` | ST como substituto | ativo imobilizado | `1.406` | `x60` |
| `5.401`, `5.403` | ST como substituto | uso ou consumo | `1.407` | `x60` |
| `5.405` | ST já cobrada anteriormente/substituído | comercialização/revenda | `1.403` | `x60` |
| `5.405` | ST já cobrada anteriormente/substituído | ativo imobilizado | `1.406` | `x60` |
| `5.405` | ST já cobrada anteriormente/substituído | uso ou consumo | `1.407` | `x60` |

> `x` representa o primeiro dígito da origem da mercadoria, definido sob o enfoque do declarante.

### 5.2 Entrada interestadual — remetente de outra UF

| NF-e do fornecedor | Condição da mercadoria | Destinação no declarante | CFOP de entrada | CST_ICMS de entrada |
|---|---|---|---|---|
| `6.401`, `6.403` | ST como substituto | industrialização ou produção rural | `2.401` | `x60` |
| `6.401`, `6.403` | ST como substituto | comercialização/revenda | `2.403` | `x60` |
| `6.401`, `6.403` | ST como substituto | ativo imobilizado | `2.406` | `x60` |
| `6.401`, `6.403` | ST como substituto | uso ou consumo | `2.407` | `x60` |
| `6.404` | ST já retida anteriormente | comercialização/revenda | `2.403` | `x60` |
| `6.404` | ST já retida anteriormente | ativo imobilizado | `2.406` | `x60` |
| `6.404` | ST já retida anteriormente | uso ou consumo | `2.407` | `x60` |

---

## 6. Matriz prática: operações sem ICMS-ST

Quando a operação não está sujeita à substituição tributária, o CFOP de entrada deve ser escolhido pela destinação do item.

### 6.1 Entrada interna

| NF-e do fornecedor | Destinação no declarante | CFOP de entrada | CST_ICMS de entrada |
|---|---|---|---|
| `5.101` ou `5.102` | industrialização ou produção rural | `1.101` | conforme tributação e direito ao crédito |
| `5.101` ou `5.102` | comercialização/revenda | `1.102` | conforme tributação e direito ao crédito |
| `5.101` ou `5.102` | ativo imobilizado | `1.551` | conforme direito ao crédito |
| `5.101` ou `5.102` | uso ou consumo | `1.556` | normalmente `x90` se tributada e sem crédito |
| `5.101` ou `5.102` | prestação de serviço sujeita ao ICMS | `1.126` | conforme tributação e direito ao crédito |

### 6.2 Entrada interestadual

| NF-e do fornecedor | Destinação no declarante | CFOP de entrada | CST_ICMS de entrada |
|---|---|---|---|
| `6.101` ou `6.102` | industrialização ou produção rural | `2.101` | conforme tributação e direito ao crédito |
| `6.101` ou `6.102` | comercialização/revenda | `2.102` | conforme tributação e direito ao crédito |
| `6.101` ou `6.102` | ativo imobilizado | `2.551` | conforme direito ao crédito |
| `6.101` ou `6.102` | uso ou consumo | `2.556` | normalmente `x90` se tributada e sem crédito |
| `6.101` ou `6.102` | prestação de serviço sujeita ao ICMS | `2.126` | conforme tributação e direito ao crédito |

---

## 7. Regras de transformação de CST mais comuns

### 7.1 CST de ST na saída do fornecedor

| CST na NF-e de saída | Leitura no fornecedor | CST na entrada do declarante |
|---|---|---|
| `x10` | tributada + ICMS-ST devido pelo substituto | `x60`, se o imposto veio retido/cobrado anteriormente |
| `x30` | isenta/não tributada + ICMS-ST devido pelo substituto | `x60`, se o imposto veio retido/cobrado anteriormente |
| `x70` | redução de base + ICMS-ST devido pelo substituto | `x60`, se o imposto veio retido/cobrado anteriormente |
| `x60` | ICMS já cobrado anteriormente por ST | `x60`, se a condição se mantém para o declarante |

### 7.2 Compra tributada para uso e consumo

Se a mercadoria veio tributada, mas a entrada é para **uso ou consumo** e não há direito a crédito de ICMS, o declarante normalmente deve escriturar o CST final como `90`.

Exemplo:

```text
Fornecedor:
CFOP 5.102
CST 000

Declarante:
Compra para uso ou consumo, sem direito a crédito

Entrada no EFD:
CFOP 1.556
CST 090
```

### 7.3 Compra para revenda com direito a crédito

Se a mercadoria foi adquirida para revenda ou industrialização e há direito ao crédito, a entrada normalmente preserva a tributação própria aplicável.

Exemplo:

```text
Fornecedor:
CFOP 5.102
CST 000

Declarante:
Compra interna para revenda com direito a crédito

Entrada no EFD:
CFOP 1.102
CST 000
```

### 7.4 Mercadoria importada adquirida no mercado interno

O primeiro dígito do CST também deve observar o enfoque do declarante.

Exemplo:

```text
Fornecedor importador:
Venda de mercadoria importada adquirida por ele via importação direta
CST com origem 1

Declarante:
Não realizou a importação direta; comprou a mercadoria no mercado interno

Entrada no EFD:
usar origem 2, quando aplicável:
2 = Estrangeira — adquirida no mercado interno
```

---

## 8. Simples Nacional: CSOSN na NF-e e CST na entrada do EFD

Quando o fornecedor é optante pelo Simples Nacional, a NF-e pode vir com CSOSN, por exemplo:

- `101`
- `102`
- `201`
- `202`
- `400`
- `500`
- `900`

Para a escrituração de **entrada** no EFD ICMS/IPI, o declarante deve usar **CST_ICMS**, e não CSOSN, observando o enfoque do declarante.

Exemplos práticos:

| CSOSN na NF-e | Situação | Entrada sugerida no EFD |
|---|---|---|
| `500` | ICMS cobrado anteriormente por ST/substituído | CST `x60`, se a mercadoria entra com ST já cobrada |
| `201`, `202`, `203` | Simples com cobrança de ICMS-ST | CST `x60`, se o imposto foi retido/cobrado anteriormente e o declarante é substituído |
| `102` | sem permissão de crédito no Simples | CST conforme enfoque do declarante; pode ser `x90` se entrada tributada sem crédito |
| `400` | não tributada pelo Simples | CST conforme natureza da operação e legislação aplicável |

---

## 9. Orientações para parametrização em sistema

### 9.1 Nunca usar apenas uma tabela direta CFOP saída → CFOP entrada

A regra deve considerar pelo menos:

```text
CFOP de saída do fornecedor
+ UF do remetente e do destinatário
+ destinação do item no declarante
+ regime tributário do fornecedor
+ regime tributário do declarante
+ existência de ICMS-ST retido/cobrado
+ direito ao crédito
+ origem da mercadoria sob enfoque do declarante
```

### 9.2 Criar parametrização por finalidade do item

Sugestão de campos para regra:

| Campo | Exemplo |
|---|---|
| `tipo_operacao` | entrada |
| `uf_remetente` x `uf_declarante` | mesma UF / outra UF |
| `destinacao_item` | revenda, industrialização, ativo, uso/consumo |
| `mercadoria_st` | sim/não |
| `icms_st_retido` | sim/não |
| `fornecedor_simples` | sim/não |
| `csosn_fornecedor` | 500, 201, 202 etc. |
| `cst_fornecedor` | 010, 060, 070 etc. |
| `direito_credito_icms` | sim/não |
| `origem_mercadoria_declarante` | 0, 1, 2, 3, 4, 5, 6, 7 ou 8 |
| `cfop_entrada` | 1.403, 2.403 etc. |
| `cst_icms_entrada` | 060, 260, 090 etc. |

### 9.3 Ordem recomendada de decisão

```text
1. Identificar se o documento será escriturado como entrada.
2. Definir se a operação é interna, interestadual ou exterior.
3. Definir a destinação do item no estabelecimento declarante.
4. Verificar se a mercadoria está sujeita à ST.
5. Verificar se houve ICMS-ST retido/cobrado anteriormente.
6. Definir CFOP de entrada conforme destinação e ST.
7. Definir origem do CST sob enfoque do declarante.
8. Definir tributação do CST sob enfoque do declarante.
9. Verificar se há direito ao crédito de ICMS.
10. Validar bases, alíquotas e valores conforme CST e direito ao crédito.
```

---

## 10. Exemplos práticos

### Exemplo 1 — compra interna para revenda com ST

```text
NF-e fornecedor:
CFOP 5.403
CST 010

Entrada no declarante:
CFOP 1.403
CST 060
```

Motivo: o fornecedor vende como substituto tributário; o destinatário recebe a mercadoria com ICMS-ST já cobrado e a destina à revenda.

---

### Exemplo 2 — compra interestadual para revenda com ST

```text
NF-e fornecedor:
CFOP 6.403
CST 010

Entrada no declarante:
CFOP 2.403
CST 060
```

Motivo: mesma lógica do exemplo anterior, mas a operação é interestadual.

---

### Exemplo 3 — compra interna para uso/consumo com ST

```text
NF-e fornecedor:
CFOP 5.403
CST 010

Entrada no declarante:
CFOP 1.407
CST 060
```

Motivo: a mercadoria está sujeita à ST, mas a destinação no declarante é uso/consumo, não revenda.

---

### Exemplo 4 — compra interna para ativo imobilizado com ST

```text
NF-e fornecedor:
CFOP 5.403
CST 010

Entrada no declarante:
CFOP 1.406
CST 060
```

Motivo: a mercadoria está sujeita à ST, mas a destinação é ativo imobilizado.

---

### Exemplo 5 — compra tributada para uso/consumo, sem ST e sem crédito

```text
NF-e fornecedor:
CFOP 5.102
CST 000

Entrada no declarante:
CFOP 1.556
CST 090
```

Motivo: a operação é tributada, mas o declarante não tem direito ao crédito por se tratar de uso/consumo.

---

### Exemplo 6 — compra para revenda, sem ST e com crédito

```text
NF-e fornecedor:
CFOP 5.102
CST 000

Entrada no declarante:
CFOP 1.102
CST 000
```

Motivo: compra para comercialização, tributada integralmente, com direito a crédito.

---

### Exemplo 7 — fornecedor Simples Nacional com CSOSN 500

```text
NF-e fornecedor:
CFOP 5.405
CSOSN 500

Entrada no declarante:
CFOP 1.403
CST 060
```

Motivo: CSOSN é utilizado na NF-e do optante pelo Simples, mas na entrada do EFD o declarante deve escriturar CST_ICMS. Se a mercadoria entra para revenda com ICMS-ST já cobrado, usa-se CST final 60.

---

## 11. Alertas importantes

### 11.1 O CFOP do fornecedor não define sozinho o CFOP da entrada

O CFOP do fornecedor ajuda a identificar a natureza da operação, mas o CFOP da entrada depende da destinação no declarante.

Exemplo: a mesma NF-e com `5.403` pode gerar:

| Destinação | CFOP de entrada |
|---|---|
| Revenda | `1.403` |
| Industrialização | `1.401` |
| Ativo imobilizado | `1.406` |
| Uso/consumo | `1.407` |

### 11.2 CST final `60` não significa crédito de ICMS próprio

O CST `x60` indica ICMS cobrado anteriormente por ST ou antecipação com encerramento. Em regra, não representa ICMS próprio destacado para apropriação como crédito normal.

### 11.3 A origem do CST pode mudar

Não copie automaticamente o primeiro dígito do CST do fornecedor.

Exemplo: se o fornecedor é importador direto e o declarante compra no mercado interno, o declarante pode precisar usar origem `2` na entrada, e não origem `1`.

### 11.4 Conferir legislação estadual

Substituição tributária, antecipação, benefício fiscal, crédito presumido, diferimento e ressarcimento/complemento de ST podem ter regras específicas por UF.

### 11.5 Validar com os registros totalizadores

No EFD, as combinações de item devem fechar com os registros analíticos e de apuração. Portanto, a parametrização do C170 deve ser coerente com C190, C100, apuração de ICMS e, quando aplicável, registros de ST.

---

## 12. Pseudorregra para implementação

```pseudo
se documento.ind_oper == "entrada":
    definir_prefixo_cfop:
        se remetente_mesma_uf:
            prefixo = "1"
        se remetente_outra_uf:
            prefixo = "2"
        se entrada_exterior:
            prefixo = "3"

    definir_destinacao_item:
        industrializacao
        comercializacao
        ativo
        uso_consumo
        prestacao_servico
        outros

    se mercadoria_sujeita_st e icms_st_retido_ou_cobrado:
        se destinacao == industrializacao:
            cfop = prefixo + ".401"
        se destinacao == comercializacao:
            cfop = prefixo + ".403"
        se destinacao == ativo:
            cfop = prefixo + ".406"
        se destinacao == uso_consumo:
            cfop = prefixo + ".407"

        cst_final = "60"

    senao:
        se destinacao == industrializacao:
            cfop = prefixo + ".101"
        se destinacao == comercializacao:
            cfop = prefixo + ".102"
        se destinacao == ativo:
            cfop = prefixo + ".551"
        se destinacao == uso_consumo:
            cfop = prefixo + ".556"

        se sem_direito_credito e operacao_tributada:
            cst_final = "90"
        senao:
            cst_final = tributacao_aplicavel_sob_enfoque_declarante

    cst_icms = origem_mercadoria_sob_enfoque_declarante + cst_final
```

> Observação: o pseudocódigo acima é uma base de parametrização e não substitui a análise fiscal. Existem operações especiais que exigem tratamento próprio, como devoluções, remessas, retornos, bonificações, transferências, importações, energia, combustíveis, transportes e serviços de comunicação.

---

## 13. Checklist de conferência

Antes de fechar a escrituração, conferir:

- [ ] O CFOP é de entrada (`1`, `2` ou `3`)?
- [ ] O CFOP reflete a destinação real do item?
- [ ] O CST foi definido sob o enfoque do declarante?
- [ ] O primeiro dígito do CST reflete a origem correta para o declarante?
- [ ] Em operação com ST retida, o CST de entrada está como `x60`?
- [ ] Em uso/consumo sem crédito, a entrada tributada foi tratada como `x90`, quando aplicável?
- [ ] Entradas de fornecedor Simples foram convertidas de CSOSN para CST_ICMS?
- [ ] Bases, alíquotas e valores de ICMS estão coerentes com o direito ao crédito?
- [ ] C170 e C190 estão coerentes?
- [ ] A legislação da UF foi verificada para exceções?

---

## 14. Fontes normativas para conferência

- Guia Prático da EFD ICMS/IPI — versão vigente.
- Convênio s/nº, de 15 de dezembro de 1970 — CFOP e CST.
- Ajustes SINIEF que alteram CFOP, CST e CSOSN.
- Legislação estadual do ICMS aplicável à operação.
- Respostas à Consulta da UF, quando houver dúvida sobre caso concreto.
