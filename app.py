import streamlit as st
import streamlit.components.v1 as components
import folium
from branca.element import MacroElement, Template
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import requests
import os
import base64
import json
import urllib.parse
from datetime import datetime
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="PERCET GeoRisk™ | Climate Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "lat" not in st.session_state:
    st.session_state.lat = -6.8112
if "lon" not in st.session_state:
    st.session_state.lon = -79.7326
if "last_click" not in st.session_state:
    st.session_state.last_click = None

LOGO_FILE = "logo.png"

def obtener_logo_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = obtener_logo_base64(LOGO_FILE)

# 2. DICCIONARIO BILINGÜE COMPLETO (ESPAÑOL & ENGLISH)
TEXTOS = {
    "ES": {
        "unit_mm": "mm/día",
        "lang_label": "🌐 MERCADO / IDIOMA:",
        "params_header": "⚙️ PARÁMETROS DEL PROYECTO",
        "client_label": "NOMBRE DEL CLIENTE / OBRA:",
        "rubro_label": "PARTIDA CRÍTICA EN EJECUCIÓN (RUBROS MACRO):",
        "threshold_caption": "UMBRAL TÉCNICO DE ALERTA PARA ESTE RUBRO:",
        "enso_label": "FACTOR DE SEGURIDAD EL NIÑO (ENSO)",
        "enso_help": "Aplica un factor mayorante (+25%) en escenarios de anomalía térmica convectiva.",
        "header_title": "PERCET GEORISK™ | PLATAFORMA DE INTELIGENCIA CLIMÁTICA PARA LA CONSTRUCCIÓN",
        "header_sub": "Monitoreo satelital multibanda y analítica predictiva mediante Machine Learning (Gradient Boosting) para la gestión de riesgos en proyectos de infraestructura.",
        "header_client": "CLIENTE / PROYECTO ACTUAL:",
        "header_rubro": "RUBRO:",
        "sec1_title": "01. LOCALIZACIÓN TÉCNICA DE LA OBRA",
        "lat_label": "LATITUD (DECIMAL)",
        "lon_label": "LONGITUD (DECIMAL)",
        "locate_btn": "📍 LOCALIZAR OBRA",
        "map_hint": "Ingrese coordenadas de planos/GPS o haga clic directamente sobre cualquier punto del mapa.",
        "sec2_title": "02. DIAGNÓSTICO OPERATIVO EN TIEMPO REAL",
        "pdf_sec1_title": "01. DIAGNÓSTICO OPERATIVO EN TIEMPO REAL & KPI SUMMARY",
        "pdf_sec2_title": "02. CRONOGRAMA DE IMPACTO PLUVIAL DIARIO VS. UMBRAL DEL RUBRO",
        "pdf_sec3_title": "03. DICTAMEN DE INGENIERÍA & ACCIONES RECOMENDADAS",
        "pdf_sec4_title": "04. RESUMEN DE MATRIZ METEOROLÓGICA (15 DÍAS)",
        "active_badge": "● MONITOREO ACTIVO",
        "peak_banner": "PICO PRONOSTICADO · {fecha} · UMBRAL {umbral} mm/día",
        "card_forecast": "PRONÓSTICO",
        "card_threshold": "UMBRAL",
        "card_excess": "EXCESO",
        "card_margin": "MARGEN SEGURO",
        "leg_normal": "Normal",
        "leg_warn": "En Precaución",
        "leg_crit": "Crítico",
        "alert_crit_badge": "ALERTA PREVENTIVA · RIESGO ELEVADO",
        "alert_warn_badge": "AVISO OPERATIVO · RIESGO MODERADO",
        "alert_ok_badge": "OPERACIÓN ESTÁNDAR · RIESGO BAJO",
        "diag_crit_desc": "Se pronostica un pico de <b>{pico} mm/día</b> el <b>{fecha}</b>, superando el límite admisible de <b>{umbral} mm/día</b> en <b>+{exceso} mm/día</b>.",
        "diag_warn_desc": "Se pronostica un pico de <b>{pico} mm/día</b> el <b>{fecha}</b>, próximo al umbral establecido de <b>{umbral} mm/día</b>.",
        "diag_ok_desc": "Se pronostica un pico máximo de <b>{pico} mm/día</b>, manteniéndose dentro del margen seguro inferior al umbral de <b>{umbral} mm/día</b>.",
        "rec_title": "ACCIONES RECOMENDADAS PARA EL FRENTE DE OBRA",
        "peak_detected": "Pico detectado",
        "days_affected": "Días afectados",
        "day_unit": "sobre el umbral",
        "sec3_title": "03. INDICADORES CLAVE DE INGENIERÍA DE CAMPO (HORIZONTE 15 DÍAS)",
        "kpi1_title": "1. PRECIPITACIÓN PRONOSTICADA (PICO / ACUM.)",
        "kpi1_sub": "Acumulado 15 días: {acum} mm",
        "kpi2_title": "2. HUMEDAD RELATIVA DEL AMBIENTE / SUELO",
        "kpi2_sub": "Monitoreo de saturación superficial",
        "kpi3_title": "3. ESTADO DE ALERTA FLUVIAL / QUEBRADAS",
        "kpi3_sub": "Coordenada: {lat}, {lon}",
        "q_red": "ALERTA ROJA (Riesgo de Escombros)",
        "q_yellow": "VIGILANCIA (Caudal Moderado)",
        "q_green": "ESTABLE (Sin Activación)",
        "sec4_title": "04. CRONOGRAMA DE IMPACTO PLUVIAL DIARIO VS. UMBRAL DEL RUBRO",
        "pill_peak": "PRECIPITACIÓN MÁXIMA",
        "pill_days": "DÍAS SOBRE EL UMBRAL",
        "pill_thresh": "UMBRAL DE ALERTA",
        "axis_x": "HORIZONTE DE PRONÓSTICO (15 DÍAS)",
        "axis_y": "PRECIPITACIÓN (mm/día)",
        "thresh_tag": "Umbral: {umbral} mm/día",
        "dl_csv": "📥 DESCARGAR MATRIZ DE DATOS (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORTAR REPORTE TÉCNICO PDF (1 HOJA)",
        "exp_title": "🛠️ VER PARÁMETROS DE INFERENCIA TÉCNICA Y MATRIZ METEOROLÓGICA COMPLETA",
        "disclaimer": "<b>🛡️ AVISO LEGAL / DISCLAIMER:</b> PERCET GeoRisk™ es una herramienta analítica de asistencia y soporte basada en modelos predictivos satelitales y probabilísticos. Los resultados constituyen estimaciones técnicas de riesgo y no eximen al usuario de aplicar los protocolos oficiales de seguridad, supervisión en campo y normativas técnicas locales de construcción.",
        "b2b_title": "🏢 ¿NECESITAS EJECUTAR, REMODELAR O PROTEGER TU PROYECTO ANTE EL CLIMA?",
        "b2b_sub": "En <b>PERCET UNIVERSAL HOLDINGS S.A.C.</b> contamos con una red nacional de ingenieros, especialistas BIM/VDC, subcontratistas y maestros de obra calificados para construir con seguridad en todo el Perú.",
        "btn_quote": "📝 SOLICITAR COTIZACIÓN DE OBRA",
        "btn_wa": "💬 HABLAR CON UN ASESOR POR WHATSAPP"
    },
    "EN": {
        "unit_mm": "mm/day",
        "lang_label": "🌐 MARKET / LANGUAGE:",
        "params_header": "⚙️ PROJECT PARAMETERS",
        "client_label": "CLIENT / PROJECT NAME:",
        "rubro_label": "CRITICAL WORK PACKAGE (MACRO SECTORS):",
        "threshold_caption": "TECHNICAL ALERT THRESHOLD FOR THIS SECTOR:",
        "enso_label": "EL NIÑO SAFETY FACTOR (ENSO)",
        "enso_help": "Applies a safety multiplier (+25%) for convective thermal anomaly scenarios.",
        "header_title": "PERCET GEORISK™ | CLIMATE INTELLIGENCE PLATFORM FOR CONSTRUCTION",
        "header_sub": "Multi-band satellite monitoring and Machine Learning predictive analytics (Gradient Boosting) for infrastructure project risk management.",
        "header_client": "CURRENT CLIENT / PROJECT:",
        "header_rubro": "SECTOR:",
        "sec1_title": "01. TECHNICAL SITE LOCATION",
        "lat_label": "LATITUDE (DECIMAL)",
        "lon_label": "LONGITUDE (DECIMAL)",
        "locate_btn": "📍 LOCATE SITE",
        "map_hint": "Enter blueprint/GPS coordinates or click directly on any point on the map.",
        "sec2_title": "02. REAL-TIME OPERATIONAL DIAGNOSTIC",
        "pdf_sec1_title": "01. REAL-TIME OPERATIONAL DIAGNOSTIC & KPI SUMMARY",
        "pdf_sec2_title": "02. DAILY RAINFALL IMPACT SCHEDULE VS. SECTOR THRESHOLD",
        "pdf_sec3_title": "03. ENGINEERING ASSESSMENT & RECOMMENDED ACTIONS",
        "pdf_sec4_title": "04. METEOROLOGICAL MATRIX SUMMARY (15 DAYS)",
        "active_badge": "● ACTIVE MONITORING",
        "peak_banner": "FORECASTED PEAK · {fecha} · THRESHOLD {umbral} mm/day",
        "card_forecast": "FORECAST",
        "card_threshold": "THRESHOLD",
        "card_excess": "EXCESS",
        "card_margin": "SAFE MARGIN",
        "leg_normal": "Normal",
        "leg_warn": "Caution",
        "leg_crit": "Critical",
        "alert_crit_badge": "PREVENTIVE ALERT · HIGH RISK",
        "alert_warn_badge": "OPERATIONAL NOTICE · MODERATE RISK",
        "alert_ok_badge": "STANDARD OPERATION · LOW RISK",
        "diag_crit_desc": "A peak of <b>{pico} mm/day</b> is forecasted on <b>{fecha}</b>, exceeding the established threshold of <b>{umbral} mm/day</b> by <b>+{exceso} mm/day</b>.",
        "diag_warn_desc": "A peak of <b>{pico} mm/day</b> is forecasted on <b>{fecha}</b>, approaching the established threshold of <b>{umbral} mm/day</b>.",
        "diag_ok_desc": "A maximum peak of <b>{pico} mm/day</b> is forecasted, remaining safely below the threshold of <b>{umbral} mm/day</b>.",
        "rec_title": "RECOMMENDED FIELD ACTIONS",
        "peak_detected": "Peak detected",
        "days_affected": "Affected days",
        "day_unit": "above threshold",
        "sec3_title": "03. KEY FIELD ENGINEERING INDICATORS (15-DAY HORIZON)",
        "kpi1_title": "1. FORECASTED PRECIPITATION (PEAK / ACCUM.)",
        "kpi1_sub": "15-day cumulative: {acum} mm",
        "kpi2_title": "2. AMBIENT / SOIL RELATIVE HUMIDITY",
        "kpi2_sub": "Surface saturation monitoring",
        "kpi3_title": "3. FLUVIAL / RAVINE ACTIVATION STATUS",
        "kpi3_sub": "Coordinate: {lat}, {lon}",
        "q_red": "RED ALERT (Debris Flow Risk)",
        "q_yellow": "WATCH (Moderate Flow)",
        "q_green": "STABLE (No Activation)",
        "sec4_title": "04. DAILY RAINFALL IMPACT SCHEDULE VS. SECTOR THRESHOLD",
        "pill_peak": "MAXIMUM PRECIPITATION",
        "pill_days": "DAYS ABOVE THRESHOLD",
        "pill_thresh": "ALERT THRESHOLD",
        "axis_x": "FORECAST HORIZON (15 DAYS)",
        "axis_y": "PRECIPITATION (mm/day)",
        "thresh_tag": "Threshold: {umbral} mm/day",
        "dl_csv": "📥 DOWNLOAD DATA MATRIX (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORT TECHNICAL PDF REPORT (1 PAGE)",
        "exp_title": "🛠️ VIEW TECHNICAL INFERENCE PARAMETERS & FULL METEOROLOGICAL MATRIX",
        "disclaimer": "<b>🛡️ LEGAL DISCLAIMER:</b> PERCET GeoRisk™ is an analytical support tool based on satellite and probabilistic predictive models. Results constitute technical risk estimates and do not exempt the user from applying official safety protocols, field supervision, and local construction codes.",
        "b2b_title": "🌎 CLIMATE INTELLIGENCE & INFRASTRUCTURE SOLUTIONS",
        "b2b_sub": "At <b>PERCET UNIVERSAL HOLDINGS S.A.C.</b>, we drive intelligent climate risk management through enterprise API licensing, specialized hydrological calibration, and a network of qualified engineering professionals. We integrate technology, science, and technical expertise to develop safer, more resilient, and sustainable infrastructure projects.",
        "btn_quote": "📝 REQUEST PROJECT / SAAS QUOTE",
        "btn_wa": "💬 CONTACT SALES ENGINEERING (WHATSAPP)"
    }
}

