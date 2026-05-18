# Validacao e Inconsistencias Comuns na ECD

> **Purpose**: Validar o arquivo ECD, identificar inconsistencias comuns e como corrigi-las
> **MCP Validated**: 2026-05-04

## When to Use

- Antes de transmitir a ECD para detectar erros antecipadamente
- Ao receber rejeicao do PGE e precisar diagnosticar a causa
- Ao implementar validacao automatica no sistema gerador

## Implementation

```text
CHECKLIST DE VALIDACAO PRE-ENVIO

[ESTRUTURAL]
[ ] Arquivo em UTF-8 sem BOM
[ ] Cada linha termina com CRLF (\r\n)
[ ] Toda linha comeca e termina com pipe |
[ ] Sequencia de blocos: 0 > I > J > 9 (K apenas se financeira)
[ ] Registros de abertura e encerramento presentes em cada bloco

[BLOCO 0]
[ ] 0000: todos os campos obrigatorios preenchidos
[ ] 0000: CNPJ com 14 digitos, valido (modulo 11)
[ ] 0000: DT_INI e DT_FIN no formato DDMMAAAA
[ ] 0000: COD_VER_LC = 10 para exercicio 2024+
[ ] 0007: CNPJ dos responsaveis validos
[ ] 0990: qtd de linhas do bloco correto

[BLOCO I — PLANO DE CONTAS]
[ ] I050: toda conta analitica (IND_CTA=A) tem I051 filho
[ ] I050: hierarquia de contas sem gaps (cod_cta_sup existe no I050)
[ ] I050: natureza devedora/credora compativel com grupo da conta
[ ] I051: cod_cta_ref existe no PCRFB publicado pela RFB
[ ] I051: nivel_cta_ref compativel com codigo informado

[BLOCO I — LANCAMENTOS]
[ ] I200/I250: soma dos debitos = soma dos creditos por lancamento
[ ] I250: toda partida aponta para conta analitica do I050
[ ] I100/I150: saldos de abertura batem com saldos de fechamento do periodo anterior
[ ] I350: saldos periodicos calculados corretamente por conta

[BLOCO J]
[ ] J005: cod_inc_trib valido (1=Lucro Real, 2=Lucro Presumido, etc.)
[ ] J100: soma do ativo = soma do passivo + PL no BP
[ ] J100: resultado do periodo no PL bate com resultado da DRE
[ ] J150: transferencias referenciam contas existentes no J100

[BLOCO 9]
[ ] 9900: quantidade de cada registro contada corretamente
[ ] 9999: total de linhas do arquivo correto
```

## Inconsistencias Mais Frequentes e Solucoes

| Inconsistencia | Causa | Solucao |
|---|---|---|
| Conta analitica sem I051 | Faltou mapeamento PCRFB | Criar I051 para cada conta com IND_CTA=A |
| Lancamento nao fecha (D != C) | Erro na exportacao das partidas | Verificar I250 por I200; soma D deve = soma C |
| CNPJ invalido no 0000 | Digito verificador errado | Calcular CNPJ modulo 11 |
| Data no formato errado | Data com barras ou hifens | Converter para DDMMAAAA (8 digitos) |
| Saldo de abertura divergente | Fechamento anterior nao bate | Conferir I150 com balancete de abertura |
| Hash anterior incorreto | COD_HASH_ANT errado | Copiar SHA-1 exato do recibo da ECD anterior |
| J100 ativo != passivo+PL | Erro no balanco | Conferir soma dos grupos no J100 |
| Registro 9900 com qtd errada | Contagem incorreta | Recontar todas as ocorrencias de cada REG |
| Conta nao existe no I050 | Partida referencia conta inexistente | Incluir todas as contas no I050 antes das partidas |
| Nivel de conta inconsistente | Hierarquia quebrada | Verificar que cod_cta_sup de cada conta existe no I050 |

## Configuration

| Ferramenta | Funcao | Disponibilidade |
|---------|---------|-------------|
| PGE (Programa Gerador de Escrituracao) | Validacao oficial RFB | Gratuito — site RFB |
| Validador SPED da RFB (online) | Validacao basica sem instalacao | Portal SPED |
| Scripts proprios | Pre-validacao antes do PGE | Implementacao interna |

## Example Usage

```python
# Validacao basica: verificar se todos os lancamentos fecham
def validar_lancamentos(linhas_arquivo: list[str]) -> list[str]:
    """
    Retorna lista de erros de balanceamento nos lancamentos I200/I250.
    """
    erros = []
    lancamento_atual = None
    soma_debito = 0.0
    soma_credito = 0.0

    for linha in linhas_arquivo:
        campos = linha.strip().split("|")
        if len(campos) < 2:
            continue
        reg = campos[1]

        if reg == "I200":
            # Fechar lancamento anterior
            if lancamento_atual and abs(soma_debito - soma_credito) > 0.005:
                erros.append(
                    f"Lancamento {lancamento_atual}: "
                    f"D={soma_debito:.2f} C={soma_credito:.2f} "
                    f"diferenca={soma_debito - soma_credito:.2f}"
                )
            lancamento_atual = campos[2] if len(campos) > 2 else "?"
            soma_debito = 0.0
            soma_credito = 0.0

        elif reg == "I250" and lancamento_atual:
            valor = float(campos[4].replace(",", ".")) if len(campos) > 4 else 0
            ind_dc = campos[5] if len(campos) > 5 else ""
            if ind_dc == "D":
                soma_debito += valor
            elif ind_dc == "C":
                soma_credito += valor

    return erros

# Validacao: contas analiticas sem I051
def validar_mapeamento_pcrfb(linhas_arquivo: list[str]) -> list[str]:
    contas_analiticas = set()
    contas_com_i051 = set()
    conta_atual = None
    erros = []

    for linha in linhas_arquivo:
        campos = linha.strip().split("|")
        if len(campos) < 2:
            continue
        reg = campos[1]

        if reg == "I050":
            cod_cta = campos[2]
            ind_cta = campos[6] if len(campos) > 6 else ""
            if ind_cta == "A":
                contas_analiticas.add(cod_cta)
            conta_atual = cod_cta

        elif reg == "I051":
            if conta_atual:
                contas_com_i051.add(conta_atual)

    sem_mapeamento = contas_analiticas - contas_com_i051
    for cta in sorted(sem_mapeamento):
        erros.append(f"Conta analitica sem I051: {cta}")

    return erros
```

## See Also

- [Geracao do Arquivo ECD](geracao-arquivo-ecd.md)
- [Transmissao](../concepts/transmissao.md)
- [Bloco I Lancamentos](bloco-i-lancamentos.md)
- [FAQ ECD](faq-perguntas-respostas.md)
