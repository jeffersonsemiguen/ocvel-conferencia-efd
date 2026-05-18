# FAQ — Perguntas e Respostas sobre ECD

> **Purpose**: Respostas completas para as duvidas mais frequentes sobre a ECD
> **MCP Validated**: 2026-05-04

## When to Use

- Como referencia rapida para duvidas de contadores e desenvolvedores
- Para resolver duvidas operacionais sem precisar consultar a legislacao
- Como base para treinamento de equipes em sistemas ECD

## Implementation

```text
INDICE DAS PERGUNTAS

01. O que e a ECD e qual a diferenca para a ECF?
02. Quem e obrigado a entregar a ECD?
03. Qual o prazo de entrega da ECD?
04. A empresa do Simples Nacional precisa entregar a ECD?
05. O que acontece se a ECD nao for entregue no prazo?
06. Qual programa uso para transmitir a ECD?
07. Posso corrigir uma ECD ja entregue?
08. Qual o encoding correto do arquivo ECD?
09. Como mapear as contas para o Plano de Contas Referencial?
10. O que e o hash SHA-1 e para que serve na ECD?
11. Quem deve assinar digitalmente a ECD?
12. O que e o Bloco K e para quem e obrigatorio?
13. Como incluir a DRE na ECD?
14. O que sao as SCP (Sociedades em Conta de Participacao) na ECD?
15. Como tratar empresa inativa na ECD?
16. O que e o registro I051 e por que e importante?
17. Como funciona a validacao no PGE?
18. O CNPJ da empresa mudou durante o ano — como fazer a ECD?
19. Posso ter mais de um livro Diario na mesma ECD?
20. O que fazer quando o PGE apresenta erro de "conta sem mapeamento"?
21. A holding precisa entregar ECD?
22. Qual a diferenca entre ECD simplificada (tipo S) e geral (tipo G)?
```

## Perguntas e Respostas

**Q01: O que e a ECD e qual a diferenca para a ECF?**

A ECD (Escrituração Contabil Digital) e a versao digital dos livros contabeis (Diario, Razao, Balancos). A ECF (Escrituracao Contabil Fiscal) e a declaracao de IRPJ e CSLL. Sao obrigacoes separadas: a ECD e entregue ate o ultimo dia util de junho, a ECF ate o ultimo dia util de julho. A ECF utiliza saldos da ECD como base para a apuracao do IRPJ.

**Q02: Quem e obrigado a entregar a ECD?**

Sao obrigadas: (a) todas as empresas tributadas pelo Lucro Real; (b) empresas do Lucro Presumido que distribuiram lucros isentos acima do limite presumido; (c) empresas do Lucro Presumido que optaram por manter escrituracao contabil completa; (d) entidades imunes e isentas com receita bruta >= R$ 4,8 milhoes; (e) sociedades em conta de participacao (via socio ostensivo). Sao dispensadas: Simples Nacional, MEI, empresas inativas, orgaos publicos.

**Q03: Qual o prazo de entrega da ECD?**

O prazo e o ultimo dia util de junho do ano seguinte ao ano-calendario escriturado. Exemplo: ECD do exercicio 2024 deve ser entregue ate o ultimo dia util de junho de 2025. Em casos de fusao, cisao, incorporacao ou extincao, o prazo e o ultimo dia util do mes subsequente ao evento.

**Q04: A empresa do Simples Nacional precisa entregar a ECD?**

Nao. As empresas optantes pelo Simples Nacional estao dispensadas da ECD (Art. 4o, I, da IN RFB 1.863/2018). Tambem estao dispensados o MEI e as empresas totalmente inativas durante o ano-calendario.

**Q05: O que acontece se a ECD nao for entregue no prazo?**

A multa e de R$ 500,00 por mes ou fracao de mes de atraso (R$ 250,00 para empresas com receita bruta <= R$ 3,6 milhoes). Alem disso, a nao entrega pode impedir a entrega da ECF (que usa dados da ECD) e gerar autuacoes por omissao de informacoes. A multa e reduzida em 50% se a entrega ocorrer antes de qualquer notificacao da RFB.

**Q06: Qual programa uso para transmitir a ECD?**

