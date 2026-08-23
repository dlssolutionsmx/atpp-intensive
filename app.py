from pathlib import Path
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="ATpp Intensive",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parent
SITE_FILE = ROOT / "site.html"
MATRIX_FILE = ROOT / "matriz-pda-problemas-v2.xlsx"


@st.cache_data
def cargar_matriz_curricular() -> list[dict]:
    """Carga la matriz oficial y normaliza sus columnas para la interfaz G2."""
    df = pd.read_excel(MATRIX_FILE, header=5)
    if df.shape[1] < 22:
        raise ValueError("La matriz curricular no contiene las 22 columnas esperadas.")

    df = df.iloc[:, :22].copy()
    df.columns = [
        "fase",
        "campo",
        "contenido",
        "pda",
        *[f"P{i}" for i in range(1, 18)],
        "metodologia",
    ]
    df = df.dropna(subset=["fase", "campo", "contenido", "pda"])

    records = []
    for row in df.to_dict(orient="records"):
        records.append(
            {
                "fase": str(row["fase"]),
                "campo": str(row["campo"]),
                "contenido": str(row["contenido"]),
                "pda": str(row["pda"]),
                "metodologia": str(row["metodologia"]),
                "matches": {
                    f"P{i}": str(row[f"P{i}"]).strip()
                    for i in range(1, 18)
                },
            }
        )
    return records

st.markdown(
    """
    <style>
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stAppViewContainer"] > .main {padding-top: 0;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    iframe {border: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if not SITE_FILE.exists():
    st.error("No se encontró el recurso del micrositio: site.html")
    st.stop()

if not MATRIX_FILE.exists():
    st.error("No se encontró la matriz curricular: matriz-pda-problemas-v2.xlsx")
    st.stop()

try:
    site_html = SITE_FILE.read_text(encoding="utf-8").replace(
        "__G2_MATRIX_FROM_EXCEL__",
        json.dumps(cargar_matriz_curricular(), ensure_ascii=False),
    )
except Exception as exc:
    st.error(f"No fue posible cargar la matriz curricular: {exc}")
    st.stop()

components.html(
    site_html,
    height=900,
    scrolling=True,
)
