from pathlib import Path
import base64
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ATpp",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = ROOT / "dashboard.html"
SITE_FILE = ROOT / "site.html"
MATRIX_FILE = ROOT / "matriz-pda-problemas-v2.xlsx"
SOLUTIONS_FILE = ROOT / "matriz-soluciones-pmc.xlsx"
LINKS_FILE = ROOT / "objeto_tablas_enlaces.json"
CHALKBOARD_FILE = ROOT / "pizarron_transparente.png"
ATPP_MAIN_LOGO_FILE = ROOT / "ATpp_sticker_main.png"
ATPP_INTENSIVE_LOGO_FILE = ROOT / "ATpp_sticker_intensive.png"
DLS_LOGO_FILE = ROOT / "DLS_LOGO_N2.png"


def cargar_matriz_curricular() -> list[dict]:
    df = pd.read_excel(MATRIX_FILE, header=5)
    if df.shape[1] < 22:
        raise ValueError("La matriz curricular no contiene las 22 columnas esperadas.")
    df = df.iloc[:, :22].copy()
    df.columns = ["fase", "campo", "contenido", "pda", *[f"P{i}" for i in range(1, 18)], "metodologia"]
    df = df.dropna(subset=["fase", "campo", "contenido", "pda"])
    return [
        {
            "fase": str(row["fase"]),
            "campo": str(row["campo"]),
            "contenido": str(row["contenido"]),
            "pda": str(row["pda"]),
            "metodologia": str(row["metodologia"]),
            "matches": {f"P{i}": str(row[f"P{i}"]).strip() for i in range(1, 18)},
        }
        for row in df.to_dict(orient="records")
    ]


def cargar_matriz_soluciones() -> list[dict]:
    df = pd.read_excel(SOLUTIONS_FILE, sheet_name="Matriz de Soluciones")
    if df.shape[1] < 10:
        raise ValueError("La matriz de soluciones no contiene las 10 columnas esperadas.")
    df = df.iloc[:, :10].copy()
    df.columns = [
        "id_problema", "problema_master", "ambito_pmc", "id_solucion", "solucion_propuesta",
        "costo_financiero", "involucramiento_comunidad", "tiempo_estimado",
        "puntaje_viabilidad", "analisis_contextualizado",
    ]
    if len(df) != 85 or df.isna().any().any():
        raise ValueError("La matriz de soluciones debe contener 85 registros completos.")
    counts = df.groupby("id_problema").size()
    if len(counts) != 17 or not counts.eq(5).all():
        raise ValueError("Cada problemática P1-P17 debe contener cinco soluciones.")
    records = df.to_dict(orient="records")
    for record in records:
        record["puntaje_viabilidad"] = int(record["puntaje_viabilidad"])
    return records


def render_dashboard() -> None:
    if not DASHBOARD_FILE.exists():
        st.error("No se encontró dashboard.html")
        st.stop()
    dashboard_html = DASHBOARD_FILE.read_text(encoding="utf-8")
    dashboard_html = dashboard_html.replace(
        "</body>",
        """<script>
(function () {
  function intensiveUrl() {
    try {
      return new URL('?page=intensive', window.top.location.href).href;
    } catch (error) {
      return '?page=intensive';
    }
  }
  function wireIntensiveButton() {
    document.querySelectorAll('button').forEach(function (button) {
      if (button.dataset.atppIntensiveWired === 'true') return;
      if ((button.textContent || '').trim().replace(/\\s+/g, ' ').startsWith('ATpp Intensive')) {
        button.dataset.atppIntensiveWired = 'true';
        var link = document.createElement('a');
        link.href = intensiveUrl();
        link.target = '_top';
        link.rel = 'noopener';
        link.className = button.className;
        link.style.cssText = button.style.cssText;
        link.innerHTML = button.innerHTML;
        link.setAttribute('aria-label', 'Abrir ATpp Intensive');
        button.replaceWith(link);
      }
    });
  }
  wireIntensiveButton();
  new MutationObserver(wireIntensiveButton).observe(document.body, {childList: true, subtree: true});
})();
</script></body>""",
    )
    components.html(dashboard_html, height=1200, scrolling=True)


