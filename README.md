# Data Quality Studio

> **Diagnostique, trate e valide planilhas antes de usá-las em análises ou sistemas.**

Projeto visual de qualidade de dados desenvolvido por **Morgana Petterle da Cunha** com Python, pandas e Streamlit. A aplicação não é apenas um conversor de arquivos: ela mede a confiabilidade da base, explica os problemas, aplica regras controladas e documenta o resultado.

## Aplicação online

### [Abrir o Data Quality Studio](https://data-cleaning-python.streamlit.app/)

Teste diretamente pelo navegador usando a base demonstrativa ou envie um arquivo CSV/Excel.

## O problema que resolve

Bases operacionais frequentemente contêm espaços invisíveis, campos vazios, cabeçalhos inconsistentes e registros duplicados. O Data Cleaning Studio identifica esses problemas, permite escolher as correções e compara o resultado antes do download.

## Experiência da aplicação

1. Envie um arquivo CSV ou Excel — ou use a carteira demonstrativa.
2. Consulte a nota de qualidade e os problemas por coluna.
3. Escolha as regras de tratamento.
4. Compare a nota e os dados antes × depois.
5. Baixe somente os dados ou um Excel com relatório e histórico.

## Funcionalidades

- upload de `.csv`, `.xlsx` e `.xls`;
- detecção automática do separador de arquivos CSV;
- diagnóstico geral e por coluna;
- nota de qualidade antes e depois;
- validação de formato de e-mails;
- detecção de linhas e colunas completamente vazias;
- padronização de nomes de colunas;
- remoção de espaços extras;
- padronização de e-mails e nomes próprios;
- conversão de textos vazios em valores nulos;
- remoção controlada de linhas duplicadas;
- substituição personalizada de valores;
- comparação visual antes × depois;
- exportação em CSV;
- Excel com dados limpos, qualidade por coluna e histórico do tratamento;
- processamento temporário, sem banco de dados.

## Tecnologias

- Python
- pandas
- Streamlit
- openpyxl
- unittest

## Executar localmente

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testes

```bash
python -m unittest discover -s tests -v
```

O projeto possui testes para a limpeza visual e para o exercício acadêmico que deu origem ao repositório.

## Origem do projeto

O repositório nasceu como uma atividade da disciplina **DGT2823 — Tecnologias para Desenvolvimento de Soluções de Big Data**. Os arquivos `microatividades.py` e `pratica_pandas.py` foram preservados como histórico da evolução: de scripts executados no terminal para uma ferramenta visual e reutilizável.

## Autoria e licença

Copyright © 2026 **Morgana Petterle da Cunha**. Uso disponível somente para portfólio, demonstração e avaliação profissional. Consulte a [licença](LICENSE).

[LinkedIn](https://linkedin.com/in/morgana-petterle) · [GitHub](https://github.com/Morgana-Fstack)
