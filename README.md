# Data Cleaning Studio

> **Transforme planilhas desorganizadas em bases prontas para análise — direto pelo navegador.**

Projeto visual de qualidade de dados desenvolvido por **Morgana Petterle da Cunha** com Python, pandas e Streamlit.

## O problema que resolve

Bases operacionais frequentemente contêm espaços invisíveis, campos vazios, cabeçalhos inconsistentes e registros duplicados. O Data Cleaning Studio identifica esses problemas, permite escolher as correções e compara o resultado antes do download.

## Experiência da aplicação

1. Envie um arquivo CSV ou Excel — ou use a base demonstrativa.
2. Consulte o diagnóstico de registros, colunas, vazios e duplicados.
3. Escolha as regras de limpeza.
4. Compare a tabela original com a tabela tratada.
5. Baixe o resultado em CSV ou Excel.

## Funcionalidades

- upload de `.csv`, `.xlsx` e `.xls`;
- detecção automática do separador de arquivos CSV;
- diagnóstico geral e por coluna;
- padronização de nomes de colunas;
- remoção de espaços extras;
- conversão de textos vazios em valores nulos;
- remoção controlada de linhas duplicadas;
- comparação visual antes × depois;
- exportação em CSV e Excel;
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