def render_intensive() -> None:
    required = [SITE_FILE, MATRIX_FILE, SOLUTIONS_FILE, LINKS_FILE, CHALKBOARD_FILE,
                ATPP_MAIN_LOGO_FILE, ATPP_INTENSIVE_LOGO_FILE, DLS_LOGO_FILE]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        st.error("Faltan recursos: " + ", ".join(missing))
        st.stop()

    site_html = SITE_FILE.read_text(encoding="utf-8")
    site_html = site_html.replace(
        "__G2_MATRIX_FROM_EXCEL__", json.dumps(cargar_matriz_curricular(), ensure_ascii=False)
    ).replace(
        "__G3_SOLUTIONS_FROM_EXCEL__", json.dumps(cargar_matriz_soluciones(), ensure_ascii=False)
    ).replace(
        "__ORIENTATION_LINKS_JSON__", LINKS_FILE.read_text(encoding="utf-8")
    ).replace(
        "__CHALKBOARD_DATA_URI__", "data:image/png;base64," + base64.b64encode(CHALKBOARD_FILE.read_bytes()).decode("ascii")
    ).replace(
        "__ATPP_MAIN_LOGO_DATA_URI__", "data:image/png;base64," + base64.b64encode(ATPP_MAIN_LOGO_FILE.read_bytes()).decode("ascii")
    ).replace(
        "__ATPP_INTENSIVE_LOGO_DATA_URI__", "data:image/png;base64," + base64.b64encode(ATPP_INTENSIVE_LOGO_FILE.read_bytes()).decode("ascii")
    ).replace(
        "__DLS_LOGO_DATA_URI__", "data:image/png;base64," + base64.b64encode(DLS_LOGO_FILE.read_bytes()).decode("ascii")
    )
    intensive_override = """
<style>
  .topbar { display: none !important; }
  #atpp { display: none !important; }
  #intensive { display: block !important; }
  .topbar .nav { display: flex !important; }
  .topbar .mobile-toggle, .topbar .demo { display: none !important; }
  .topbar .brand { pointer-events: none; }
  .topbar .nav .home-link {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 10px 17px;
    border-radius: 9px;
    background: var(--blue);
    color: #fff;
    font-weight: 700;
    text-decoration: none;
  }
  .back-atpp { display: inline-flex !important; }
</style>
<script>
(function () {
  document.title = 'ATpp Intensive — Fases y talleres intensivos';
  var nav = document.querySelector('.topbar .nav');
  if (nav) {
    nav.innerHTML = '<a class="home-link" href="' + new URL('?page=dashboard', window.top.location.href).href + '" target="_top" rel="noopener">← Inicio</a>';
    nav.setAttribute('aria-label', 'Navegación de ATpp Intensive');
  }
  var back = document.querySelector('.back-atpp');
  if (back) {
    back.textContent = '← Volver al dashboard';
    back.addEventListener('click', function (event) {
      event.preventDefault();
      window.top.location.href = '?page=dashboard';
    });
  }
})();
</script>
"""
    site_html = site_html.replace("</body>", intensive_override + "</body>")
    st.markdown(
        """
        <style>
          .intensive-streamlit-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            min-height: 58px;
            padding: 8px 18px;
            margin: -1rem 0 0.5rem;
            border-bottom: 1px solid #dfe7ee;
            background: #fff;
            color: #0A2F5E;
            font: 700 15px/1.2 Inter, Arial, sans-serif;
          }
          .intensive-streamlit-nav a {
            display: inline-flex;
            align-items: center;
            padding: 9px 15px;
            border-radius: 9px;
            background: #0A2F5E;
            color: #fff !important;
            text-decoration: none !important;
          }
        </style>
        <nav class="intensive-streamlit-nav" aria-label="Navegación de ATpp Intensive">
          <span><img src="data:image/png;base64,""" + base64.b64encode(ATPP_INTENSIVE_LOGO_FILE.read_bytes()).decode("ascii") + """" alt="ATpp Intensive" style="height:42px;width:auto;object-fit:contain;"></span>
          <a href="?page=dashboard">← Inicio</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )
    components.html(site_html, height=1200, scrolling=True)


page = st.query_params.get("page", "dashboard")
if page == "intensive":
    render_intensive()
else:
    render_dashboard()