RUBROS_DATA = [
    {
        "umbral": 3.0,
        "es_name": "1. Geotecnia y Movimiento de Tierras",
        "en_name": "1. Geotechnics & Earthworks",
        "es_recs_crit": [
            "Detener compactación de subrasante inmediatamente por saturación.",
            "Perfilar y proteger taludes expuestos con geomembranas.",
            "Activar bombeo en zanjas y drenaje perimetral de escorrentía."
        ],
        "es_recs_warn": [
            "Monitorear el límite líquido del suelo antes de compactar.",
            "Cubrir acopios de material de préstamo y agregados."
        ],
        "es_recs_ok": [
            "Continuar excavación masiva y compactación según cronograma.",
            "Mantener inspección rutinaria de humedad en canteras."
        ],
        "en_recs_crit": [
            "Halt subgrade compaction immediately due to soil saturation.",
            "Reinforce and cover exposed slopes with geomembranes.",
            "Activate trench pumping and perimeter runoff drainage."
        ],
        "en_recs_warn": [
            "Monitor soil liquid limit prior to compaction operations.",
            "Cover borrow material and aggregate stockpiles."
        ],
        "en_recs_ok": [
            "Proceed with mass excavation and compaction per schedule.",
            "Maintain routine moisture inspection on site."
        ]
    },
    {
        "umbral": 2.0,
        "es_name": "2. Estructuras de Concreto y Acero",
        "en_name": "2. Concrete & Steel Structures",
        "es_recs_crit": [
            "Reprogramar vaciados expuestos de losas y elementos horizontales.",
            "Proteger elementos frescos con mantas plásticas impermeables.",
            "Verificar relación agua/cemento por exceso de humedad superficial."
        ],
        "es_recs_warn": [
            "Instalar carpas preventivas sobre frentes de vaciado activo.",
            "Cubrir acero de refuerzo habilitado para evitar oxidación."
        ],
        "es_recs_ok": [
            "Condiciones óptimas para vaciado de concreto estructural.",
            "Proceder con encofrado y montaje de armaduras sin restricción."
        ],
        "en_recs_crit": [
            "Reschedule exposed slab and horizontal concrete pours.",
            "Protect fresh concrete elements with waterproof plastic tarps.",
            "Check water/cement ratio against surface moisture excess."
        ],
        "en_recs_warn": [
            "Deploy preventive tents over active concrete pouring fronts.",
            "Cover staged rebar to prevent premature surface oxidation."
        ],
        "en_recs_ok": [
            "Optimal conditions for structural concrete placement.",
            "Proceed with formwork and rebar assembly without restriction."
        ]
    },
    {
        "umbral": 1.0,
        "es_name": "3. Arquitectura y Cierre de Envolvente",
        "en_name": "3. Architecture & Building Envelope",
        "es_recs_crit": [
            "Paralizar aplicación de pintura exterior y recubrimientos.",
            "Suspender colocación de mantos impermeabilizantes en techos.",
            "Sellar vanos y proteger materiales de acabados en almacén."
        ],
        "es_recs_warn": [
            "Restringir acabados en fachadas expuestas al viento húmedo.",
            "Priorizar partidas de tabiquería y acabados interiores."
        ],
        "es_recs_ok": [
            "Clima seco favorable para pintura exterior y sellado de fachadas.",
            "Ejecutar instalación de mantos impermeables según plan."
        ],
        "en_recs_crit": [
            "Halt exterior painting and facade coating applications.",
            "Suspend installation of roof waterproofing membranes.",
            "Seal openings and protect finishing materials in storage."
        ],
        "en_recs_warn": [
            "Restrict facade finishes exposed to wind-driven moisture.",
            "Prioritize interior drywall and finishing work packages."
        ],
        "en_recs_ok": [
            "Dry weather favorable for exterior painting and facade sealing.",
            "Execute roof waterproofing membrane installation as planned."
        ]
    },
    {
        "umbral": 5.0,
        "es_name": "4. Instalaciones y Redes de Servicio",
        "en_name": "4. MEP Installations & Utility Networks",
        "es_recs_crit": [
            "Cortar energía temporal en frentes descubiertos por riesgo eléctrico.",
            "Suspender tendido de redes en zanjas con riesgo de inundación.",
            "Asegurar grupos electrógenos y tableros con cerramiento IP65."
        ],
        "es_recs_warn": [
            "Aislar empalmes y tableros provisionales de obra.",
            "Entibar y proteger zanjas de tuberías sanitarias/hidráulicas."
        ],
        "es_recs_ok": [
            "Operación segura para montaje electromecánico y tendido de redes.",
            "Realizar pruebas hidráulicas y de presión con normalidad."
        ],
        "en_recs_crit": [
            "Cut temporary power in open fronts due to electrocution hazard.",
            "Suspend utility trenching in areas prone to waterlogging.",
            "Secure generators and switchboards with IP65 enclosures."
        ],
        "en_recs_warn": [
            "Insulate splices and temporary site distribution boards.",
            "Shore and protect sanitary/hydraulic pipeline trenches."
        ],
        "en_recs_ok": [
            "Safe operation for MEP assembly and utility network laying.",
            "Perform hydraulic and pressure testing as scheduled."
        ]
    }
]