O PGE (Programa Gerador de Escrituracao), disponibilizado gratuitamente pela RFB no portal SPED (https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/declaracoes-e-demonstrativos/sped). O PGE valida o arquivo, recebe as assinaturas digitais e transmite ao servidor da RFB. Cada versao do PGE suporta uma versao do leiaute ECD.

**Q07: Posso corrigir uma ECD ja entregue?**

Sim. A retificacao e permitida a qualquer momento. Para isso: (1) corrija o arquivo ECD no sistema contabil; (2) preencha o campo COD_HASH_ANT no registro 0000 com o hash SHA-1 da ECD que sera substituida (obtido no recibo da transmissao anterior ou no e-CAC); (3) transmita normalmente pelo PGE. A retificacao substitui integralmente a ECD anterior.

**Q08: Qual o encoding correto do arquivo ECD?**

UTF-8 sem BOM (Byte Order Mark). Arquivos com BOM ou em outros encodings (Latin-1, Windows-1252) sao rejeitados pelo PGE com erro de leitura. No Windows, ao gerar o arquivo em Python, usar `open(caminho, "w", encoding="utf-8")` sem o parametro `encoding="utf-8-sig"`.

**Q09: Como mapear as contas para o Plano de Contas Referencial?**

Cada conta ANALITICA do plano proprio (registro I050 com IND_CTA=A) deve ter um registro filho I051 com o codigo correspondente no PCRFB (Plano de Contas Referencial RFB). O PCRFB e publicado no portal da RFB. Contas sinteticas nao recebem I051. O mapeamento nao precisa ser 1:1 — varias contas proprias podem mapear para o mesmo codigo referencial.

**Q10: O que e o hash SHA-1 e para que serve na ECD?**

O hash SHA-1 e uma "impressao digital" do arquivo ECD calculada algoritmicamente. Ele e gerado automaticamente pelo PGE na transmissao e consta no recibo (.rec). O hash e usado no campo COD_HASH_ANT do registro 0000 quando ha retificacao, comprovando qual versao do arquivo esta sendo substituida. Tambem e informado na ECF para vincular as duas escrituracoes.

**Q11: Quem deve assinar digitalmente a ECD?**

Obrigatoriamente dois signatarios: (1) o CONTABILISTA RESPONSAVEL, com e-CPF que contenha o numero do CRC; e (2) o REPRESENTANTE LEGAL da pessoa juridica, com e-CPF do administrador/socio ou e-CNPJ da empresa. O PGE nao permite transmissao sem as duas assinaturas.

**Q12: O que e o Bloco K e para quem e obrigatorio?**

O Bloco K contem as informacoes do COSIF (Plano Contabil das Instituicoes do Sistema Financeiro Nacional). E obrigatorio apenas para instituicoes financeiras reguladas pelo BACEN (bancos, financeiras, cooperativas de credito, corretoras, distribuidoras) e para seguradoras reguladas pela SUSEP. Empresas nao financeiras devem incluir o Bloco K com IND_MOV=1 (sem dados).

**Q13: Como incluir a DRE na ECD?**

A DRE e incluida no Bloco J, registro J100, com o campo IND_VL=07. Cada linha da DRE usa um codigo do PCRFB no campo COD_CTA_REF. Os valores das contas de receita sao informados com IND_DC=C, e as despesas com IND_DC=D. O resultado liquido deve coincidir com a variacao do PL no Balanco Patrimonial.

**Q14: O que sao as SCP na ECD?**

SCP (Sociedade em Conta de Participacao) e uma sociedade sem personalidade juridica composta por socio ostensivo (que opera externamente) e socios participantes (ocultos). O socio ostensivo inclui as contas da SCP na sua propria ECD, identificadas no registro 0035 (com CNPJ da SCP) e nos lancamentos do Bloco I com o campo COD_SCP preenchido.

**Q15: Como tratar empresa inativa na ECD?**

Empresa que ficou TOTALMENTE inativa durante todo o ano-calendario esta DISPENSADA da ECD (Art. 4o, IV, IN 1.863/2018). Inativa = sem qualquer atividade operacional, comercial ou financeira. Se houve qualquer transacao (mesmo apenas pagamento de taxa), a empresa e ativa e deve entregar a ECD se obrigada. Para DCTF/DEFIS da empresa inativa, existem declaracoes especificas.

**Q16: O que e o registro I051 e por que e importante?**

