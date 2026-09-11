from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from data_cleaner import clean_dataframe, profile_data


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
    df, source_name = pd.read_csv(Path(__file__).with_name("data.csv"), sep=";"), "data.csv (demonstração)"

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
st.markdown('<div class="step">01 · DIAGNÓSTICO DA BASE</div>', unsafe_allow_html=True)
cols = st.columns(4)
for col, label, value in zip(cols, ["Registros", "Colunas", "Campos vazios", "Duplicados"], before.values()):
    col.metric(label, f"{value:,}".replace(",", "."))

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

st.markdown('<div class="step">03 · COMPARE O RESULTADO</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    st.subheader("Antes")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
with right:
    st.subheader("Depois")
    st.dataframe(cleaned.head(20), use_container_width=True, hide_index=True)

st.markdown('<div class="step">04 · BAIXE A BASE LIMPA</div>', unsafe_allow_html=True)
summary = st.columns(3)
summary[0].metric("Linhas removidas", before["rows"] - after["rows"])
summary[1].metric("Duplicados restantes", after["duplicates"])
summary[2].metric("Campos vazios restantes", after["missing"])

csv_data = cleaned.to_csv(index=False).encode("utf-8-sig")
xlsx = BytesIO()
with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
    cleaned.to_excel(writer, index=False, sheet_name="Dados limpos")

d1, d2 = st.columns(2)
d1.download_button("Baixar CSV limpo", csv_data, "base_limpa.csv", "text/csv", use_container_width=True, type="primary")
d2.download_button("Baixar Excel limpo", xlsx.getvalue(), "base_limpa.xlsx", use_container_width=True)

st.caption("Projeto de portfólio desenvolvido por Morgana Petterle da Cunha.")
