# Obrigatoriedade da ECD

> **Purpose**: Quem deve entregar a ECD, dispensa, exceções e prazos de entrega
> **Confidence**: 0.97
> **MCP Validated**: 2026-05-04

## Overview

A obrigatoriedade da ECD é definida pela IN RFB nº 1.863/2018 e suas atualizações. Em regra, toda pessoa jurídica sujeita à tributação pelo Lucro Real é obrigada. O Lucro Presumido é obrigado quando distribuir lucros sem incidência do IR acima do limite presumido, ou quando optar pela escrituração contábil completa. Entidades imunes e isentas com receita acima de R$ 4,8 milhões também são obrigadas.

## Quem é Obrigado (Art. 3º IN 1.863/2018)

| Tipo de Pessoa Jurídica | Obrigado? | Condição |
|---|---|---|
| Lucro Real | Sim | Sempre |
| Lucro Presumido (distribuição > limite) | Sim | Quando distribui lucros isento acima do presumido |
| Lucro Presumido (escrituração contábil) | Sim | Quando opta por manter contabilidade completa |
| Lucro Arbitrado | Sim | Sempre |
| Entidade Imune/Isenta (receita >= R$4,8 mi) | Sim | Receita bruta >= R$ 4.800.000,00 no ano |
| SCP (Sócio Ostensivo) | Sim | Incluir contas da SCP na ECD do sócio ostensivo |
| Optante pelo Simples Nacional | Nao | Dispensada |
| MEI | Nao | Dispensada |
| Pessoa Jurídica inativa | Nao | Dispensada (usa DCTF inatividade) |

## Quem Está Dispensado

```text
Dispensados da ECD (Art. 4º IN 1.863/2018):
1. Optantes pelo Simples Nacional
2. MEI (Microempreendedor Individual)
3. PJ que ficou inativa durante todo o ano-calendário
4. PJ imune/isenta com receita bruta < R$ 4.800.000,00
5. PJ tributada pelo Lucro Presumido que não distribuiu
   lucros acima do limite e não manteve escrituração completa
6. Órgãos públicos, autarquias e fundações públicas
```

## Prazos de Entrega

| Ano-Calendário | Prazo de Entrega | Situação |
|---|---|---|
| 2020 | Último dia útil de junho/2021 | Entregue |
| 2021 | Último dia útil de junho/2022 | Entregue |
| 2022 | Último dia útil de junho/2023 | Entregue |
| 2023 | Último dia útil de junho/2024 | Entregue |
| 2024 | Último dia útil de junho/2025 | Entregue |
| 2025 | Último dia útil de junho/2026 | Vigente |

**Nota:** O prazo histórico é sempre o último dia útil de junho do ano seguinte ao ano-calendário da escrituração. Eventos especiais (fusão, cisão, incorporação, extinção) têm prazo específico de 90 dias do evento ou até o prazo normal, o que ocorrer primeiro.

## Casos Especiais de Prazo

| Evento | Prazo |
|---|---|
| Extinção da PJ | Último dia útil do mês seguinte ao evento |
| Fusão / Incorporação / Cisão | Último dia útil do mês seguinte ao evento |
| Saída do Simples Nacional | Prazo normal (junho do ano seguinte) |

## Multas por Atraso

```text
Base: Art. 57 da MP 2.158-35/2001

- Entrega com atraso: R$ 500,00 por mês ou fração
- Para empresas com receita bruta anual <= R$ 3.600.000: R$ 250,00/mês
- Não entrega ou entrega com informações incorretas:
  0,5% do valor das transações (mínimo R$ 500,00)
- Redução de 50% se entregue antes de notificação da RFB
```

## Common Mistakes

### Wrong

```text
Empresa do Lucro Presumido acha que está automaticamente dispensada
da ECD e não entrega, mesmo tendo distribuído lucros isentos acima
do valor apurado pela presunção legal.
```

### Correct

```text
Verificar se houve distribuição de lucros isentos. Se o lucro contábil
apurado foi superior ao lucro presumido, a distribuição do excedente
isento EXIGE escrituração contábil completa, logo, a ECD é obrigatória.
Regra: distribui isento acima do presumido = obrigado à ECD.
```

## Related

- [O Que e ECD](o-que-e-ecd.md)
- [Transmissao](../patterns/transmissao.md)
- [Substituicao e Retificacao](../patterns/substituicao-retificacao.md)
