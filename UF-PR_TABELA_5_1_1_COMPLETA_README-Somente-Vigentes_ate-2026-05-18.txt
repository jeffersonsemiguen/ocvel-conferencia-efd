RELATORIO DE CONFORMIDADE - FILTRO DE VIGENCIA
==============================================

ARQUIVO DE ORIGEM
-----------------
Nome: TABELA_5_1_1_COMPLETA.pdf
Tipo: PDF textual
Paginas: 19

ARQUIVOS GERADOS
----------------
1) Markdown filtrado com registros vigentes (.md)
2) Relatorio desta filtragem (.txt)

REFERENCIA DE VIGENCIA
----------------------
Data de referencia: 18/05/2026
Regra aplicada: manter somente linhas com DT INICIO <= 18/05/2026
e DT FINAL vazio/ausente ou DT FINAL >= 18/05/2026.

RESULTADO DO FILTRO
-------------------
- Registros originais: 474
- Registros mantidos (vigentes): 230
- Registros removidos (fora de validade): 244
- Removidos por DT FINAL anterior a data de referencia: 244
- Removidos por DT INICIO posterior a data de referencia: 0
- Codigos distintos vigentes: 230
- Secoes/categorias com pelo menos um registro vigente: 26

OBSERVACOES
-----------
1. Esta filtragem usa apenas as colunas DT INICIO e DT FINAL presentes no material extraido.
2. Linha sem DT FINAL foi tratada como vigente ate nova substituicao.
3. Nao houve remocao por tachado nesta etapa; o filtro aplicado aqui e apenas temporal.
4. O texto de descricao e de ajuste foi preservado exatamente como no Markdown normalizado anterior.

LIMITACOES
----------
1. O filtro nao substitui validacao juridica de vigencia normativa.
2. Se houver sobreposicoes, revogacoes textuais ou excecoes nao refletidas nas datas, elas permanecem fora do escopo desta etapa.
3. Para usar outra data de corte, e necessario rodar nova filtragem.

STATUS
------
Concluido com sucesso.