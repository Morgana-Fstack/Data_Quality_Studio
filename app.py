from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from data_cleaner import (
    clean_dataframe,
    column_quality_report,
    inspect_data,
    normalize_column_name,
    profile_data,
    quality_score,
)

st.set_page_config(page_title="Data Quality Studio", page_icon="✨", layout="wide")

st.markdown("""
<style>
  .stApp{background:#f7f8fa}.block-container{padding-top:3.4rem;padding-bottom:3rem}
  [data-testid="stSidebar"]{background:#111827}[data-testid="stSidebar"] *{color:#f9fafb}
  .hero{padding:2rem 2.2rem;border-radius:22px;color:#fff;background:linear-gradient(120deg,#111827 0%,#7f1d1d 65%,#dc2626 100%);margin-bottom:1.2rem}
  .hero h1{margin:0;font-size:2.2rem}.hero p{margin:.55rem 0 0;color:#fee2e2;max-width:780px}
  .eyebrow{color:#fecaca;font-weight:800;letter-spacing:.1em;font-size:.74rem}
  .feature{background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:1.15rem;min-height:142px}
  .feature strong{font-size:1.05rem;color:#111827}.feature p{color:#6b7280;font-size:.88rem}
  [data-testid="stMetric"]{background:#fff;border:1px solid #e5e7eb;padding:1rem;border-radius:16px;box-shadow:0 4px 16px rgba(17,24,39,.04)}
  .problem{background:#fff7ed;border:1px solid #fed7aa;border-left:5px solid #f97316;padding:.8rem 1rem;border-radius:12px;margin:.35rem 0}
  .fixed{background:#f0fdf4;border:1px solid #bbf7d0;border-left:5px solid #22c55e;padding:.8rem 1rem;border-radius:12px;margin:.35rem 0}
  .explain{background:#eff6ff;border:1px solid #bfdbfe;border-radius:14px;padding:1rem;margin:.5rem 0 1rem;color:#1e3a8a}
  .score{font-size:2.7rem;font-weight:850;line-height:1;color:#dc2626}.score.good{color:#16a34a}
  @media(max-width:640px){.block-container{padding-top:4.2rem}.hero{padding:1.5rem}.hero h1{font-size:1.75rem}}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="eyebrow">DATA QUALITY · PYTHON + PANDAS</div>
<h1>Data Quality Studio</h1>
<p>Diagnostique problemas, aplique regras de tratamento e gere uma base confiável com relatório completo do processo.</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Fluxo da análise")
    st.markdown("**1. Diagnosticar**\n\nEntender o que está errado.\n\n**2. Tratar**\n\nEscolher o que será corrigido.\n\n**3. Validar**\n\nComparar a qualidade.\n\n**4. Exportar**\n\nBaixar dados e relatório.")
    st.divider()
    st.caption("Processamento temporário. A base não é armazenada.")

def read_upload(file) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(file, sep=None, engine="python")
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, sep=None, engine="python", encoding="latin-1")
    return pd.read_excel(file)

def trim_for_preview(frame: pd.DataFrame) -> pd.DataFrame:
    preview = frame.copy()
    for column in preview.select_dtypes(include=["object", "string"]).columns:
        preview[column] = preview[column].astype("string").str.strip()
    return preview

def sample_data() -> pd.DataFrame:
    return pd.DataFrame({
        " Nome do Cliente ": ["  Acme Tech  ", "beta store", "Gamma Foods", "beta store", "Delta Lab", "Épsilon", "  "],
        "E-mail ": ["CONTATO@ACME.COM ", "", "email-invalido", "", " contato@delta.com", "equipe@epsilon.com", ""],
        " Status": ["ATIVO ", "em risco", "Ativo", "em risco", " ativo", "CANCELADO", ""],
        "Valor Mensal": ["R$ 1.200,00", "850", "1.500,00", "850", "R$ 990,00", "700", None],
        "Observação vazia": [None] * 7,
    })

st.subheader("O que este projeto faz?")
features = st.columns(3)
features[0].markdown('<div class="feature"><strong>🔎 Diagnostica</strong><p>Mede qualidade, encontra vazios, duplicados, espaços invisíveis, colunas inúteis e e-mails inválidos.</p></div>', unsafe_allow_html=True)
features[1].markdown('<div class="feature"><strong>🧹 Trata</strong><p>Padroniza cabeçalhos e textos, remove duplicidades e permite configurar regras sem alterar o arquivo original.</p></div>', unsafe_allow_html=True)
features[2].markdown('<div class="feature"><strong>📦 Entrega</strong><p>Compara antes e depois e gera Excel com a base limpa, relatório por coluna e histórico das correções.</p></div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Envie um CSV ou Excel para começar", type=["csv", "xlsx", "xls"])
c1, c2 = st.columns([1, 4])
if c1.button("Testar demonstração", type="primary", width="stretch"):
    st.session_state.source_df = sample_data()
    st.session_state.source_name = "carteira_clientes_com_problemas.csv"
if c2.button("Limpar arquivo da sessão", width="content"):
    st.session_state.pop("source_df", None)
    st.session_state.pop("source_name", None)
    st.rerun()

if uploaded is not None:
    upload_key = f"{uploaded.name}:{uploaded.size}"
    if st.session_state.get("upload_key") != upload_key:
        try:
            st.session_state.source_df = read_upload(uploaded)
            st.session_state.source_name = uploaded.name
            st.session_state.upload_key = upload_key
        except Exception as exc:
            st.error(f"Não consegui ler este arquivo: {exc}")

if "source_df" not in st.session_state:
    st.markdown('<div class="explain"><strong>Experimente sem enviar nada:</strong> clique em “Testar demonstração”. Você verá uma carteira propositalmente bagunçada ser diagnosticada e tratada.</div>', unsafe_allow_html=True)
    st.stop()

df = st.session_state.source_df.copy()
source_name = st.session_state.source_name
before = profile_data(df)
issues = inspect_data(df)
score_before = quality_score(df)
st.success(f"Analisando: **{source_name}**")

diagnosis_tab, treatment_tab, result_tab = st.tabs(["1 · Diagnóstico", "2 · Tratamento", "3 · Resultado e download"])

with diagnosis_tab:
    st.markdown('<div class="explain"><strong>Objetivo desta etapa:</strong> mostrar o que impede a base de ser confiável antes de modificar qualquer dado.</div>', unsafe_allow_html=True)
    metrics = st.columns(5)
    metrics[0].metric("Qualidade inicial", f"{score_before}%")
    metrics[1].metric("Registros", before["rows"])
    metrics[2].metric("Campos vazios", before["missing"])
    metrics[3].metric("Duplicados", issues["duplicates_after_trim"])
    metrics[4].metric("E-mails inválidos", issues["invalid_emails"])

    labels = [
        ("headers", "nomes de colunas precisam ser padronizados"),
        ("whitespace", "células contêm espaços extras"),
        ("blank_strings", "textos vazios não são nulos reais"),
        ("duplicates_after_trim", "linhas ficam duplicadas após padronizar os textos"),
        ("empty_rows", "linhas estão completamente vazias"),
        ("empty_columns", "colunas estão completamente vazias"),
        ("invalid_emails", "e-mails possuem formato inválido"),
    ]
    st.subheader("Problemas encontrados")
    found = [(issues[key], label) for key, label in labels if issues[key]]
    if found:
        for count, label in found:
            st.markdown(f'<div class="problem">⚠️ <strong>{count}</strong> {label}</div>', unsafe_allow_html=True)
    else:
        st.success("Nenhum problema automático foi encontrado.")

    st.subheader("Qualidade por coluna")
    st.dataframe(column_quality_report(df), width="stretch", hide_index=True)
    with st.expander("Ver linhas duplicadas"):
        duplicate_view = df[trim_for_preview(df).duplicated(keep=False)]
        if duplicate_view.empty:
            st.info("Nenhuma duplicidade encontrada.")
        else:
            st.dataframe(duplicate_view, width="stretch", hide_index=True)

with treatment_tab:
    st.markdown('<div class="explain"><strong>Você mantém o controle:</strong> somente as regras marcadas abaixo serão aplicadas. O arquivo original permanece intacto.</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    normalize = left.checkbox("Padronizar nomes das colunas", True, help="Nome do Cliente → nome_do_cliente")
    trim = left.checkbox("Remover espaços extras dos textos", True)
    empty = left.checkbox("Transformar textos vazios em nulos", True)
    lower_emails = left.checkbox("Converter e-mails para minúsculas", True)
    dedupe = right.checkbox("Remover linhas duplicadas", True)
    remove_rows = right.checkbox("Remover linhas completamente vazias", True)
    remove_columns = right.checkbox("Remover colunas completamente vazias", True)

    preview_columns = [str(c) for c in df.columns if df[c].dtype == "object"]
    title_original = right.multiselect("Colunas para padronizar como Nome Próprio", preview_columns, help="Ex.: acme tech → Acme Tech")
    normalized_title_columns = tuple(
        normalize_column_name(col) if normalize else col for col in title_original
    )

    cleaned = clean_dataframe(
        df,
        normalize_headers=normalize,
        trim_text=trim,
        empty_to_null=empty,
        remove_duplicates=dedupe,
        remove_empty_rows=remove_rows,
        remove_empty_columns=remove_columns,
        lowercase_emails=lower_emails,
        title_columns=normalized_title_columns,
    )

    st.subheader("Substituição personalizada")
    st.caption("Opcional: escolha uma coluna e troque um valor por outro, como ATIVO → Ativo.")
    replace_col = st.selectbox("Coluna", ["Não aplicar"] + list(cleaned.columns))
    r1, r2 = st.columns(2)
    old_value = r1.text_input("Valor encontrado")
    new_value = r2.text_input("Substituir por")
    replacement_count = 0
    if replace_col != "Não aplicar" and old_value:
        replacement_count = int(cleaned[replace_col].astype("string").eq(old_value).sum())
        cleaned[replace_col] = cleaned[replace_col].replace(old_value, new_value)
        st.info(f"{replacement_count} ocorrência(s) serão substituídas.")

    st.session_state.cleaned_df = cleaned
    st.session_state.clean_settings = {
        "normalize": normalize, "trim": trim, "empty": empty, "lower_emails": lower_emails,
        "dedupe": dedupe, "remove_rows": remove_rows, "remove_columns": remove_columns,
        "title_columns": list(normalized_title_columns), "replacement_count": replacement_count,
    }
    st.dataframe(cleaned.head(20), width="stretch", hide_index=True)

cleaned = st.session_state.get("cleaned_df")
settings = st.session_state.get("clean_settings", {})
if cleaned is None:
    cleaned = clean_dataframe(df)
    settings = {"normalize": True, "trim": True, "empty": True, "lower_emails": True, "dedupe": True, "remove_rows": True, "remove_columns": True, "title_columns": [], "replacement_count": 0}

with result_tab:
    after = profile_data(cleaned)
    score_after = quality_score(cleaned)
    audit = []
    if settings.get("normalize") and issues["headers"]: audit.append(("Cabeçalhos", issues["headers"], "Padronizados"))
    if settings.get("trim") and issues["whitespace"]: audit.append(("Espaços extras", issues["whitespace"], "Removidos"))
    if settings.get("empty") and issues["blank_strings"]: audit.append(("Textos vazios", issues["blank_strings"], "Convertidos em nulos"))
    if settings.get("dedupe") and before["rows"] > after["rows"]: audit.append(("Linhas", before["rows"] - after["rows"], "Removidas"))
    if settings.get("remove_columns") and before["columns"] > after["columns"]: audit.append(("Colunas vazias", before["columns"] - after["columns"], "Removidas"))
    if settings.get("lower_emails"): audit.append(("E-mails", 1, "Padronizados em minúsculas"))
    if settings.get("title_columns"): audit.append(("Colunas de texto", len(settings["title_columns"]), "Convertidas para Nome Próprio"))
    if settings.get("replacement_count"): audit.append(("Valores personalizados", settings["replacement_count"], "Substituídos"))
    audit_df = pd.DataFrame(audit, columns=["Regra", "Quantidade", "Resultado"])

    st.markdown('<div class="explain"><strong>Resultado:</strong> o ganho de qualidade abaixo compara exatamente a base recebida com a versão tratada.</div>', unsafe_allow_html=True)
    a, arrow, b = st.columns([2, 1, 2])
    a.markdown(f'<div class="feature"><strong>ANTES</strong><div class="score">{score_before}%</div><p>Qualidade da base original</p></div>', unsafe_allow_html=True)
    arrow.markdown("<h1 style='text-align:center;padding-top:1.5rem'>→</h1>", unsafe_allow_html=True)
    b.markdown(f'<div class="feature"><strong>DEPOIS</strong><div class="score good">{score_after}%</div><p>Qualidade após o tratamento</p></div>', unsafe_allow_html=True)

    remaining = inspect_data(cleaned)
    pending = after["missing"] + remaining["invalid_emails"]
    if pending:
        st.warning(
            f"Restaram {pending} campo(s) que exigem decisão humana: "
            f"{after['missing']} vazio(s) e {remaining['invalid_emails']} e-mail(s) inválido(s). "
            "O sistema sinaliza essas pendências, mas não inventa informações."
        )
    else:
        st.success("A base não possui pendências automáticas após o tratamento.")

    st.subheader("Histórico do que foi alterado")
    if audit_df.empty:
        st.info("Nenhuma alteração foi aplicada.")
    else:
        st.dataframe(audit_df, width="stretch", hide_index=True)

    original_view, cleaned_view = st.tabs(["🔴 Arquivo recebido", "🟢 Base tratada"])
    with original_view:
        st.dataframe(df.head(50), width="stretch", hide_index=True)
    with cleaned_view:
        st.dataframe(cleaned.head(50), width="stretch", hide_index=True)

    xlsx = BytesIO()
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        cleaned.to_excel(writer, index=False, sheet_name="Dados limpos")
        column_quality_report(cleaned).to_excel(writer, index=False, sheet_name="Qualidade por coluna")
        audit_df.to_excel(writer, index=False, sheet_name="Historico da limpeza")
    csv_data = cleaned.to_csv(index=False).encode("utf-8-sig")
    d1, d2 = st.columns(2)
    d1.download_button("Baixar somente os dados (CSV)", csv_data, "base_tratada.csv", "text/csv", width="stretch")
    d2.download_button("Baixar dados + relatório (Excel)", xlsx.getvalue(), "base_tratada_com_relatorio.xlsx", width="stretch", type="primary")

st.caption("Projeto de portfólio desenvolvido por Morgana Petterle da Cunha.")
