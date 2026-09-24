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
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = ROOT / "index.html"
SITE_FILE = ROOT / "intensive.html"
MATRIX_FILE = ROOT / "matriz-pda-problemas-v2.xlsx"
SOLUTIONS_FILE = ROOT / "matriz-soluciones-pmc.xlsx"
LINKS_FILE = ROOT / "objeto_tablas_enlaces.json"
CHALKBOARD_FILE = ROOT / "pizarron_transparente.png"
ATPP_MAIN_LOGO_FILE = ROOT / "ATpp_sticker_main.png"
ATPP_INTENSIVE_LOGO_FILE = ROOT / "ATpp_sticker_intensive.png"
DLS_LOGO_FILE = ROOT / "DLS_LOGO_N2.png"


def navegar(page: str, section: str | None = None) -> None:
    st.query_params.clear()
    st.query_params["page"] = page
    if section:
        st.query_params["section"] = section


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


def render_dashboard_sidebar(section: str) -> None:
    st.sidebar.markdown("## ATpp")
    st.sidebar.caption("MENÚ PRINCIPAL")
    st.sidebar.button("▦  Dashboard", key="nav-dashboard", use_container_width=True,
                      on_click=navegar, args=("dashboard", "dashboard"))
    st.sidebar.caption("PLANEACIÓN")
    links = [
        ("1. Diagnóstico", "diagnostico"),
        ("2. Contenidos", "contenidos"),
        ("3. Estrategias", "estrategias"),
        ("4. Secuencia", "secuencia"),
        ("5. Evaluación", "evaluacion"),
        ("6. Evidencias", "evidencias"),
    ]
    for label, key in links:
        st.sidebar.button(label, key=f"nav-{key}", use_container_width=True,
                          on_click=navegar, args=("dashboard", key))
    st.sidebar.markdown(
        """
        <style>
          [data-testid="stSidebar"] { background: #061d32; }
          [data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
          [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] .stCaption { color: #d8e5f2; }
          .native-sidebar-link {
            display: block; padding: 10px 12px; margin: 3px 0;
            border-radius: 10px; color: #9fb4c9 !important;
            text-decoration: none !important; font-weight: 600;
          }
          .native-sidebar-link:hover, .native-sidebar-link.active {
            background: #fff; color: #08263f !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_overview() -> None:
    st.markdown(
        """
        <style>
          .native-overview { padding: 8px 2px 18px; }
          .native-overview h1 { color: #08263f; font-size: clamp(28px, 4vw, 46px); line-height: .98; margin: 0; }
          .native-overview .lead { color: #0A2F5E; font-size: 17px; font-weight: 700; margin: 8px 0 18px; }
          .native-overview .quick-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
          .native-overview .quick-card { display: block; min-height: 76px; padding: 18px; border: 1px solid #e1e7ed; border-radius: 16px; background: #fff; color: #08263f !important; text-decoration: none !important; box-shadow: 0 2px 8px rgba(8,38,63,.05); }
          .native-overview .quick-card:hover { border-color: #18a957; transform: translateY(-1px); }
          .native-overview .quick-card strong { display: block; font-size: 15px; margin-bottom: 5px; }
          .native-overview .quick-card span { color: #5a6e8a; font-size: 12px; }
          .native-overview .action-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }
          .native-overview .action { display: inline-flex; align-items: center; justify-content: center; padding: 13px 20px; border-radius: 12px; background: #08263f; color: #fff !important; text-decoration: none !important; font-weight: 800; }
          .native-overview .action.green { background: #04a84f; }
          @media (max-width: 640px) { .native-overview .quick-grid { grid-template-columns: 1fr; } }
        </style>
        <section class="native-overview" aria-label="Panel de inicio nativo">
          <h1>¡Maestro! ¡Buen día!</h1>
          <div class="lead">¿En qué te apoyamos?</div>
          <div class="quick-grid">
            <a class="quick-card" href="?page=dashboard&section=diagnostico"><strong>¿Qué hacer hoy?</strong><span>Inicia o continúa el diagnóstico del grupo.</span></a>
            <a class="quick-card" href="?page=dashboard&section=secuencia"><strong>¿Qué vamos a hacer mañana?</strong><span>Consulta la secuencia didáctica y sus tiempos.</span></a>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    left.button("ATpp Intensive →", type="primary", use_container_width=True,
                on_click=navegar, args=("intensive",))
    right.button("Continuar →", use_container_width=True,
                 on_click=navegar, args=("dashboard", "contenidos"))


@st.cache_data(show_spinner=False)
def cargar_matriz_curricular_segura() -> list[dict]:
    try:
        return cargar_matriz_curricular()
    except Exception:
        return []


def render_native_planning(section: str) -> None:
    if section == "diagnostico":
        st.title("1. Diagnóstico")
        st.caption("Bloque nativo de Streamlit · Características, intereses y necesidades del grupo")
        with st.form("native-diagnostico"):
            left, right = st.columns(2)
            with left:
                grupo = st.text_input("Grupo", value=st.session_state.get("diag_grupo", "3° A"))
                contexto = st.selectbox("Contexto del grupo", ["Urbano", "Rural", "Indígena", "Multigrado"], index=0)
            with right:
                fortalezas = st.text_area("Fortalezas observadas", value=st.session_state.get("diag_fortalezas", ""), height=110)
                necesidades = st.text_area("Necesidades prioritarias", value=st.session_state.get("diag_necesidades", ""), height=110)
            if st.form_submit_button("Guardar diagnóstico", type="primary"):
                st.session_state.update(diag_grupo=grupo, diag_fortalezas=fortalezas, diag_necesidades=necesidades)
                st.success("Diagnóstico guardado en esta sesión.")
        st.info("La vista original continúa debajo como respaldo mientras terminamos de trasladar sus tarjetas y modales.")
    elif section == "contenidos":
        st.title("2. Contenidos")
        st.caption("Bloque nativo de Streamlit · Selección curricular y PDA")
        records = cargar_matriz_curricular_segura()
        options = sorted({r["contenido"] for r in records}) or ["Producción e interpretación de textos"]
        selected = st.selectbox("Selecciona un contenido", options, index=0)
        matches = [r for r in records if r["contenido"] == selected]
        if matches:
            record = matches[0]
            st.markdown(f"**Campo formativo:** {record['campo']}  ")
            st.markdown(f"**Fase:** {record['fase']}  ")
            st.info(f"**PDA:** {record['pda']}")
            st.text_area("Metodología sugerida", value=record["metodologia"], height=100, disabled=True)
        if st.button("Guardar selección de contenido", type="primary"):
            st.session_state["contenido_seleccionado"] = selected
            st.success("Contenido seleccionado para la planeación.")
        st.info("La matriz original permanece debajo para conservar filtros y relaciones hasta completar la migración.")
    elif section == "estrategias":
        st.title("3. Estrategias")
        st.caption("Bloque nativo de Streamlit · Diseño de la intervención didáctica")
        with st.form("native-estrategias"):
            estrategias = st.multiselect("Estrategias activas", ["ABP", "Estaciones", "Tutoría entre pares", "Gamificación", "Lectura compartida"], default=st.session_state.get("estrategias", ["ABP"]))
            duracion = st.slider("Duración estimada (minutos)", 20, 240, int(st.session_state.get("duracion", 150)), 10)
            nota = st.text_area("Notas de implementación", value=st.session_state.get("estrategia_nota", ""), height=100)
            if st.form_submit_button("Guardar estrategias", type="primary"):
                st.session_state.update(estrategias=estrategias, duracion=duracion, estrategia_nota=nota)
                st.success("Estrategias guardadas en esta sesión.")
        st.info("La vista React original sigue disponible debajo para comparar el flujo antes de retirar el respaldo.")


def render_native_execution(section: str) -> None:
    if section == "secuencia":
        st.title("4. Secuencia")
        st.caption("Bloque nativo de Streamlit · Inicio, desarrollo y cierre")
        with st.form("native-secuencia"):
            inicio = st.number_input("Inicio (minutos)", min_value=5, max_value=120, value=40, step=5)
            desarrollo = st.number_input("Desarrollo (minutos)", min_value=10, max_value=240, value=70, step=5)
            cierre = st.number_input("Cierre (minutos)", min_value=5, max_value=120, value=40, step=5)
            actividades = st.text_area("Actividades clave", value=st.session_state.get("actividades", "Activación de saberes previos\nTrabajo colaborativo\nSocialización de evidencias"), height=120)
            if st.form_submit_button("Guardar secuencia", type="primary"):
                st.session_state.update(inicio=inicio, desarrollo=desarrollo, cierre=cierre, actividades=actividades)
                st.success(f"Secuencia guardada: {inicio + desarrollo + cierre} minutos.")
        a, b, c = st.columns(3)
        a.metric("Inicio", f"{inicio} min")
        b.metric("Desarrollo", f"{desarrollo} min")
        c.metric("Cierre", f"{cierre} min")
    elif section == "evaluacion":
        st.title("5. Evaluación")
        st.caption("Bloque nativo de Streamlit · Evidencias, criterios e instrumentos")
        with st.form("native-evaluacion"):
            instrumento = st.selectbox("Instrumento principal", ["Rúbrica", "Lista de cotejo", "Autoevaluación", "Guía de observación"])
            criterios = st.multiselect("Criterios", ["Participación", "Comprensión", "Producción", "Colaboración", "Comunicación"], default=["Participación", "Comprensión"])
            evidencia = st.text_input("Evidencia esperada", value=st.session_state.get("evidencia", "Producto escrito y socialización oral"))
            if st.form_submit_button("Guardar evaluación", type="primary"):
                st.session_state.update(instrumento=instrumento, criterios=criterios, evidencia=evidencia)
                st.success("Evaluación guardada en esta sesión.")
        st.write("**Criterios activos:**", ", ".join(criterios) if criterios else "Sin criterios seleccionados")
    elif section == "evidencias":
        st.title("6. Evidencias")
        st.caption("Bloque nativo de Streamlit · Productos, participación y recursos")
        with st.form("native-evidencias"):
            productos = st.text_area("Productos o evidencias", value=st.session_state.get("productos", "Borrador\nProducto final\nRegistro de participación"), height=120)
            recursos = st.text_input("Recursos principales", value=st.session_state.get("recursos", "Cuaderno, textos, proyector y materiales de aula"))
            responsable = st.text_input("Responsable de seguimiento", value=st.session_state.get("responsable", "Docente titular"))
            if st.form_submit_button("Guardar evidencias", type="primary"):
                st.session_state.update(productos=productos, recursos=recursos, responsable=responsable)
                st.success("Evidencias guardadas en esta sesión.")
        st.download_button("Descargar resumen de evidencias", f"{productos}\nRecursos: {recursos}\nResponsable: {responsable}", file_name="evidencias-atpp.txt")


def render_native_planning_summary() -> None:
    state = {
        "diagnostico": {
            "grupo": st.session_state.get("diag_grupo", "3° A"),
            "fortalezas": st.session_state.get("diag_fortalezas", ""),
            "necesidades": st.session_state.get("diag_necesidades", ""),
        },
        "contenido": st.session_state.get("contenido_seleccionado", "Sin seleccionar"),
        "estrategias": st.session_state.get("estrategias", []),
        "duracion": st.session_state.get("duracion", 150),
        "secuencia": {
            "inicio": st.session_state.get("inicio", 40),
            "desarrollo": st.session_state.get("desarrollo", 70),
            "cierre": st.session_state.get("cierre", 40),
        },
        "evaluacion": {
            "instrumento": st.session_state.get("instrumento", "Rúbrica"),
            "criterios": st.session_state.get("criterios", []),
            "evidencia": st.session_state.get("evidencia", ""),
        },
        "evidencias": {
            "productos": st.session_state.get("productos", ""),
            "recursos": st.session_state.get("recursos", ""),
            "responsable": st.session_state.get("responsable", "Docente titular"),
        },
    }
    with st.expander("Resumen integrado de la planeación", expanded=False):
        a, b, c = st.columns(3)
        a.metric("Grupo", state["diagnostico"]["grupo"])
        b.metric("Contenido", state["contenido"][:24])
        c.metric("Duración", f"{state['duracion']} min")
        st.write("**Estrategias:**", ", ".join(state["estrategias"]) or "Sin seleccionar")
        st.write("**Instrumento:**", state["evaluacion"]["instrumento"])
        st.write("**Criterios:**", ", ".join(state["evaluacion"]["criterios"]) or "Sin seleccionar")
        st.download_button(
            "Descargar planeación integrada (JSON)",
            json.dumps(state, ensure_ascii=False, indent=2),
            file_name="planeacion-atpp.json",
            mime="application/json",
        )


def render_dashboard(section: str = "dashboard") -> None:
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] .main .block-container {
            width: 100% !important;
            max-width: none !important;
            padding: 0 24px !important;
          }
          [data-testid="stAppViewContainer"] .main iframe {
            width: 100% !important;
            max-width: none !important;
            display: block;
          }
          .subject-menu { display: flex; gap: 8px; overflow-x: auto; padding: 8px 0 10px; border-bottom: 1px solid #e6edf2; white-space: nowrap; }
          .subject-pill { display: inline-flex; align-items: center; padding: 8px 15px; border: 1px solid #e5eaf0; border-radius: 999px; background: #fff; color: #17324d !important; font: 600 12px/1.1 Inter, Arial, sans-serif; text-decoration: none !important; }
          .subject-pill:hover, .subject-pill.active { background: #08263f; border-color: #08263f; color: #fff !important; }
          .subject-pill.grouped { background: #dff4fb; border-color: #bde7f4; color: #075276 !important; }
          .subject-pill.grouped:hover, .subject-pill.grouped.active { background: #b9e8f5; border-color: #8dd7eb; color: #063c57 !important; }
          .dashboard-native-header {
            display: flex;
            align-items: center;
            gap: 14px;
            min-height: 54px;
            padding: 7px 18px;
            margin: 0 0 8px;
            border-bottom: 1px solid #dfe7ee;
            background: #fff;
            color: #0A2F5E;
            font: 700 14px/1.2 Inter, Arial, sans-serif;
          }
          .dashboard-native-header .brand {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-right: auto;
          }
          .dashboard-native-header .brand-mark {
            padding: 4px 8px;
            border-radius: 8px;
            background: #08263f;
            color: #fff;
            font-weight: 800;
          }
          .dashboard-native-header a {
            padding: 9px 13px;
            border-radius: 18px;
            background: #e2f4fb;
            color: #0A2F5E !important;
            text-decoration: none !important;
            white-space: nowrap;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    subject_key = st.query_params.get("subject", "espanol")
    subject_menu = [
        ("espanol", "Español", False), ("ingles", "Inglés", False), ("artes", "Artes", False),
        ("lengua-materna", "Lengua Indígena como Lengua Materna", False),
        ("lengua-segunda", "Lengua Indígena como Segunda Lengua", False),
        ("saberes", "Saberes y P.C.", True), ("etica", "Ética NyC", True), ("humano", "De lo Humano", True),
    ]
    menu_items = []
    labels = {key: label for key, label, _ in subject_menu}
    subject = labels.get(subject_key, "Español")
    for key, label, grouped in subject_menu:
        active = " active" if key == subject_key else ""
        menu_items.append(f"<a class='subject-pill{' grouped' if grouped else ''}{active}' href='?page=dashboard&subject={key}'>{label}</a>")
    st.markdown(
        "<nav class='subject-menu' aria-label='Asignaturas'>" + "".join(menu_items) + "</nav>",
        unsafe_allow_html=True,
    )
    st.session_state["asignatura"] = subject
    st.markdown(
        f"<div class='dashboard-native-header'><div class='brand'><span class='brand-mark'>ATpp</span><span>3° A Tercer Grado · Matutino · Prim. Benito Juárez · {subject}</span></div><span>ATpp General</span></div>",
        unsafe_allow_html=True,
    )
    render_dashboard_sidebar(section)
    if section == "dashboard":
        render_dashboard_overview()
    else:
        render_native_planning(section)
        render_native_execution(section)
        render_native_planning_summary()


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
  .topbar { display: block !important; }
  #atpp { display: none !important; }
  #intensive { display: block !important; }
  .topbar .nav { display: none !important; }
  .topbar .mobile-toggle, .topbar .demo { display: none !important; }
  .topbar .brand { pointer-events: none; }
  html, body { min-height: 0 !important; height: auto !important; overflow: hidden !important; }
  body { display: block !important; }
  body > main, #atpp-layout { min-height: 0 !important; height: auto !important; }
  body > main { flex: none !important; }
  .authority-footer { margin-top: 0 !important; }
  *, *::before, *::after { scrollbar-width: none !important; }
  *::-webkit-scrollbar { display: none !important; width: 0 !important; height: 0 !important; }
  #root, #atpp-layout, #atpp-menu, #atpp-dashboard, main, .shell, .chalk-content, .modal-box, .p2-recovery, .p2-recovery-card { overflow: hidden !important; }
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
  .back-atpp { display: none !important; }
</style>
<script>
(function () {
  document.title = 'ATpp Intensive — Fases y talleres intensivos';
})();
</script>
"""
    site_html = site_html.replace("</body>", intensive_override + "</body>")
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] .main .block-container,
          [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: none !important;
            padding: 0 !important;
          }
          [data-testid="stIFrame"],
          [data-testid="stIFrame"] iframe,
          iframe[title="st.iframe"] {
            display: block;
            width: 100% !important;
            max-width: none !important;
            height: 2500px !important;
            border: 0 !important;
          }
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
          <span>Fases y talleres intensivos</span>
        </nav>
        """,
        unsafe_allow_html=True,
    )
    st.button("← Volver a ATpp General", key="intensive-back", on_click=navegar,
              args=("dashboard", "dashboard"))
    components.html(site_html, height=2500, scrolling=False)


def render_main_dashboard() -> None:
    """Renderiza únicamente el HTML principal adjunto en un iframe sin scroll interno."""
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] { display: none !important; }
          [data-testid="stAppViewContainer"] .main .block-container,
          [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: none !important;
            padding: 0 !important;
          }
          [data-testid="stIFrame"],
          [data-testid="stIFrame"] iframe,
          iframe[title="st.iframe"] {
            display: block;
            width: 100% !important;
            max-width: none !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if not DASHBOARD_FILE.is_file():
        st.error("No se encontró index.html junto a app.py.")
        st.stop()
    dashboard_html = DASHBOARD_FILE.read_text(encoding="utf-8")
    dashboard_html = dashboard_html.replace(
        "intensive.html", "https://atpp-intensiva.streamlit.app/?page=intensive"
    )
    main_logo_uri = "data:image/png;base64," + base64.b64encode(ATPP_MAIN_LOGO_FILE.read_bytes()).decode("ascii")
    intensive_logo_uri = "data:image/png;base64," + base64.b64encode(ATPP_INTENSIVE_LOGO_FILE.read_bytes()).decode("ascii")
    dashboard_html = dashboard_html.replace("__ATPP_MAIN_LOGO_DATA_URI__", main_logo_uri).replace("__ATPP_INTENSIVE_LOGO_DATA_URI__", intensive_logo_uri)
    dashboard_floor = f"""
    <style id="atpp-main-floor">
      html, body {{ height: auto; overflow: hidden !important; }}
      body {{ display: flex; flex-direction: column; }}
      #root {{ flex: 0 0 auto; }}
      .atpp-dashboard-floor {{
        flex: 0 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 18px;
        min-height: 86px; padding: 16px 28px; box-sizing: border-box;
        background: #061d32; color: #d8e5f2; border-top: 4px solid #2E9E4A;
        font: 600 12px/1.4 Inter, Arial, sans-serif;
      }}
      .atpp-dashboard-floor img {{ width: 190px; height: 48px; object-fit: contain; object-position: left center; }}
      .atpp-dashboard-floor strong {{ color: #fff; font-size: 14px; }}
      .atpp-dashboard-floor small {{ display: block; color: #a9d994; margin-top: 3px; }}
      @media(max-width:680px) {{
        .atpp-dashboard-floor {{ flex-direction: column; align-items: flex-start; padding: 14px 18px; }}
      }}
    </style>
    <script>
      (function() {{
        var intensiveUrl = "https://atpp-intensiva.streamlit.app/?page=intensive";
        document.addEventListener('click', function(event) {{
          var trigger = event.target.closest('button,a');
          if (!trigger || !/ATpp\\s+Intensive/i.test(trigger.textContent || '')) return;
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
          window.top.location.assign(intensiveUrl);
        }}, true);

        var uri = "{main_logo_uri}";
        function replaceMenuLogo() {{
          var menu = document.getElementById('atpp-menu') || document.querySelector('aside');
          if (!menu) return;
          var holder = document.getElementById('atpp-menu-logo');
          if (!holder || !menu.contains(holder)) {{
            holder = document.createElement('div');
            holder.id = 'atpp-menu-logo';
            holder.style.cssText = 'padding:6px 10px 22px;border-bottom:1px solid #dfe7ee;margin-bottom:14px;';
            menu.insertBefore(holder, menu.firstChild);
          }}
          var current = holder.querySelector('img');
          if (!current) {{
            holder.innerHTML = '<img src="' + uri + '" alt="ATpp Sticker" style="width:205px;height:48px;object-fit:contain;object-position:left">';
          }} else if (current.src !== uri) {{
            current.src = uri;
          }}
          Array.from(menu.children).forEach(function(child) {{
            if (child === holder) return;
            var text = (child.innerText || '').trim();
            if (/ATpp|logo/i.test(text) && !/Dashboard|MENÚ PRINCIPAL|PLANEACIÓN/i.test(text)) child.remove();
          }});
          var dashboardLink = Array.from(menu.querySelectorAll('a,button')).find(function(el) {{ return /Dashboard/i.test(el.textContent || ''); }});
          if (dashboardLink) {{
            var navBlock = dashboardLink;
            while (navBlock.parentElement && navBlock.parentElement !== menu) navBlock = navBlock.parentElement;
            var children = Array.from(menu.children);
            var navIndex = children.indexOf(navBlock);
            if (navIndex > 0) children.slice(0, navIndex).forEach(function(child) {{ if (child !== holder) child.remove(); }});
          }}
          menu.querySelectorAll('img').forEach(function(img) {{ if (!holder.contains(img)) img.remove(); }});
        }}
        replaceMenuLogo();
        new MutationObserver(replaceMenuLogo).observe(document.body, {{childList:true,subtree:true}});
      }})();
    </script>
    <footer class="atpp-dashboard-floor" aria-label="Piso de ATpp Intensive">
      <img src="{main_logo_uri}" alt="ATpp Sticker">
      <div><strong>ATpp Intensive</strong><small>Piso de acompañamiento · Hecho por maestros, para maestros.</small></div>
    </footer>
    """
    dashboard_html = dashboard_html.replace("</body>", dashboard_floor + "</body>", 1)
    components.html(
        dashboard_html,
            height=1500,
        scrolling=False,
    )


page = st.query_params.get("page", "dashboard")
if page == "intensive":
    render_intensive()
else:
    render_main_dashboard()
