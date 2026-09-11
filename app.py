from __future__ import annotations

from io import BytesIO
import pandas as pd
import streamlit as st

from data_cleaner import clean_dataframe, inspect_data, profile_data


st.set_page_config(page_title="Data Cleaning Studio", page_icon="✨", layout="wide")

st.markdown("""
<style>
  .stApp { background: #f7f8fa; }
  [data-testid="stSidebar"] { background: #111827; }
  [data-testid="stSidebar"] * { color: #f9fafb; }
  .hero { padding: 1.8rem 2rem; border-radius: 22px; color: white;
    background: linear-gradient(120deg,#111827 0%,#7f1d1d 70%,#dc2626 100%); margin-bottom: 1.2rem; }
  .hero h1 { margin:0; font-size:2.15rem; }
  .hero p { margin:.5rem 0 0; color:#fee2e2; }
  div[data-testid="stMetric"] { background:white; border:1px solid #e5e7eb; padding:1rem;
    border-radius:16px; box-shadow:0 4px 16px rgba(17,24,39,.05); }
  .step { color:#991b1b; font-weight:700; letter-spacing:.04em; font-size:.78rem; }
  .problem { background:#fff7ed; border:1px solid #fed7aa; border-left:5px solid #f97316;
    padding:.8rem 1rem; border-radius:12px; margin:.35rem 0; }
  .fixed { background:#f0fdf4; border:1px solid #bbf7d0; border-left:5px solid #22c55e;
    padding:.8rem 1rem; border-radius:12px; margin:.35rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="step">DATA QUALITY · PYTHON + PANDAS</div>
<h1>Data Cleaning Studio</h1><p>Envie uma base, identifique problemas e baixe uma versão pronta para análise.</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Como funciona")
    st.markdown("**1.** Envie CSV ou Excel\n\n**2.** Veja o diagnóstico\n\n**3.** Escolha as correções\n\n**4.** Baixe a base limpa")
    st.divider()
    st.caption("Seus dados são processados somente durante esta sessão.")

uploaded = st.file_uploader("Arraste sua planilha aqui", type=["csv", "xlsx", "xls"])
use_sample = st.button("Usar base de demonstração", type="secondary")

def read_upload(file) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(file, sep=None, engine="python")
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, sep=None, engine="python", encoding="latin-1")
    return pd.read_excel(file)

df = None
source_name = ""
if uploaded:
    try:
        df, source_name = read_upload(uploaded), uploaded.name
    except Exception as exc:
        st.error(f"Não consegui ler o arquivo: {exc}")
elif use_sample:
    df = pd.DataFrame({
        " Nome do Cliente ": ["  Acme Tech  ", "Beta Store", "Gamma Foods", "Beta Store", "Delta Lab", "  "],
        "E-mail ": ["CONTATO@ACME.COM ", "", "gamma@email.com", "", " contato@delta.com", ""],
        " Status": ["Ativo ", "Em risco", "Ativo", "Em risco", "Ativo", ""],
        "Valor Mensal": [1200, 850, 1500, 850, 990, None],
    })
    source_name = "carteira_clientes_suja.csv (demonstração)"

if df is None:
    st.info("Comece enviando um arquivo ou abra a demonstração. Nenhuma limpeza acontece sem sua confirmação.")
    st.subheader("O que o Studio verifica")
    c1, c2, c3 = st.columns(3)
    c1.markdown("#### Dados ausentes\nLocaliza células vazias e textos em branco.")
    c2.markdown("#### Duplicidades\nEncontra linhas repetidas que distorcem análises.")
    c3.markdown("#### Padronização\nOrganiza cabeçalhos e remove espaços invisíveis.")
    st.stop()

st.success(f"Arquivo carregado: **{source_name}**")
before = profile_data(df)
issues = inspect_data(df)
st.markdown('<div class="step">01 · DIAGNÓSTICO DA BASE</div>', unsafe_allow_html=True)
cols = st.columns(4)
for col, label, value in zip(cols, ["Registros", "Colunas", "Campos vazios", "Duplicados"], before.values()):
    col.metric(label, f"{value:,}".replace(",", "."))

st.subheader("Problemas encontrados")
problem_labels = [
    ("headers", "nomes de colunas fora do padrão"),
    ("whitespace", "células com espaços extras"),
    ("blank_strings", "textos vazios escondidos"),
    ("duplicates_after_trim", "linhas duplicadas após a padronização"),
]
found = [(issues[key], label) for key, label in problem_labels if issues[key]]
if found:
    for count, label in found:
        st.markdown(f'<div class="problem">⚠️ <strong>{count}</strong> {label}</div>', unsafe_allow_html=True)
else:
    st.success("Nenhum dos problemas automáticos foi encontrado nesta base.")

with st.expander("Ver qualidade por coluna", expanded=True):
    quality = pd.DataFrame({
        "Coluna": df.columns.astype(str),
        "Tipo atual": df.dtypes.astype(str).values,
        "Vazios": df.isna().sum().values,
        "Valores únicos": df.nunique(dropna=True).values,
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

st.markdown('<div class="step">02 · ESCOLHA AS CORREÇÕES</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
normalize = c1.checkbox("Padronizar nomes das colunas", True, help="Ex.: Nome Empresa → nome_empresa")
trim = c1.checkbox("Remover espaços extras dos textos", True)
empty = c2.checkbox("Converter textos vazios em campos nulos", True)
dedupe = c2.checkbox("Remover linhas exatamente duplicadas", True)

cleaned = clean_dataframe(df, normalize_headers=normalize, trim_text=trim, empty_to_null=empty, remove_duplicates=dedupe)
after = profile_data(cleaned)

st.markdown('<div class="step">03 · ENTENDA O QUE MUDOU</div>', unsafe_allow_html=True)
applied = []
if normalize and issues["headers"]:
    applied.append(f'{issues["headers"]} nomes de colunas foram padronizados')
if trim and issues["whitespace"]:
    applied.append(f'{issues["whitespace"]} células perderam espaços extras')
if empty and issues["blank_strings"]:
    applied.append(f'{issues["blank_strings"]} textos vazios viraram campos nulos reais')
removed = before["rows"] - after["rows"]
if dedupe and removed:
    applied.append(f'{removed} linhas duplicadas foram removidas')

if applied:
    for item in applied:
        st.markdown(f'<div class="fixed">✓ {item}</div>', unsafe_allow_html=True)
else:
    st.info("As opções selecionadas não produziram alterações nesta base.")

original_tab, clean_tab = st.tabs(["🔴 Base original (suja)", "🟢 Resultado limpo"])
with original_tab:
    st.caption("Este é o arquivo exatamente como foi recebido.")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
with clean_tab:
    st.caption("Este é o arquivo após aplicar somente as opções marcadas acima.")
    st.dataframe(cleaned.head(50), use_container_width=True, hide_index=True)

st.markdown('<div class="step">04 · BAIXE A BASE LIMPA</div>', unsafe_allow_html=True)
summary = st.columns(3)
summary[0].metric("Correções realizadas", len(applied))
summary[1].metric("Duplicados restantes", after["duplicates"])
summary[2].metric("Campos vazios restantes", after["missing"])

csv_data = cleaned.to_csv(index=False).encode("utf-8-sig")
xlsx = BytesIO()
with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
    cleaned.to_excel(writer, index=False, sheet_name="Dados limpos")

d1, d2 = st.columns(2)
d1.download_button("Baixar resultado em CSV", csv_data, "base_limpa.csv", "text/csv", use_container_width=True, type="primary")
d2.download_button("Baixar resultado em Excel", xlsx.getvalue(), "base_limpa.xlsx", use_container_width=True)

st.caption("Projeto de portfólio desenvolvido por Morgana Petterle da Cunha.")