# 3. ESTILO CORPORATIVO UNIFICADO (RESPETANDO LOS ÍCONOS NATIVOS DE STREAMLIT)
def aplicar_estilo_corporativo():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    /* Aplicar Montserrat a textos sin romper Material Symbols de Streamlit */
    html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea, td, th {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Proteger explícitamente todos los íconos del sistema (evita keyboard_double, arrow_right, upload, etc.) */
    span[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons, [translate="no"] {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
    }

    .stApp {
        background-color: #f0f4f8;
    }

    .stAppDeployButton {
        display: none !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
        background-color: #f8fafc;
        border-right: 1px solid #cbd5e1;
    }

    section[data-testid="stSidebar"] label p {
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        color: #041e42 !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase !important;
    }

    /* Encabezado Superior Derecho armonizado con el logo */
    .corporate-header {
        background: linear-gradient(135deg, #020b1e 0%, #042454 55%, #004799 100%);
        padding: 1.8rem 2.4rem;
        border-radius: 14px;
        color: white;
        box-shadow: 0 10px 25px rgba(2, 11, 30, 0.25);
        margin-bottom: 1.6rem;
        border-bottom: 4px solid #00b4d8;
        border-left: 6px solid #38bdf8;
    }
    .corporate-title {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #ffffff !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase;
        line-height: 1.25 !important;
    }
    .corporate-subtitle {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: #e0f2fe !important;
        margin-top: 0.55rem !important;
        margin-bottom: 0.65rem !important;
    }
    .corporate-client {
        font-size: 1.08rem !important;
        color: #38bdf8 !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Títulos de sección */
    .sec-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #ffffff;
        padding: 0.85rem 1.25rem;
        border-radius: 10px;
        border-left: 5px solid #042454;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .sec-header-title {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #020b1e !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 !important;
    }
    .status-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 5px 12px;
        border-radius: 20px;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    /* Latitud y Longitud de mayor tamaño */
    div[data-testid="stNumberInput"] label p {
        font-size: 1.02rem !important;
        font-weight: 800 !important;
        color: #020b1e !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 1.12rem !important;
        font-weight: 700 !important;
        color: #042454 !important;
    }

    /* Mapa sin espacio blanco */
    iframe[title="streamlit_folium.st_folium"] {
        width: 100% !important;
        min-width: 100% !important;
        border-radius: 12px !important;
        border: 2px solid #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        display: block !important;
    }

    /* Botones ejecutivos */
    .stButton > button {
        background: linear-gradient(90deg, #020b1e 0%, #004799 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
        border-radius: 8px !important;
        border: 1px solid #38bdf8 !important;
        padding: 0.65rem 1rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #004799 0%, #00b4d8 100%) !important;
        box-shadow: 0 4px 12px rgba(0, 180, 216, 0.35) !important;
    }

    /* Tarjetas del Diagnóstico Operativo */
    .diag-subbanner {
        background-color: #042454;
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 800;
        text-align: center;
        padding: 8px 12px;
        border-radius: 8px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .mini-kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 12px;
    }
    .mini-kpi-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #042454;
        border-radius: 10px;
        padding: 10px 12px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .mini-kpi-label {
        font-size: 0.75rem;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .mini-kpi-val {
        font-size: 1.65rem;
        font-weight: 900;
        color: #020b1e;
        line-height: 1.15;
        margin: 4px 0 2px 0;
    }
    .mini-kpi-unit {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
    }

    /* Tarjeta de Diagnóstico (Sección 02 limpia, sin acciones recomendadas) */
    .diag-alert-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 18px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 10px;
    }
    .diag-badge-crit {
        display: inline-block;
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .diag-badge-warn {
        display: inline-block;
        background-color: #fef3c7;
        color: #b45309;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .diag-badge-ok {
        display: inline-block;
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Punto 03: Tarjetas KPI de Ingeniería */
    .field-kpi-card {
        background: #ffffff;
        border-radius: 12px;
        border-left: 6px solid #042454;
        padding: 18px 22px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        height: 100%;
    }
    .field-kpi-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 8px;
    }
    .field-kpi-value {
        font-size: 2.1rem;
        font-weight: 900;
        color: #020b1e;
        margin-bottom: 8px;
        line-height: 1.1;
    }
    .field-kpi-pill {
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        background-color: #e0f2fe;
        color: #0369a1;
    }

    /* Punto 04: Píldoras Ejecutivas y Bloque Único de Acciones Recomendadas */
    .exec-pill-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .exec-icon-circle {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .exec-recs-only-banner {
        border-radius: 12px;
        padding: 18px 24px;
        margin-top: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    }

    /* Banner B2B y Disclaimer */
    .b2b-banner {
        background: linear-gradient(135deg, #020b1e 0%, #042454 100%);
        color: white;
        padding: 2.2rem;
        border-radius: 14px;
        text-align: center;
        border: 2px solid #00b4d8;
        box-shadow: 0 10px 25px rgba(2, 11, 30, 0.22);
        margin-top: 1.8rem;
        margin-bottom: 1rem;
    }
    .legal-disclaimer {
        font-size: 0.82rem;
        color: #475569;
        background-color: #e2e8f0;
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 1.2rem;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

aplicar_estilo_corporativo()

# 4. BARRA LATERAL LIMPIA
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    
    st.markdown("<hr style='margin: 0.6rem 0;'>", unsafe_allow_html=True)
    
    idioma_sel = st.radio(
        "🌐 MERCADO / IDIOMA:",
        ["🇵🇪 Español (Construcción & Obras)", "🌎 English (Global SaaS)"],
        index=0
    )
    LANG = "ES" if "Español" in idioma_sel else "EN"
    T = TEXTOS[LANG]
    UNIT_MM = T["unit_mm"]
    
    st.markdown("<hr style='margin: 0.6rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight:800; color:#020b1e; font-size:0.95rem; letter-spacing:0.5px;'>{T['params_header']}</p>", unsafe_allow_html=True)
    
    nombre_proyecto = st.text_input(T["client_label"], value="Consorcio Qalvan")
    
    opciones_rubros = [r["es_name"] if LANG == "ES" else r["en_name"] for r in RUBROS_DATA]
    idx_rubro = st.selectbox(
        T["rubro_label"],
        range(len(RUBROS_DATA)),
        format_func=lambda i: opciones_rubros[i],
        index=1
    )
    
    rubro_actual = RUBROS_DATA[idx_rubro]
    nombre_rubro_activo = rubro_actual["es_name"] if LANG == "ES" else rubro_actual["en_name"]
    umbral_critico = rubro_actual["umbral"]
    
    st.caption(f"{T['threshold_caption']} **> {umbral_critico} {UNIT_MM}**")
    
    modo_enso = st.toggle(T["enso_label"], value=True, help=T["enso_help"])

# 5. MODAL DE COTIZACIÓN BILINGÜE
@st.dialog("📝 PERCET UNIVERSAL HOLDINGS S.A.C.")
def mostrar_modal_cotizacion():
    if LANG == "ES":
        st.markdown("Complete los datos de su proyecto para recibir una propuesta técnico-económica.")
        emp = st.text_input("Empresa / Cliente:")
        cont = st.text_input("Correo o Teléfono:")
        t_proy = st.selectbox("Tipo de Proyecto:", [
            "Obras de Tierra y Pavimentación",
            "Edificación Estructural y Vivienda",
            "Infraestructura Comercial / Industrial",
            "Mitigación Hidrológica y Drenaje"
        ])
        archivo = st.file_uploader("Adjuntar Plano o Expediente (Opcional):", type=["pdf", "png", "jpg"])
        if st.button("ENVIAR SOLICITUD", type="primary"):
            if emp and cont:
                st.success(f"✅ Solicitud registrada para {emp} en ({st.session_state.lat}, {st.session_state.lon}).")
    else:
        st.markdown("Complete your project details to receive a technical and commercial proposal.")
        emp = st.text_input("Company / Client Name:")
        cont = st.text_input("Corporate Email or Phone:")
        t_proy = st.selectbox("Service Required:", [
            "Enterprise SaaS API License",
            "Custom Basin ML Calibration",
            "Infrastructure & Mitigation Engineering"
        ])
        archivo = st.file_uploader("Upload Blueprint or RFP (Optional):", type=["pdf", "png", "jpg"])
        if st.button("SUBMIT REQUEST", type="primary"):
            if emp and cont:
                st.success(f"✅ Request registered for {emp} at ({st.session_state.lat}, {st.session_state.lon}).")

# 6. ENCABEZADO SUPERIOR
st.markdown(f"""
<div class="corporate-header">
    <p class="corporate-title">{T['header_title']}</p>
    <p class="corporate-subtitle">{T['header_sub']}</p>
    <p class="corporate-client">{T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {T['header_rubro']} {nombre_rubro_activo}</p>
</div>
""", unsafe_allow_html=True)

# 7. EXTRACCIÓN DE DATOS REALES OPEN-METEO
lat_actual = st.session_state.lat
lon_actual = st.session_state.lon

url_api = (
    f"https://api.open-meteo.com/v1/forecast?latitude={lat_actual}&longitude={lon_actual}"
    f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
    f"precipitation_sum,precipitation_probability_max,wind_speed_10m_max,"
    f"wind_direction_10m_dominant,shortwave_radiation_sum"
    f"&hourly=relative_humidity_2m,surface_pressure"
    f"&timezone=America%2FLima&forecast_days=15"
)

try:
    resp = requests.get(url_api, timeout=10)
    data = resp.json()
    
    df_diario = pd.DataFrame({
        "Fecha": pd.to_datetime(data["daily"]["time"]).strftime('%d-%b'),
        "Temp. Máx (°C)": data["daily"]["temperature_2m_max"],
        "Temp. Mín (°C)": data["daily"]["temperature_2m_min"],
        "Temp. Prom (°C)": data["daily"]["temperature_2m_mean"],
        "Radiación (MJ/m²)": data["daily"]["shortwave_radiation_sum"],
        "Viento Máx (km/h)": data["daily"]["wind_speed_10m_max"],
        "Dirección Viento (°)": data["daily"]["wind_direction_10m_dominant"],
        "Prob. Lluvia (%)": data["daily"]["precipitation_probability_max"],
        "Precipitación Base (mm)": data["daily"]["precipitation_sum"]
    })
    
    humedad_media = round(float(np.mean(data["hourly"]["relative_humidity_2m"])), 1)
    presion_media = round(float(np.mean(data["hourly"]["surface_pressure"])), 1)
    
    factor_seguridad = 1.25 if modo_enso else 1.0
    df_diario["Pronóstico"] = (df_diario["Precipitación Base (mm)"] * factor_seguridad).round(1)
    
    pico_max_dia = float(df_diario["Pronóstico"].max())
    fecha_pico = df_diario.loc[df_diario["Pronóstico"].idxmax(), "Fecha"]
    lluvia_acumulada = round(float(df_diario["Pronóstico"].sum()), 1)
    dias_criticos = int((df_diario["Pronóstico"] > umbral_critico).sum())
    diferencia_umbral = round(pico_max_dia - umbral_critico, 1)

    if pico_max_dia >= 15.0 or lluvia_acumulada >= 60.0:
        estado_quebrada = f"🔴 {T['q_red']}"
    elif pico_max_dia >= 5.0 or lluvia_acumulada >= 25.0:
        estado_quebrada = f"🟡 {T['q_yellow']}"
    else:
        estado_quebrada = f"🟢 {T['q_green']}"

    # 8. SECCIÓN 01 (MAPA) Y SECCIÓN 02 (DIAGNÓSTICO SIN ACCIONES REPETIDAS)
    col_mapa, col_panel = st.columns([1.25, 1], gap="large")

    with col_mapa:
        st.markdown(f"""
        <div class="sec-header">
            <p class="sec-header-title">📍 {T['sec1_title']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1.8, 1.8, 1.4])
        with c1:
            lat_input = st.number_input(T["lat_label"], value=float(st.session_state.lat), format="%.4f", step=0.0010)
        with c2:
            lon_input = st.number_input(T["lon_label"], value=float(st.session_state.lon), format="%.4f", step=0.0010)
        with c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            buscar_btn = st.button(T["locate_btn"])
        
        if buscar_btn:
            st.session_state.lat = round(lat_input, 4)
            st.session_state.lon = round(lon_input, 4)
            st.rerun()
        
        st.caption(T["map_hint"])
        
        m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=12, tiles="OpenStreetMap")
        folium.Marker(
            [st.session_state.lat, st.session_state.lon],
            popup=f"<b>{nombre_proyecto}</b><br>Lat: {st.session_state.lat}<br>Lon: {st.session_state.lon}",
            tooltip=nombre_proyecto,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        folium.LatLngPopup().add_to(m)

        oeste_letra = "O" if LANG == "ES" else "W"
        compass_html = f"""
        {{% macro html(this, kwargs) %}}
        <div style="
            position: fixed; 
            bottom: 18px; left: 18px; width: 78px; height: 78px; 
            z-index: 9999; background: rgba(2, 11, 30, 0.88);
            border: 2px solid #38bdf8; border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
            display: flex; align-items: center; justify-content: center;
            pointer-events: none; font-family: 'Montserrat', sans-serif;">
            <svg viewBox="0 0 100 100" width="70" height="70">
                <circle cx="50" cy="50" r="44" fill="none" stroke="#334155" stroke-width="1.5"/>
                <text x="50" y="15" fill="#38bdf8" font-size="13" font-weight="900" text-anchor="middle">N</text>
                <text x="50" y="94" fill="#cbd5e1" font-size="11" font-weight="700" text-anchor="middle">S</text>
                <text x="90" y="54" fill="#cbd5e1" font-size="11" font-weight="700" text-anchor="middle">E</text>
                <text x="10" y="54" fill="#cbd5e1" font-size="11" font-weight="700" text-anchor="middle">{oeste_letra}</text>
                <text x="77" y="27" fill="#64748b" font-size="8" font-weight="700" text-anchor="middle">NE</text>
                <text x="23" y="27" fill="#64748b" font-size="8" font-weight="700" text-anchor="middle">N{oeste_letra}</text>
                <text x="77" y="80" fill="#64748b" font-size="8" font-weight="700" text-anchor="middle">SE</text>
                <text x="23" y="80" fill="#64748b" font-size="8" font-weight="700" text-anchor="middle">S{oeste_letra}</text>
                <polygon points="50,20 57,50 50,44 43,50" fill="#ef4444"/>
                <polygon points="50,80 57,50 50,56 43,50" fill="#e2e8f0"/>
                <circle cx="50" cy="50" r="3.5" fill="#020b1e" stroke="#38bdf8" stroke-width="1.5"/>
            </svg>
        </div>
        {{% endmacro %}}
        """
        compass = MacroElement()
        compass._template = Template(compass_html)
        m.get_root().add_child(compass)
        
        map_data = st_folium(m, height=430, use_container_width=True)
        
        if map_data and map_data.get("last_clicked"):
            click_coords = (round(map_data["last_clicked"]["lat"], 4), round(map_data["last_clicked"]["lng"], 4))
            if click_coords != st.session_state.last_click:
                st.session_state.last_click = click_coords
                st.session_state.lat, st.session_state.lon = click_coords
                st.rerun()

    # PANEL DERECHO: SECCIÓN 02 LIMPIA (SIN ACCIONES RECOMENDADAS)
    with col_panel:
        st.markdown(f"""
        <div class="sec-header">
            <p class="sec-header-title">🧭 {T['sec2_title']}</p>
            <span class="status-badge">{T['active_badge']}</span>
        </div>
        <div class="diag-subbanner">
            {T['peak_banner'].format(fecha=fecha_pico.upper(), umbral=f"{umbral_critico:.1f}")}
        </div>
        """, unsafe_allow_html=True)

        etiqueta_dif = T["card_excess"] if diferencia_umbral > 0 else T["card_margin"]
        color_dif = "#dc2626" if diferencia_umbral > 0 else "#16a34a"
        signo_dif = f"+{diferencia_umbral:.1f}" if diferencia_umbral > 0 else f"{diferencia_umbral:.1f}"

        st.markdown(f"""
        <div class="mini-kpi-grid">
            <div class="mini-kpi-card" style="border-top-color: #004799;">
                <div class="mini-kpi-label">{T['card_forecast']}</div>
                <div class="mini-kpi-val">{pico_max_dia:.1f}</div>
                <div class="mini-kpi-unit">{UNIT_MM}</div>
            </div>
            <div class="mini-kpi-card" style="border-top-color: #475569;">
                <div class="mini-kpi-label">{T['card_threshold']}</div>
                <div class="mini-kpi-val">{umbral_critico:.1f}</div>
                <div class="mini-kpi-unit">{UNIT_MM}</div>
            </div>
            <div class="mini-kpi-card" style="border-top-color: {color_dif};">
                <div class="mini-kpi-label">{etiqueta_dif}</div>
                <div class="mini-kpi-val" style="color: {color_dif};">{signo_dif}</div>
                <div class="mini-kpi-unit">{UNIT_MM}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        max_escala = max(10.0, float(np.ceil(max(pico_max_dia, umbral_critico * 2) / 2.0) * 2.0))
        paso_tick = 2 if max_escala <= 12 else round(max_escala / 5)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pico_max_dia,
            number={'suffix': f" {UNIT_MM}", 'valueformat': ".1f", 'font': {'size': 36, 'color': '#020b1e', 'family': 'Montserrat'}},
            gauge={
                'axis': {
                    'range': [0, max_escala],
                    'tickmode': 'linear',
                    'tick0': 0,
                    'dtick': paso_tick,
                    'tickwidth': 2,
                    'tickcolor': "#020b1e",
                    'tickfont': {'size': 14, 'color': '#020b1e', 'family': 'Montserrat'}
                },
                'bar': {'color': "#020b1e", 'thickness': 0.32},
                'bgcolor': "#ffffff",
                'borderwidth': 1,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, umbral_critico * 0.7], 'color': "#22c55e"},
                    {'range': [umbral_critico * 0.7, umbral_critico], 'color': "#facc15"},
                    {'range': [umbral_critico, max_escala], 'color': "#ef4444"}
                ],
                'threshold': {
                    'line': {'color': "#020b1e", 'width': 5},
                    'thickness': 0.85,
                    'value': umbral_critico
                }
            }
        ))
        fig_gauge.update_layout(
            height=220,
            margin=dict(l=28, r=28, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'family': 'Montserrat'}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(f"""
        <div style="display:flex; justify-content:center; gap:20px; font-size:0.8rem; font-weight:700; margin-top:-6px; margin-bottom:10px;">
            <span>🟢 {T['leg_normal']} (&lt;{umbral_critico*0.7:.1f})</span>
            <span>🟡 {T['leg_warn']} ({umbral_critico*0.7:.1f}-{umbral_critico:.1f})</span>
            <span>🔴 {T['leg_crit']} (&gt;{umbral_critico:.1f})</span>
        </div>
        """, unsafe_allow_html=True)

        if pico_max_dia > umbral_critico:
            badge_cls = "diag-badge-crit"
            badge_txt = f"🚨 {T['alert_crit_badge']}"
            desc_txt = T["diag_crit_desc"].format(pico=f"{pico_max_dia:.1f}", fecha=fecha_pico, umbral=f"{umbral_critico:.1f}", exceso=f"{diferencia_umbral:.1f}")
            lista_recs = rubro_actual["es_recs_crit"] if LANG == "ES" else rubro_actual["en_recs_crit"]
        elif pico_max_dia >= umbral_critico * 0.7:
            badge_cls = "diag-badge-warn"
            badge_txt = f"⚠️ {T['alert_warn_badge']}"
            desc_txt = T["diag_warn_desc"].format(pico=f"{pico_max_dia:.1f}", fecha=fecha_pico, umbral=f"{umbral_critico:.1f}")
            lista_recs = rubro_actual["es_recs_warn"] if LANG == "ES" else rubro_actual["en_recs_warn"]
        else:
            badge_cls = "diag-badge-ok"
            badge_txt = f"✅ {T['alert_ok_badge']}"
            desc_txt = T["diag_ok_desc"].format(pico=f"{pico_max_dia:.1f}", umbral=f"{umbral_critico:.1f}")
            lista_recs = rubro_actual["es_recs_ok"] if LANG == "ES" else rubro_actual["en_recs_ok"]

        # Tarjeta de Diagnóstico (Imagen 3: Sin Acciones Recomendadas para evitar redundancia)
        st.markdown(f"""
        <div class="diag-alert-card">
            <div class="{badge_cls}">{badge_txt}</div>
            <div style="font-size:1.05rem; font-weight:800; color:#020b1e; margin-bottom:6px;">{nombre_rubro_activo}</div>
            <div style="font-size:0.92rem; color:#334155; margin-bottom:12px; line-height:1.45;">{desc_txt}</div>
            <div style="font-size:0.84rem; font-weight:700; color:#475569; border-top:1px solid #e2e8f0; padding-top:8px;">
                📅 {T['peak_detected']}: <b style="color:#020b1e;">{fecha_pico}</b> &nbsp;·&nbsp; ⚠️ {T['days_affected']}: <b style="color:#dc2626;">{dias_criticos}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 9. SECCIÓN 03: INDICADORES CLAVE DE INGENIERÍA DE CAMPO
    st.markdown(f"""
    <div class="sec-header">
        <p class="sec-header-title">📊 {T['sec3_title']}</p>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="field-kpi-card">
            <div class="field-kpi-title">{T['kpi1_title']}</div>
            <div class="field-kpi-value">{pico_max_dia:.1f} {UNIT_MM}</div>
            <span class="field-kpi-pill">🌧️ {T['kpi1_sub'].format(acum=lluvia_acumulada)}</span>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="field-kpi-card">
            <div class="field-kpi-title">{T['kpi2_title']}</div>
            <div class="field-kpi-value">{humedad_media} %</div>
            <span class="field-kpi-pill">💧 {T['kpi2_sub']}</span>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="field-kpi-card">
            <div class="field-kpi-title">{T['kpi3_title']}</div>
            <div class="field-kpi-value" style="font-size: 1.45rem; padding-top:6px;">{estado_quebrada}</div>
            <span class="field-kpi-pill">📍 {T['kpi3_sub'].format(lat=lat_actual, lon=lon_actual)}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 10. SECCIÓN 04: CRONOGRAMA DE IMPACTO CON NUEVOS TÍTULOS Y BLOQUE INFERIOR SIN REDUNDANCIA
    st.markdown(f"""
    <div class="sec-header">
        <p class="sec-header-title">📅 {T['sec4_title']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Fila Superior: PRECIPITACIÓN MÁXIMA | DÍAS SOBRE EL UMBRAL | UMBRAL DE ALERTA (Imágenes 5 y 8)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"""
        <div class="exec-pill-card">
            <div class="exec-icon-circle" style="background:#e0f2fe; color:#0284c7;">💧</div>
            <div>
                <div style="font-size:0.82rem; font-weight:800; color:#475569; text-transform:uppercase;">{T['pill_peak']}</div>
                <div style="display:flex; align-items:baseline; gap:12px;">
                    <span style="font-size:1.9rem; font-weight:900; color:#dc2626;">{pico_max_dia:.1f} <small style="font-size:0.9rem; color:#475569;">{UNIT_MM}</small></span>
                    <span style="font-size:0.88rem; font-weight:700; color:#334155; border-left:2px solid #cbd5e1; padding-left:10px;">📅 {fecha_pico}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="exec-pill-card">
            <div class="exec-icon-circle" style="background:#ffedd5; color:#ea580c;">🛡️</div>
            <div>
                <div style="font-size:0.82rem; font-weight:800; color:#475569; text-transform:uppercase;">{T['pill_days']}</div>
                <div>
                    <span style="font-size:1.9rem; font-weight:900; color:#dc2626;">{dias_criticos}</span>
                    <span style="font-size:0.92rem; font-weight:700; color:#475569;"> {T['day_unit']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
        <div class="exec-pill-card">
            <div class="exec-icon-circle" style="background:#e0e7ff; color:#1d4ed8;">🧭</div>
            <div>
                <div style="font-size:0.82rem; font-weight:800; color:#475569; text-transform:uppercase;">{T['pill_thresh']}</div>
                <div>
                    <span style="font-size:1.9rem; font-weight:900; color:#020b1e;">{umbral_critico:.1f}</span>
                    <span style="font-size:0.92rem; font-weight:700; color:#475569;"> {UNIT_MM}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    colores_barras = [
        "#ef4444" if val > umbral_critico else ("#f59e0b" if val >= umbral_critico * 0.7 else "#1d70b8")
        for val in df_diario["Pronóstico"]
    ]
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_diario["Fecha"],
        y=df_diario["Pronóstico"],
        marker_color=colores_barras,
        text=[f"<b>{v:.1f}</b>" if v > 0 else "0" for v in df_diario["Pronóstico"]],
        textposition="outside",
        name=T["card_forecast"]
    ))
    fig_bar.add_trace(go.Scatter(
        x=df_diario["Fecha"],
        y=df_diario["Pronóstico"],
        mode="lines",
        line=dict(color="rgba(4, 36, 84, 0.35)", width=2, shape="spline"),
        hoverinfo="skip",
        showlegend=False
    ))
    fig_bar.add_hline(
        y=umbral_critico,
        line_dash="dash",
        line_color="#dc2626",
        line_width=2.5,
        annotation_text=f"<b>{T['thresh_tag'].format(umbral=f'{umbral_critico:.1f}')}</b>",
        annotation_position="top right",
        annotation_font=dict(color="white", size=12, family="Montserrat"),
        annotation_bgcolor="#dc2626",
        annotation_borderpad=6
    )
    fig_bar.update_layout(
        height=350,
        xaxis_title=f"<b>{T['axis_x']}</b>",
        yaxis_title=f"<b>{T['axis_y']}</b>",
        yaxis=dict(range=[0, max(umbral_critico * 1.6, pico_max_dia * 1.25, 5.0)]),
        paper_bgcolor="white",
        plot_bgcolor="#ffffff",
        font=dict(family="Montserrat", color="#020b1e"),
        margin=dict(l=20, r=20, t=25, b=20),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Bloque Inferior (Imagen 4: Únicamente las Acciones Recomendadas, sin duplicar la alerta ni los días afectados)
    checks_cols_html = "".join([
        f"<div style='background:rgba(255,255,255,0.85); padding:10px 14px; border-radius:8px; border-left:4px solid #dc2626; font-weight:600; font-size:0.88rem; color:#1e293b;'><span style='color:#dc2626; font-weight:900;'>✔</span> {r}</div>"
        for r in lista_recs
    ])
    checks_pdf_html = "".join([f"<div style='margin-bottom:4px; font-weight:600; color:#1e293b;'><span style='color:#dc2626;'>✔</span> {r}</div>" for r in lista_recs])
    
    bg_banner_9 = "#fff1f2" if pico_max_dia > umbral_critico else ("#fffbeb" if pico_max_dia >= umbral_critico * 0.7 else "#f0fdf4")
    border_banner_9 = "#fecdd3" if pico_max_dia > umbral_critico else ("#fde68a" if pico_max_dia >= umbral_critico * 0.7 else "#bbf7d0")
    color_titulo_9 = "#be123c" if pico_max_dia > umbral_critico else ("#b45309" if pico_max_dia >= umbral_critico * 0.7 else "#15803d")

    st.markdown(f"""
    <div style="text-align:center; font-size:0.85rem; font-weight:700; color:#334155; margin-top:-10px; margin-bottom:12px;">
        <span style="color:#1d70b8;">●</span> {T['leg_normal']} &nbsp;&nbsp;&nbsp;
        <span style="color:#f59e0b;">●</span> {T['leg_warn']} &nbsp;&nbsp;&nbsp;
        <span style="color:#ef4444;">●</span> {T['leg_crit']}
    </div>
    <div class="exec-recs-only-banner" style="background:{bg_banner_9}; border: 1.5px solid {border_banner_9};">
        <div style="font-size:0.95rem; font-weight:900; color:#020b1e; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.4px;">
            📋 {T['rec_title']} ({nombre_rubro_activo})
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:12px;">
            {checks_cols_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 11. GENERADOR DE INFOGRAFÍA PDF EN 1 SOLA HOJA A4 (IMAGEN 7 MEJORADA: TÍTULOS LIMPIOS Y GRÁFICA MÁS GRANDE)
    def disparar_pdf_infografia_una_hoja():
        fechas_js = json.dumps(df_diario["Fecha"].tolist())
        valores_js = json.dumps(df_diario["Pronóstico"].tolist())
        colores_js = json.dumps(colores_barras)
        logo_img_tag = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:60px; border-radius:8px;">' if LOGO_B64 else "<b>PERCET</b>"
        fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")
        max_chart_pdf = round(max(pico_max_dia * 1.28, umbral_critico * 1.45, 4.0), 1)

        html_infografia = f"""
        <script>
        function abrirInfografiaPDF() {{
            var win = window.open("", "_blank", "width=1100,height=850");
            var fechas = {fechas_js};
            var valores = {valores_js};
            var colores = {colores_js};
            var maxVal = {max_chart_pdf};
            
            var chartTop = 28;
            var chartBottom = 188;
            var chartHeight = chartBottom - chartTop;
            var barrasSvg = "";

            for (var i = 0; i < fechas.length; i++) {{
                var x = 38 + i * 45;
                var h = (valores[i] / maxVal) * chartHeight;
                var y = chartBottom - h;
                barrasSvg += '<rect x="' + x + '" y="' + y + '" width="31" height="' + h + '" fill="' + colores[i] + '" rx="4"/>';
                barrasSvg += '<text x="' + (x + 15.5) + '" y="' + (y - 6) + '" font-size="10.5" font-weight="800" text-anchor="middle" fill="#020b1e">' + valores[i] + '</text>';
                barrasSvg += '<text x="' + (x + 15.5) + '" y="206" font-size="9.5" font-weight="700" text-anchor="middle" fill="#334155">' + fechas[i] + '</text>';
            }}
            var yUmbral = chartBottom - ({umbral_critico} / maxVal) * chartHeight;

            var contenido = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>PERCET_GeoRisk_{nombre_proyecto}</title>
                <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">
                <style>
                    @page {{ size: A4 portrait; margin: 9mm; }}
                    * {{ box-sizing: border-box; font-family: 'Montserrat', sans-serif; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
                    body {{ margin: 0; padding: 0; background: #ffffff; color: #020b1e; }}
                    .page {{ width: 100%; border: 2px solid #042454; border-radius: 12px; padding: 15px; }}
                    .header {{ display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #020b1e 0%, #042454 100%); color: white; padding: 14px 18px; border-radius: 10px; border-bottom: 4px solid #00b4d8; margin-bottom: 12px; }}
                    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }}
                    .card {{ border: 1px solid #cbd5e1; border-top: 4px solid #042454; border-radius: 8px; padding: 10px 12px; background: #f8fafc; }}
                    .card-title {{ font-size: 9px; font-weight: 800; color: #475569; text-transform: uppercase; }}
                    .card-val {{ font-size: 20px; font-weight: 900; color: #020b1e; margin: 3px 0; }}
                    .sec-title {{ font-size: 11px; font-weight: 800; color: #042454; text-transform: uppercase; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; margin: 10px 0 8px 0; }}
                    .chart-box {{ border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 10px 6px 10px; text-align: center; background: #ffffff; margin-bottom: 12px; }}
                    .alert-box {{ background: {bg_banner_9}; border: 1.5px solid {border_banner_9}; border-radius: 10px; padding: 12px 16px; display: grid; grid-template-columns: 1.15fr 1.25fr; gap: 14px; margin-bottom: 12px; }}
                    table {{ width: 100%; border-collapse: collapse; font-size: 8.5px; margin-bottom: 10px; }}
                    th {{ background: #042454; color: white; padding: 5px; text-transform: uppercase; font-weight: 700; }}
                    td {{ border-bottom: 1px solid #e2e8f0; padding: 4px 5px; text-align: center; font-weight: 600; }}
                    .footer {{ font-size: 8px; color: #64748b; background: #f1f5f9; padding: 8px 12px; border-radius: 6px; line-height: 1.35; }}
                </style>
            </head>
            <body>
                <div class="page">
                    <div class="header">
                        <div style="display:flex; align-items:center; gap:14px;">
                            {logo_img_tag}
                            <div>
                                <div style="font-size:15px; font-weight:900; letter-spacing:0.5px;">PERCET GEORISK™ | EXECUTIVE TECHNICAL REPORT</div>
                                <div style="font-size:10px; color:#38bdf8; font-weight:700; margin-top:2px;">
                                    {T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {nombre_rubro_activo}
                                </div>
                                <div style="font-size:9px; color:#cbd5e1; margin-top:2px;">
                                    📍 Lat: {lat_actual}, Lon: {lon_actual} &nbsp;|&nbsp; 🕒 {fecha_emision}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="sec-title">{T['pdf_sec1_title']}</div>
                    <div class="grid-3">
                        <div class="card">
                            <div class="card-title">{T['pill_peak']} ({fecha_pico})</div>
                            <div class="card-val" style="color:#dc2626;">{pico_max_dia:.1f} {UNIT_MM}</div>
                            <div style="font-size:9px; font-weight:700; color:#475569;">{T['kpi1_sub'].format(acum=lluvia_acumulada)}</div>
                        </div>
                        <div class="card">
                            <div class="card-title">{T['pill_thresh']} / {etiqueta_dif}</div>
                            <div class="card-val">{umbral_critico:.1f} {UNIT_MM} <span style="font-size:13px; color:{color_dif};">({signo_dif})</span></div>
                            <div style="font-size:9px; font-weight:700; color:#475569;">{T['pill_days']}: {dias_criticos} {T['day_unit']}</div>
                        </div>
                        <div class="card">
                            <div class="card-title">{T['kpi2_title']} & QUEBRADAS</div>
                            <div class="card-val">{humedad_media}% HR</div>
                            <div style="font-size:9px; font-weight:700; color:#020b1e;">{estado_quebrada}</div>
                        </div>
                    </div>

                    <div class="sec-title">{T['pdf_sec2_title']}</div>
                    <div class="chart-box">
                        <svg viewBox="0 0 740 220" width="100%" height="215">
                            <line x1="25" y1="188" x2="720" y2="188" stroke="#94a3b8" stroke-width="1.5"/>
                            ` + barrasSvg + `
                            <line x1="25" y1="` + yUmbral + `" x2="720" y2="` + yUmbral + `" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4"/>
                            <rect x="585" y="4" width="132" height="18" fill="#dc2626" rx="4"/>
                            <text x="651" y="16" font-size="9.5" font-weight="800" fill="#ffffff" text-anchor="middle">{T['thresh_tag'].format(umbral=f'{umbral_critico:.1f}')}</text>
                        </svg>
                    </div>

                    <div class="sec-title">{T['pdf_sec3_title']}</div>
                    <div class="alert-box">
                        <div>
                            <div style="font-size:11px; font-weight:900; color:{color_titulo_9}; margin-bottom:4px;">{badge_txt}</div>
                            <div style="font-size:10px; font-weight:800; margin-bottom:4px;">{nombre_rubro_activo}</div>
                            <div style="font-size:9px; color:#334155; line-height:1.4;">{desc_txt}</div>
                        </div>
                        <div>
                            <div style="font-size:9.5px; font-weight:800; color:#042454; margin-bottom:4px;">{T['rec_title']}:</div>
                            <div style="font-size:8.5px; line-height:1.4;">{checks_pdf_html}</div>
                        </div>
                    </div>

                    <div class="sec-title">{T['pdf_sec4_title']}</div>
                    <table>
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>{T['card_forecast']} ({UNIT_MM})</th>
                                <th>Prob. Lluvia (%)</th>
                                <th>Temp. Máx (°C)</th>
                                <th>Temp. Mín (°C)</th>
                                <th>Viento Máx (km/h)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"<tr><td>{r['Fecha']}</td><td><b>{r['Pronóstico']}</b></td><td>{r['Prob. Lluvia (%)']}%</td><td>{r['Temp. Máx (°C)']}°C</td><td>{r['Temp. Mín (°C)']}°C</td><td>{r['Viento Máx (km/h)']}</td></tr>" for _, r in df_diario.iloc[:8].iterrows()])}
                        </tbody>
                    </table>

                    <div class="footer">
                        {T['disclaimer']}
                    </div>
                </div>
                <script>
                    window.onload = function() {{ setTimeout(function() {{ window.print(); }}, 400); }};
                <\/script>
            </body>
            </html>
            `;
            win.document.open();
            win.document.write(contenido);
            win.document.close();
        }}
        abrirInfografiaPDF();
        </script>
        """
        components.html(html_infografia, height=0, width=0)

    # Botones de Exportación
    col_dl1, col_dl2 = st.columns(2)
    csv_data = df_diario.to_csv(index=False).encode('utf-8-sig')
    with col_dl1:
        st.download_button(
            label=T["dl_csv"],
            data=csv_data,
            file_name=f"PERCET_GeoRisk_{nombre_proyecto}_{lat_actual}_{lon_actual}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        if st.button(T["dl_pdf"], use_container_width=True):
            disparar_pdf_infografia_una_hoja()

    # 12. DESPLEGABLE TÉCNICO (CON ÍCONO LIMPIO SIN TEXTO SUPERPUESTO)
    with st.expander(T["exp_title"]):
        st.markdown(f"""
        * **Machine Learning Engine:** Gradient Boosting Regressor ($R^2 = 0.947$, $\\text{{RMSE}} = 0.599\\text{{ mm/day}}$, $\\text{{MAE}} = 0.394\\text{{ mm/day}}$).
        * **Linear Fit Equation:** $y = 0.871x + 0.163$ | **Surface Pressure:** `{presion_media} hPa`
        """)
        st.dataframe(df_diario, use_container_width=True, hide_index=True)

    # 13. DISCLAIMER Y BANNER B2B DE CIERRE
    st.markdown(f'<div class="legal-disclaimer">{T["disclaimer"]}</div>', unsafe_allow_html=True)

    mensaje_wa = (
        f"Hola PERCET, estoy evaluando el proyecto '{nombre_proyecto}' en la coordenada [{lat_actual}, {lon_actual}] "
        f"({nombre_rubro_activo}) con PERCET GeoRisk y solicito asesoría técnica."
    )
    url_whatsapp = f"https://wa.me/51999999999?text={urllib.parse.quote(mensaje_wa)}"

    st.markdown(f"""
    <div class="b2b-banner">
        <h3 style="color:#ffffff; font-weight:900; letter-spacing:0.5px; margin-bottom:10px;">{T['b2b_title']}</h3>
        <p style="color:#e0f2fe; font-size:1.02rem; max-width:920px; margin:0 auto; line-height:1.55;">{T['b2b_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns([0.8, 1.6, 1.6, 0.8])
    with b2:
        if st.button(T["btn_quote"]):
            mostrar_modal_cotizacion()
    with b3:
        st.link_button(T["btn_wa"], url_whatsapp, use_container_width=True)

except Exception as e:
    st.error(f"Error connecting to satellite server: {e}")