O I051 e o registro de mapeamento entre o plano de contas proprio da empresa e o Plano de Contas Referencial RFB (PCRFB). Ele e filho do I050 e deve existir para TODA conta analitica. Sem o I051, o PGE aponta erro "conta analitica sem mapeamento referencial" e impede a transmissao. O I051 permite a RFB padronizar e cruzar dados contabeis de diferentes empresas.

**Q17: Como funciona a validacao no PGE?**

Ao importar o arquivo .sped, o PGE executa automaticamente dois tipos de validacao: (1) ESTRUTURAL — verifica formato dos campos, encoding, separadores, sequencia de blocos e registros; (2) DE CONTEUDO — verifica logica contabil: balanceamento dos lancamentos, existencia das contas mapeadas, totalizacoes do Bloco 9, compatibilidade de saldos. Erros aparecem em lista no PGE com numero e descricao. Advertencias (W) nao impedem transmissao; Erros (E) impedem.

**Q18: O CNPJ da empresa mudou durante o ano — como fazer a ECD?**

CNPJ e imutavel para fins de SPED. Se houve mudanca juridica (fusao, cisao, incorporacao), cada CNPJ entrega sua propria ECD pelo periodo em que existiu, com o campo INDIC_SIT_ESP preenchido adequadamente (1=abertura, 2=cisao parcial, 3=cisao total, 4=fusao, 5=incorporacao). O prazo para eventos especiais e o ultimo dia util do mes seguinte ao evento.

**Q19: Posso ter mais de um livro Diario na mesma ECD?**

Sim. Uma empresa pode ter varios livros auxiliares alem do Diario Geral. Cada livro gera um registro I010 no Bloco I. O livro principal tem NAT_LVR=G (Diario Geral); auxiliares tem NAT_LVR=R (Razao auxiliar) ou S (Diario com fichas soltas). Todos os livros sao transmitidos no mesmo arquivo ECD.

**Q20: O que fazer quando o PGE apresenta erro "conta sem mapeamento"?**

Este erro (tipicamente E0201) indica que existe uma conta analitica no I050 (IND_CTA=A) sem o registro I051 correspondente. Solucao: (1) identificar qual conta esta sem mapeamento na lista de erros do PGE; (2) no sistema contabil, criar o I051 para essa conta com o codigo PCRFB correto; (3) re-exportar e reimportar no PGE. O PCRFB completo esta disponivel no Manual ECD da RFB.

**Q21: A holding precisa entregar ECD?**

Depende do regime tributario. Se a holding e tributada pelo Lucro Real, a ECD e obrigatoria. Se e tributada pelo Lucro Presumido, segue a regra geral: obrigada se distribuiu lucros isentos acima do limite presumido. Holdings puras (sem receita operacional) tributadas pelo Lucro Presumido geralmente estao dispensadas, mas devem avaliar caso a caso com base nas receitas de equivalencia patrimonial e dividendos recebidos.

**Q22: Qual a diferenca entre ECD tipo G (Geral) e tipo S (Simplificada)?**

TIPO_ESC_CONT no registro 0000: G = escrituracao completa com todos os livros (Diario, Razao, BP, DRE e demais demonstracoes). S = escrituracao simplificada, disponivel para entidades imunes e isentas de menor porte, contendo apenas Balanco Patrimonial e Demonstracao do Resultado do Periodo, sem lancamento detalhado no Bloco I. Empresas tributadas pelo Lucro Real e Presumido devem usar sempre o tipo G.

## Configuration

| Tipo de Duvida | Fonte Primaria | Fonte Secundaria |
|---------|---------|-------------|
| Legislacao | IN RFB 1.863/2018 | Portal RFB SPED |
| Leiaute tecnico | Manual ECD (MOL) | PGE - ajuda |
| Transmissao | PGE documentacao | e-CAC RFB |
| Certificado digital | ICP-Brasil INCA | AC autorizada |

## See Also

- [O Que e ECD](../concepts/o-que-e-ecd.md)
- [Obrigatoriedade](../concepts/obrigatoriedade.md)
- [Transmissao](../concepts/transmissao.md)
- [Substituicao e Retificacao](substituicao-retificacao.md)
- [Validacao e Inconsistencias](validacao-inconsistencias.md)
