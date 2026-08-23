from pathlib import Path

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

components.html(
    SITE_FILE.read_text(encoding="utf-8"),
    height=1600,
    scrolling=True,
)
