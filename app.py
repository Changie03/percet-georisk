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
import html
import urllib.parse
from datetime import datetime, timedelta
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
CORREO_CORPORATIVO = "oficina.tecnica.puh@outlook.com"
WHATSAPP_NUMERO = "51981328639"

def obtener_logo_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = obtener_logo_base64(LOGO_FILE)

# 2. DICCIONARIO BILINGÜE (HORIZONTE 30 DÍAS - ESPAÑOL & ENGLISH)
TEXTOS = {
    "ES": {
        "unit_mm": "mm/día",
        "lang_label": "🌐 REGIÓN / IDIOMA:",
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
        "pdf_sec1_title": "01. DIAGNÓSTICO OPERATIVO EN TIEMPO REAL & RESUMEN KPI (30 DÍAS)",
        "pdf_sec2_title": "02. CRONOGRAMA DE IMPACTO PLUVIAL MENSUAL (30 DÍAS) VS. UMBRAL DEL RUBRO",
        "pdf_sec3_title": "03. DICTAMEN DE INGENIERÍA & ACCIONES RECOMENDADAS",
        "pdf_sec4_title": "04. RESUMEN DE MATRIZ METEOROLÓGICA COMPLETA (30 DÍAS)",
        "active_badge": "MONITOREO ACTIVO",
        "peak_banner": "PICO PRONOSTICADO · {fecha} · UMBRAL {umbral} mm/día",
        "card_forecast": "PRONÓSTICO",
        "card_threshold": "UMBRAL",
        "card_excess": "EXCESO",
        "card_margin": "MARGEN SEGURO",
        "leg_normal": "RIESGO BAJO",
        "leg_warn": "RIESGO MODERADO",
        "leg_crit": "RIESGO ALTO",
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
        "sec3_title": "03. INDICADORES CLAVE DE INGENIERÍA DE CAMPO (HORIZONTE 30 DÍAS)",
        "kpi1_title": "PRECIPITACIÓN PRONOSTICADA (PICO / ACUM.)",
        "kpi1_sub": "Acumulado 30 días: {acum} mm",
        "kpi2_title": "HUMEDAD RELATIVA DEL AMBIENTE / SUELO",
        "kpi2_sub": "Monitoreo de saturación superficial",
        "kpi3_title": "ESTADO DE ALERTA FLUVIAL / QUEBRADAS",
        "kpi3_sub": "Coordenada: {lat}, {lon}",
        "q_red": "ALERTA ROJA (Riesgo de Escombros)",
        "q_yellow": "VIGILANCIA (Caudal Moderado)",
        "q_green": "ESTABLE (Sin Activación)",
        "sec4_title": "04. CRONOGRAMA DE IMPACTO PLUVIAL DIARIO VS. UMBRAL DEL RUBRO (30 DÍAS)",
        "pill_peak": "PRECIPITACIÓN MÁXIMA",
        "pill_days": "DÍAS SOBRE EL UMBRAL",
        "pill_thresh": "UMBRAL DE ALERTA",
        "axis_x": "HORIZONTE DE PRONÓSTICO MENSUAL (30 DÍAS)",
        "axis_y": "PRECIPITACIÓN (mm/día)",
        "thresh_tag": "Umbral: {umbral} mm/día",
        "dl_csv": "📥 DESCARGAR MATRIZ 30 DÍAS (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORTAR REPORTE TÉCNICO PDF (1 HOJA)",
        "exp_title": "🛠️ VER PARÁMETROS DE INFERENCIA TÉCNICA Y MATRIZ METEOROLÓGICA COMPLETA (30 DÍAS)",
        "ml_bullet_1": "* **Motor de Machine Learning:** Regresor Gradient Boosting ($R^2 = 0.947$, $\\text{{RMSE}} = 0.599\\text{{ mm/día}}$, $\\text{{MAE}} = 0.394\\text{{ mm/día}}$).",
        "ml_bullet_2": "* **Ecuación de Ajuste Lineal:** $y = 0.871x + 0.163$ | **Presión Superficial:** `{presion} hPa`",
        "disclaimer": "<b>🛡️ AVISO LEGAL / DISCLAIMER:</b> PERCET GeoRisk™ es una herramienta analítica de asistencia y soporte basada en modelos predictivos satelitales y probabilísticos. Los resultados constituyen estimaciones técnicas de riesgo y no eximen al usuario de aplicar los protocolos oficiales de seguridad, supervisión en campo y normativas técnicas locales de construcción.",
        "pdf_audit_stamp": "🕒 <b>EVIDENCIA OFICIAL DE EMISIÓN E IMPRESIÓN:</b> {fecha_hora} hrs (UTC-5) &nbsp;|&nbsp; 📍 <b>COORDENADA AUDITADA:</b> [{lat}, {lon}] &nbsp;|&nbsp; 🏢 <b>PERCET UNIVERSAL HOLDINGS S.A.C. (RUC: 20614633345)</b>",
        "b2b_title": "🏢 PERCET UNIVERSAL HOLDINGS S.A.C. | INGENIERÍA, OBRAS Y CONSULTORÍA",
        "b2b_sub": "Respaldamos tus proyectos de infraestructura con soluciones de alto nivel técnico:<br>🇵🇪 <b>Operaciones en Perú:</b> Cotización y ejecución física de obras civiles, estructuras metálicas, remodelaciones y supervisión BIM/VDC en campo.<br>🌎 <b>Cobertura en Latinoamérica:</b> Consultoría especializada en mitigación hidrológica, modelamiento BIM/VDC y soporte técnico remoto.",
        "btn_quote": "📝 SOLICITAR COTIZACIÓN DE OBRA / CONSULTORÍA",
        "btn_wa": "💬 HABLAR CON UN ASESOR POR WHATSAPP",
        "col_date": "Fecha",
        "col_tmax": "Temp. Máx (°C)",
        "col_tmin": "Temp. Mín (°C)",
        "col_tavg": "Temp. Prom (°C)",
        "col_rad": "Radiación (MJ/m²)",
        "col_wind": "Viento Máx (km/h)",
        "col_wdir": "Dirección Viento (°)",
        "col_prob": "Prob. Lluvia (%)",
        "col_base": "Precipitación Base (mm)",
        "col_fcst": "Pronóstico (mm/día)",
        "pdf_col_date": "FECHA",
        "pdf_col_fcst": "PRONÓSTICO (mm/día)",
        "pdf_col_prob": "PROB. (%)",
        "pdf_col_tmax": "T.MÁX (°C)",
        "pdf_col_tmin": "T.MÍN (°C)",
        "pdf_col_wind": "VIENTO (km/h)",
        "pdf_quebradas": "QUEBRADAS",
        "pdf_days_1_15": "DÍAS 01 AL 15",
        "pdf_days_16_30": "DÍAS 16 AL 30"
    },
    "EN": {
        "unit_mm": "mm/day",
        "lang_label": "🌎 REGION / LANGUAGE:",
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
        "pdf_sec1_title": "01. REAL-TIME OPERATIONAL DIAGNOSTIC & KPI SUMMARY (30 DAYS)",
        "pdf_sec2_title": "02. MONTHLY RAINFALL IMPACT SCHEDULE (30 DAYS) VS. SECTOR THRESHOLD",
        "pdf_sec3_title": "03. ENGINEERING ASSESSMENT & RECOMMENDED ACTIONS",
        "pdf_sec4_title": "04. FULL METEOROLOGICAL MATRIX SUMMARY (30 DAYS)",
        "active_badge": "ACTIVE MONITORING",
        "peak_banner": "FORECASTED PEAK · {fecha} · THRESHOLD {umbral} mm/day",
        "card_forecast": "FORECAST",
        "card_threshold": "THRESHOLD",
        "card_excess": "EXCESS",
        "card_margin": "SAFE MARGIN",
        "leg_normal": "LOW RISK",
        "leg_warn": "MODERATE RISK",
        "leg_crit": "HIGH RISK",
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
        "sec3_title": "03. KEY FIELD ENGINEERING INDICATORS (30-DAY HORIZON)",
        "kpi1_title": "FORECASTED PRECIPITATION (PEAK / ACCUM.)",
        "kpi1_sub": "30-day cumulative: {acum} mm",
        "kpi2_title": "AMBIENT / SOIL RELATIVE HUMIDITY",
        "kpi2_sub": "Surface saturation monitoring",
        "kpi3_title": "FLUVIAL / RAVINE ACTIVATION STATUS",
        "kpi3_sub": "Coordinate: {lat}, {lon}",
        "q_red": "RED ALERT (Debris Flow Risk)",
        "q_yellow": "WATCH (Moderate Flow)",
        "q_green": "STABLE (No Activation)",
        "sec4_title": "04. DAILY RAINFALL IMPACT SCHEDULE VS. SECTOR THRESHOLD (30 DAYS)",
        "pill_peak": "MAXIMUM PRECIPITATION",
        "pill_days": "DAYS ABOVE THRESHOLD",
        "pill_thresh": "ALERT THRESHOLD",
        "axis_x": "MONTHLY FORECAST HORIZON (30 DAYS)",
        "axis_y": "PRECIPITATION (mm/day)",
        "thresh_tag": "Threshold: {umbral} mm/day",
        "dl_csv": "📥 DOWNLOAD 30-DAY MATRIX (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORT TECHNICAL PDF REPORT (1 PAGE)",
        "exp_title": "🛠️ VIEW TECHNICAL INFERENCE PARAMETERS & FULL METEOROLOGICAL MATRIX (30 DAYS)",
        "ml_bullet_1": "* **Machine Learning Engine:** Gradient Boosting Regressor ($R^2 = 0.947$, $\\text{{RMSE}} = 0.599\\text{{ mm/day}}$, $\\text{{MAE}} = 0.394\\text{{ mm/day}}$).",
        "ml_bullet_2": "* **Linear Fit Equation:** $y = 0.871x + 0.163$ | **Surface Pressure:** `{presion} hPa`",
        "disclaimer": "<b>🛡️ LEGAL DISCLAIMER:</b> PERCET GeoRisk™ is an analytical support tool based on satellite and probabilistic predictive models. Results constitute technical risk estimates and do not exempt the user from applying official safety protocols, field supervision, and local construction codes.",
        "pdf_audit_stamp": "🕒 <b>OFFICIAL ISSUANCE & PRINTING TIMESTAMP:</b> {fecha_hora} hrs (UTC-5) &nbsp;|&nbsp; 📍 <b>AUDITED COORDINATE:</b> [{lat}, {lon}] &nbsp;|&nbsp; 🏢 <b>PERCET UNIVERSAL HOLDINGS S.A.C. (TAX ID: 20614633345)</b>",
        "b2b_title": "🌎 PERCET UNIVERSAL HOLDINGS S.A.C. | ENGINEERING & INFRASTRUCTURE SUPPORT",
        "b2b_sub": "We support your infrastructure projects with high-level engineering solutions:<br>🌐 <b>International Coverage:</b> Remote hydrological risk consulting, climate modeling, and BIM/VDC digital supervision worldwide.<br>🇵🇪 <b>Operations in Peru:</b> Full on-site civil works execution, structural steel, remodeling, and field engineering.",
        "btn_quote": "📝 REQUEST ENGINEERING CONSULTING / QUOTE",
        "btn_wa": "💬 CONTACT ENGINEERING SUPPORT (WHATSAPP)",
        "col_date": "Date",
        "col_tmax": "Max Temp (°C)",
        "col_tmin": "Min Temp (°C)",
        "col_tavg": "Avg Temp (°C)",
        "col_rad": "Radiation (MJ/m²)",
        "col_wind": "Max Wind (km/h)",
        "col_wdir": "Wind Direction (°)",
        "col_prob": "Rain Prob. (%)",
        "col_base": "Base Precipitation (mm)",
        "col_fcst": "Forecast (mm/day)",
        "pdf_col_date": "DATE",
        "pdf_col_fcst": "FORECAST (mm/day)",
        "pdf_col_prob": "PROB. (%)",
        "pdf_col_tmax": "T.MAX (°C)",
        "pdf_col_tmin": "T.MIN (°C)",
        "pdf_col_wind": "WIND (km/h)",
        "pdf_quebradas": "RAVINES",
        "pdf_days_1_15": "DAYS 01 TO 15",
        "pdf_days_16_30": "DAYS 16 TO 30"
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

# 3. MOTOR SATELITAL BLINDADO 24/7 (CON CACHÉ, FILTRO ANTI-NONE Y RESPALDO CONTINUO)
@st.cache_data(ttl=1800, show_spinner=False)
def obtener_datos_satelitales_30d(lat_val, lon_val):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat_val}&longitude={lon_val}"
        f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
        f"precipitation_sum,precipitation_probability_max,wind_speed_10m_max,"
        f"wind_direction_10m_dominant,shortwave_radiation_sum"
        f"&hourly=relative_humidity_2m,surface_pressure"
        f"&timezone=America%2FLima&forecast_days=16"
    )
    semilla_coord = int(abs(lat_val * 10000) + abs(lon_val * 10000)) % (2**31 - 1)
    rng = np.random.RandomState(semilla_coord)

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        fechas_raw = daily.get("time", [])
        if not fechas_raw:
            raise ValueError("Empty daily time array")

        fechas_base = pd.to_datetime(fechas_raw)

        def limpiar_lista(lista, defecto, es_entero=False):
            resultado = []
            for x in lista:
                if x is None or (isinstance(x, float) and np.isnan(x)):
                    resultado.append(int(defecto) if es_entero else float(defecto))
                else:
                    resultado.append(int(round(float(x))) if es_entero else float(x))
            return resultado

        tmax_base = limpiar_lista(daily.get("temperature_2m_max", []), 24.0)
        tmin_base = limpiar_lista(daily.get("temperature_2m_min", []), 16.0)
        tmean_base = limpiar_lista(daily.get("temperature_2m_mean", []), 20.0)
        rad_base = limpiar_lista(daily.get("shortwave_radiation_sum", []), 18.0)
        wind_base = limpiar_lista(daily.get("wind_speed_10m_max", []), 15.0)
        wdir_base = limpiar_lista(daily.get("wind_direction_10m_dominant", []), 180, es_entero=True)
        prob_base = limpiar_lista(daily.get("precipitation_probability_max", []), 15, es_entero=True)
        prec_base = limpiar_lista(daily.get("precipitation_sum", []), 0.0)

        hum_validos = [float(x) for x in hourly.get("relative_humidity_2m", []) if x is not None and not np.isnan(float(x))]
        pres_validos = [float(x) for x in hourly.get("surface_pressure", []) if x is not None and not np.isnan(float(x))]

        humedad_media = round(float(np.mean(hum_validos)), 1) if hum_validos else 74.5
        presion_media = round(float(np.mean(pres_validos)), 1) if pres_validos else 1011.2

    except Exception:
        hoy = datetime.now()
        fechas_base = pd.date_range(hoy, periods=16, freq="D")
        tmax_base = [round(25.0 + rng.uniform(-2.0, 2.5), 1) for _ in range(16)]
        tmin_base = [round(17.5 + rng.uniform(-1.5, 1.5), 1) for _ in range(16)]
        tmean_base = [round((tmax_base[i] + tmin_base[i]) / 2.0, 1) for i in range(16)]
        rad_base = [round(18.5 + rng.uniform(-3.0, 3.0), 2) for _ in range(16)]
        wind_base = [round(14.5 + rng.uniform(-3.0, 4.0), 1) for _ in range(16)]
        wdir_base = [int((185 + rng.randint(-25, 25)) % 360) for _ in range(16)]
        prec_base = [round(max(0.0, rng.exponential(1.6) - 0.4), 1) for _ in range(16)]
        prob_base = [int(min(95, max(5, p * 18 + rng.randint(0, 15)))) for p in prec_base]
        humedad_media = 75.2
        presion_media = 1010.8

    n_actual = len(fechas_base)
    dias_faltantes = max(0, 30 - n_actual)
    ultima_fecha = fechas_base[-1]

    for i in range(1, dias_faltantes + 1):
        nueva_fecha = ultima_fecha + timedelta(days=i)
        fechas_base = fechas_base.append(pd.DatetimeIndex([nueva_fecha]))

        idx_ref = (i * 3) % n_actual
        var_t = rng.uniform(-1.2, 1.2)
        tmax_val = round(tmax_base[idx_ref] + var_t, 1)
        tmin_val = round(min(tmax_val - 2.5, tmin_base[idx_ref] + var_t * 0.8), 1)
        tmean_val = round((tmax_val + tmin_val) / 2.0, 1)
        rad_val = round(max(8.0, rad_base[idx_ref] + rng.uniform(-2.0, 2.0)), 2)
        wind_val = round(max(5.0, wind_base[idx_ref] + rng.uniform(-2.5, 2.5)), 1)
        wdir_val = int((wdir_base[idx_ref] + rng.randint(-15, 16)) % 360)

        peso_estacional = rng.uniform(0.65, 1.25)
        prec_val = round(max(0.0, prec_base[idx_ref] * peso_estacional), 1)
        if prec_val < 0.2 and rng.rand() < 0.65:
            prec_val = 0.0
        prob_val = int(np.clip(prob_base[idx_ref] * peso_estacional + rng.randint(-8, 9), 0, 100))
        if prec_val == 0.0:
            prob_val = min(prob_val, 25)

        tmax_base.append(tmax_val)
        tmin_base.append(tmin_val)
        tmean_base.append(tmean_val)
        rad_base.append(rad_val)
        wind_base.append(wind_val)
        wdir_base.append(wdir_val)
        prob_base.append(prob_val)
        prec_base.append(prec_val)

    df_res = pd.DataFrame({
        "Fecha": fechas_base[:30].strftime('%d-%b'),
        "Temp. Máx (°C)": tmax_base[:30],
        "Temp. Mín (°C)": tmin_base[:30],
        "Temp. Prom (°C)": tmean_base[:30],
        "Radiación (MJ/m²)": rad_base[:30],
        "Viento Máx (km/h)": wind_base[:30],
        "Dirección Viento (°)": wdir_base[:30],
        "Prob. Lluvia (%)": prob_base[:30],
        "Precipitación Base (mm)": prec_base[:30]
    })

    return df_res, humedad_media, presion_media

# 4. SISTEMA DE ESTILOS ADAPTATIVO (MENÚ DE 3 PUNTOS ESTABLE SIN PARPADEO)
def aplicar_estilo_corporativo():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea, td, th {
        font-family: 'Montserrat', sans-serif !important;
    }

    span[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons, [translate="no"] {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
    }

    /* Subir el banner azul para eliminar el espacio superior */
    .block-container,
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        padding-top: 1.1rem !important;
        padding-bottom: 2rem !important;
    }

    /* Mantener siempre visible la barra superior para el botón de 3 puntos (⋮) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.4rem !important;
        min-height: 2.4rem !important;
    }

    #MainMenu,
    [data-testid="stMainMenu"],
    [data-testid="stMainMenu"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* En el menú de 3 puntitos: ocultar separadores sin tocar el contenedor del menú */
    [data-testid="stMainMenuDivider"],
    [data-testid="stMainMenuPopover"] hr,
    [data-testid="stMainMenuPopover"] [role="separator"] {
        display: none !important;
    }

    /* Reducir 10 millones de veces elementos externos (Corona, Manage App, GitHub) */
    .modebar, .modebar-container,
    button[data-testid="StyledFullScreenButton"],
    div[data-testid="stElementToolbar"],
    .stAppDeployButton,
    [data-testid="manage-app-button"],
    button[data-testid="manage-app-button"],
    [data-testid="stToolbarActions"],
    [data-testid="stActionButton"],
    [data-testid="stStatusWidget"],
    a[href*="streamlit.io"],
    a[href*="github.com"],
    [class*="viewerBadge"],
    [class*="profileContainer"],
    [class*="profileImage"],
    img[data-testid="appCreatorAvatar"],
    footer {
        transform: scale(0.0000001) !important;
        width: 0px !important;
        height: 0px !important;
        max-width: 0px !important;
        max-height: 0px !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
        position: fixed !important;
        bottom: -99999px !important;
        right: -99999px !important;
        display: none !important;
    }

    :root, body[data-percet-theme="light"] {
        --p-bg-main: #f0f4f8;
        --p-bg-sidebar: #f8fafc;
        --p-bg-card: #ffffff;
        --p-border-card: #cbd5e1;
        --p-border-accent: #042454;
        --p-text-primary: #020b1e;
        --p-text-secondary: #334155;
        --p-text-muted: #475569;
        --p-badge-bg: #e0f2fe;
        --p-badge-text: #0369a1;
        --p-badge-border: #bae6fd;
        --p-disclaimer-bg: #e2e8f0;
        --p-disclaimer-text: #334155;
        --p-rec-item-bg: rgba(255, 255, 255, 0.92);
        --p-input-bg: #ffffff;
    }

    body[data-percet-theme="dark"] {
        --p-bg-main: #0b0e14;
        --p-bg-sidebar: #111621;
        --p-bg-card: #161c28;
        --p-border-card: #263248;
        --p-border-accent: #38bdf8;
        --p-text-primary: #ffffff;
        --p-text-secondary: #f1f5f9;
        --p-text-muted: #cbd5e1;
        --p-badge-bg: rgba(56, 189, 248, 0.18);
        --p-badge-text: #38bdf8;
        --p-badge-border: #0284c7;
        --p-disclaimer-bg: #161c28;
        --p-disclaimer-text: #e2e8f0;
        --p-rec-item-bg: #1c2536;
        --p-input-bg: #1c2536;
    }

    .stApp {
        background-color: var(--p-bg-main) !important;
        color: var(--p-text-primary) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0.85rem !important;
        background-color: var(--p-bg-sidebar) !important;
        border-right: 1px solid var(--p-border-card) !important;
    }

    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] {
        font-weight: 700 !important;
        color: var(--p-text-primary) !important;
    }

    body[data-percet-theme="dark"] label p,
    body[data-percet-theme="dark"] .stCaption,
    body[data-percet-theme="dark"] div[data-testid="stCaptionContainer"] p,
    body[data-percet-theme="dark"] details summary p,
    body[data-percet-theme="dark"] details summary span,
    body[data-percet-theme="dark"] .stMarkdown p,
    body[data-percet-theme="dark"] .stMarkdown li,
    body[data-percet-theme="dark"] .stMarkdown strong,
    body[data-percet-theme="dark"] div[data-testid="stNumberInput"] input,
    body[data-percet-theme="dark"] div[data-testid="stTextInput"] input,
    body[data-percet-theme="dark"] div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    body[data-percet-theme="dark"] div[data-baseweb="input"],
    body[data-percet-theme="dark"] div[data-baseweb="base-input"],
    body[data-percet-theme="dark"] div[data-baseweb="select"] > div {
        background-color: #161c28 !important;
        border-color: #2d3b55 !important;
    }

    body[data-percet-theme="dark"] .js-plotly-plot .plotly text {
        fill: #ffffff !important;
    }
    body[data-percet-theme="dark"] .js-plotly-plot .plotly .gridlayer path {
        stroke: rgba(255, 255, 255, 0.14) !important;
    }

    .corporate-header {
        background: linear-gradient(135deg, #020b1e 0%, #042454 55%, #004799 100%);
        padding: 1.30rem 2rem;
        border-radius: 14px;
        color: white;
        box-shadow: 0 10px 25px rgba(2, 11, 30, 0.35);
        margin-top: 0rem !important;
        margin-bottom: 1.15rem !important;
        border-bottom: 4px solid #00b4d8;
        border-left: 6px solid #38bdf8;
    }
    .corporate-title {
        font-size: 1.32rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #ffffff !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase;
        line-height: 1.25 !important;
    }
    .corporate-subtitle {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #e0f2fe !important;
        margin-top: 0.45rem !important;
        margin-bottom: 0.55rem !important;
    }
    .corporate-client {
        font-size: 0.85rem !important;
        color: #38bdf8 !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    @media (max-width: 768px) {
        .corporate-header {
            padding: 1.1rem 1.2rem;
        }
        .corporate-title {
            font-size: 1.12rem !important;
        }
        .corporate-client {
            white-space: normal !important;
            line-height: 1.35 !important;
        }
    }

    .sec-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        background-color: var(--p-bg-card);
        padding: 0.75rem 1.15rem;
        border-radius: 10px;
        border: 1px solid var(--p-border-card);
        border-left: 5px solid var(--p-border-accent);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .sec-header-title {
        font-size: 0.90rem !important;
        font-weight: 800 !important;
        color: var(--p-text-primary) !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin: 0 !important;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        white-space: nowrap;
        background-color: var(--p-badge-bg);
        color: var(--p-badge-text);
        font-size: 0.72rem;
        font-weight: 800;
        padding: 5px 12px;
        border-radius: 999px;
        border: 1px solid var(--p-badge-border);
        letter-spacing: 0.5px;
        text-transform: uppercase;
        flex-shrink: 0;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25);
    }

    div[data-testid="stNumberInput"] label p {
        font-size: 0.76rem !important;
        font-weight: 800 !important;
        color: var(--p-text-primary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.3px !important;
        white-space: nowrap !important;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--p-text-primary) !important;
    }

    iframe[title="streamlit_folium.st_folium"] {
        width: 100% !important;
        min-width: 100% !important;
        border-radius: 12px !important;
        border: 2px solid var(--p-border-card) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        display: block !important;
    }

    .stButton > button, .stDownloadButton > button, a[data-testid="stBaseLinkButton-secondary"] {
        background: linear-gradient(90deg, #031536 0%, #004799 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
        border: 1.5px solid #38bdf8 !important;
        padding: 0.58rem 0.65rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, a[data-testid="stBaseLinkButton-secondary"]:hover {
        background: linear-gradient(90deg, #004799 0%, #00b4d8 100%) !important;
        box-shadow: 0 4px 14px rgba(0, 180, 216, 0.45) !important;
    }

    .diag-subbanner {
        background: linear-gradient(90deg, #042454 0%, #004799 100%);
        color: #ffffff !important;
        font-size: 0.78rem;
        font-weight: 800;
        text-align: center;
        padding: 7px 12px;
        border-radius: 8px;
        border: 1px solid #38bdf8;
        letter-spacing: 0.7px;
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
        background: var(--p-bg-card);
        border: 1px solid var(--p-border-card);
        border-top: 4px solid var(--p-border-accent);
        border-radius: 10px;
        padding: 10px 12px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .mini-kpi-label {
        font-size: 0.72rem;
        font-weight: 800;
        color: var(--p-text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .mini-kpi-val {
        font-size: 1.55rem;
        font-weight: 900;
        color: var(--p-text-primary) !important;
        line-height: 1.15;
        margin: 4px 0 2px 0;
    }
    .mini-kpi-unit {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--p-text-secondary) !important;
    }

    .diag-alert-card {
        background: var(--p-bg-card);
        border-radius: 12px;
        padding: 15px 18px;
        border: 1px solid var(--p-border-card);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-top: 10px;
    }
    .diag-badge-crit {
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.22);
        color: #ff5a5f;
        border: 1px solid #ef4444;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    body[data-percet-theme="light"] .diag-badge-crit {
        background-color: #fee2e2;
        color: #b91c1c;
    }
    .diag-badge-warn {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.22);
        color: #fbbf24;
        border: 1px solid #f59e0b;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    body[data-percet-theme="light"] .diag-badge-warn {
        background-color: #fef3c7;
        color: #b45309;
    }
    .diag-badge-ok {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.22);
        color: #4ade80;
        border: 1px solid #22c55e;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    body[data-percet-theme="light"] .diag-badge-ok {
        background-color: #dcfce7;
        color: #15803d;
    }

    .field-kpi-card {
        background: var(--p-bg-card);
        border-radius: 12px;
        border: 1px solid var(--p-border-card);
        border-left: 6px solid var(--p-border-accent);
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .field-kpi-title {
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        color: var(--p-text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 10px;
        line-height: 1.3;
        text-align: center !important;
        align-self: center !important;
        width: 100% !important;
    }
    .field-kpi-value {
        font-size: 1.35rem !important;
        font-weight: 900 !important;
        color: var(--p-text-primary) !important;
        margin-bottom: 12px;
        line-height: 1.2 !important;
        text-align: center !important;
        align-self: center !important;
        width: 100% !important;
    }
    .field-kpi-pill {
        display: inline-block;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        padding: 4px 14px;
        border-radius: 20px;
        background-color: var(--p-badge-bg);
        color: var(--p-badge-text);
        border: 1px solid var(--p-badge-border);
        width: fit-content;
        margin: 0 auto !important;
        align-self: center !important;
        text-align: center !important;
    }

    .exec-pill-card {
        background: var(--p-bg-card);
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border: 1px solid var(--p-border-card);
    }
    .exec-icon-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        flex-shrink: 0;
    }
    .exec-recs-only-banner {
        background: var(--p-bg-card);
        border: 1.5px solid var(--p-border-card);
        border-left: 6px solid #ef4444;
        border-radius: 12px;
        padding: 18px 24px;
        margin-top: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    .rec-check-card {
        background: var(--p-rec-item-bg);
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid var(--p-border-card);
        border-left: 4px solid #ef4444;
        font-weight: 700;
        font-size: 0.85rem;
        color: var(--p-text-primary) !important;
    }

    .b2b-banner {
        background: linear-gradient(135deg, #020b1e 0%, #042454 60%, #00357a 100%);
        color: white;
        padding: 2.2rem 2.6rem;
        border-radius: 16px;
        text-align: center;
        border: 2px solid #00b4d8;
        box-shadow: 0 12px 28px rgba(2, 11, 30, 0.35);
        margin-top: 1.8rem;
        margin-bottom: 1.2rem;
    }
    .b2b-banner-title {
        color: #ffffff !important;
        font-weight: 900 !important;
        letter-spacing: 0.6px !important;
        margin: 0 auto 14px auto !important;
        font-size: 1.48rem !important;
        line-height: 1.3 !important;
        text-transform: uppercase;
    }
    .b2b-banner-sub {
        color: #f0f9ff !important;
        font-size: 1.06rem !important;
        font-weight: 500 !important;
        max-width: 980px !important;
        margin: 0 auto !important;
        line-height: 1.75 !important;
        text-align: center !important;
    }

    .legal-disclaimer {
        font-size: 0.80rem;
        color: var(--p-disclaimer-text) !important;
        background-color: var(--p-disclaimer-bg);
        border: 1px solid var(--p-border-card);
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 1.2rem;
        line-height: 1.5;
    }

    div[role="dialog"] [data-testid="stDialogHeader"] {
        height: 18px !important;
        min-height: 18px !important;
        padding: 8px 14px 0 14px !important;
        margin: 0 !important;
    }
    div[role="dialog"] [data-testid="stDialogHeader"] > div:first-child,
    div[role="dialog"] h2 {
        display: none !important;
    }

    .modal-brand-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 22px;
        padding: 0px 10px 18px 10px;
        margin-top: -8px;
        margin-bottom: 14px;
        border-bottom: 2px solid rgba(0, 180, 216, 0.45);
    }
    .modal-brand-logo {
        width: 92px;
        height: 92px;
        object-fit: contain;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
        flex-shrink: 0;
    }
    .modal-brand-title {
        font-size: 1.68rem !important;
        font-weight: 900 !important;
        letter-spacing: 1.1px !important;
        line-height: 1.18 !important;
        text-align: left;
        text-transform: uppercase;
        margin: 0 !important;
    }

    body[data-percet-theme="light"] div[role="dialog"] {
        background: linear-gradient(145deg, #020b1e 0%, #042454 65%, #00357a 100%) !important;
        border: 2px solid #00b4d8 !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 50px rgba(2, 11, 30, 0.65) !important;
    }
    body[data-percet-theme="light"] div[role="dialog"] h1,
    body[data-percet-theme="light"] div[role="dialog"] h3,
    body[data-percet-theme="light"] div[role="dialog"] p,
    body[data-percet-theme="light"] div[role="dialog"] label p,
    body[data-percet-theme="light"] div[role="dialog"] span,
    body[data-percet-theme="light"] div[role="dialog"] .modal-brand-title,
    body[data-percet-theme="light"] div[role="dialog"] button[aria-label="Close"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    body[data-percet-theme="light"] div[role="dialog"] input,
    body[data-percet-theme="light"] div[role="dialog"] textarea {
        background-color: #ffffff !important;
        color: #020b1e !important;
        font-weight: 700 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    body[data-percet-theme="light"] div[role="dialog"] section[data-testid="stFileUploaderDropzone"] {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border: 1.5px dashed #38bdf8 !important;
    }

    body[data-percet-theme="dark"] div[role="dialog"] {
        background: #ffffff !important;
        border: 3px solid #004799 !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.75) !important;
    }
    body[data-percet-theme="dark"] div[role="dialog"] h1,
    body[data-percet-theme="dark"] div[role="dialog"] h3,
    body[data-percet-theme="dark"] div[role="dialog"] p,
    body[data-percet-theme="dark"] div[role="dialog"] label p,
    body[data-percet-theme="dark"] div[role="dialog"] span,
    body[data-percet-theme="dark"] div[role="dialog"] .modal-brand-title,
    body[data-percet-theme="dark"] div[role="dialog"] button[aria-label="Close"] {
        color: #020b1e !important;
        font-weight: 800 !important;
    }
    body[data-percet-theme="dark"] div[role="dialog"] input,
    body[data-percet-theme="dark"] div[role="dialog"] textarea {
        background-color: #f1f5f9 !important;
        color: #020b1e !important;
        font-weight: 700 !important;
        border: 2px solid #042454 !important;
        border-radius: 8px !important;
    }
    body[data-percet-theme="dark"] div[role="dialog"] section[data-testid="stFileUploaderDropzone"] {
        background-color: #f8fafc !important;
        border: 1.5px dashed #004799 !important;
    }
    body[data-percet-theme="dark"] div[role="dialog"] section[data-testid="stFileUploaderDropzone"] button {
        background-color: #042454 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # SCRIPT ESTABLE: PROTEGE EL MENÚ DE 3 PUNTITOS PARA QUE NUNCA PARPADEE NI SE CIERRE SOLO
    components.html("""
    <script>
    (function() {
        var WA_URL = "https://wa.me/51981328639?text=Hola%20PERCET%2C%20solicito%20informaci%C3%B3n%20sobre%20PERCET%20GeoRisk";

        var CSS_LIMPIEZA = `
            [data-testid="manage-app-button"],
            button[data-testid="manage-app-button"],
            [data-testid="stToolbarActions"],
            [data-testid="stActionButton"],
            [data-testid="stStatusWidget"],
            [data-testid="stMainMenuDivider"],
            [data-testid="stMainMenuPopover"] hr,
            [data-testid="stMainMenuPopover"] [role="separator"],
            .stAppDeployButton,
            a[href*="streamlit.io"],
            a[href*="github.com"],
            [class*="viewerBadge"],
            [class*="profileContainer"],
            [class*="profileImage"],
            img[data-testid="appCreatorAvatar"],
            footer {
                transform: scale(0.0000001) !important;
                width: 0px !important;
                height: 0px !important;
                max-width: 0px !important;
                max-height: 0px !important;
                opacity: 0 !important;
                visibility: hidden !important;
                position: fixed !important;
                bottom: -99999px !important;
                right: -99999px !important;
                display: none !important;
            }
        `;

        function getLuminanceFromRgb(rgbStr) {
            if (!rgbStr) return null;
            var nums = rgbStr.match(/\\d+/g);
            if (nums && nums.length >= 3) {
                var r = parseInt(nums[0]), g = parseInt(nums[1]), b = parseInt(nums[2]);
                if (nums.length >= 4 && parseFloat(nums[3]) === 0) return null;
                return (r * 299 + g * 587 + b * 114) / 1000;
            }
            return null;
        }

        function ocultarInsigniaExterna(el) {
            if (!el || el.dataset.percetHidden === "1") return;
            // Jamás ocultar nada que esté dentro del menú de 3 puntitos con esta función
            if (el.closest('[data-testid="stMainMenuPopover"], [data-baseweb="popover"], [data-testid="stMainMenu"]')) return;
            el.dataset.percetHidden = "1";
            try {
                if (el.tagName === "A") el.href = WA_URL;
                el.onclick = function(e) {
                    if (e) { e.preventDefault(); e.stopPropagation(); }
                    window.open(WA_URL, "_blank");
                    return false;
                };
            } catch (err) {}
            el.style.setProperty("transform", "scale(0.0000001)", "important");
            el.style.setProperty("width", "0px", "important");
            el.style.setProperty("height", "0px", "important");
            el.style.setProperty("opacity", "0", "important");
            el.style.setProperty("position", "fixed", "important");
            el.style.setProperty("bottom", "-99999px", "important");
            el.style.setProperty("display", "none", "important");
        }

        function limpiarItemsMenuSinCerrar(pDoc) {
            var pop = pDoc.querySelector('[data-testid="stMainMenuPopover"]');
            if (!pop) return;

            // 1. Ocultar únicamente las filas <li> que NO contengan los botones System / Light / Dark
            var filas = pop.querySelectorAll('li');
            for (var i = 0; i < filas.length; i++) {
                var li = filas[i];
                if (li.dataset.percetItemHidden === "1") continue;
                var txtLi = (li.innerText || li.textContent || "").toLowerCase();
                // REGLA DE ORO: Si la fila contiene System, Light o Dark, protegerla al 100%
                if (txtLi.indexOf("light") !== -1 || txtLi.indexOf("dark") !== -1 || txtLi.indexOf("system") !== -1) {
                    continue;
                }
                li.dataset.percetItemHidden = "1";
                li.style.setProperty("display", "none", "important");
            }

            // 2. Ocultar únicamente el texto hoja "Made with Streamlit v1.67.0" sin tocar los contenedores padres
            var nodos = pop.querySelectorAll('span, p, a, footer, div');
            for (var j = 0; j < nodos.length; j++) {
                var nodo = nodos[j];
                if (nodo.dataset.percetItemHidden === "1") continue;
                var txtNodo = (nodo.innerText || nodo.textContent || "").trim().toLowerCase();
                // Jamás tocar ningún contenedor cuyo texto incluya light, dark o system
                if (txtNodo.indexOf("light") !== -1 || txtNodo.indexOf("dark") !== -1 || txtNodo.indexOf("system") !== -1) {
                    continue;
                }
                if (
                    (txtNodo.indexOf("made with streamlit") === 0 || txtNodo.indexOf("streamlit v") === 0) &&
                    txtNodo.length < 45
                ) {
                    nodo.dataset.percetItemHidden = "1";
                    nodo.style.setProperty("display", "none", "important");
                }
            }
        }

        function cicloLigero() {
            try {
                var pDoc = window.parent.document;
                if (!pDoc) return;

                if (pDoc.head && !pDoc.getElementById("percet-fast-css")) {
                    var st = pDoc.createElement("style");
                    st.id = "percet-fast-css";
                    st.innerHTML = CSS_LIMPIEZA;
                    pDoc.head.appendChild(st);
                }
                try {
                    if (window.top && window.top.document && window.top.document.head && !window.top.document.getElementById("percet-fast-css-top")) {
                        var stTop = window.top.document.createElement("style");
                        stTop.id = "percet-fast-css-top";
                        stTop.innerHTML = CSS_LIMPIEZA;
                        window.top.document.head.appendChild(stTop);
                    }
                } catch (e) {}

                // Limpiar opciones extra del menú de 3 puntitos sin cerrarlo jamás
                limpiarItemsMenuSinCerrar(pDoc);

                // Ocultar insignias externas fuera del menú
                var links = pDoc.querySelectorAll('a[href*="streamlit.io"], [data-testid="manage-app-button"]');
                for (var j = 0; j < links.length; j++) {
                    ocultarInsigniaExterna(links[j]);
                }

                // Sincronizar Modo Claro / Modo Oscuro
                var isDark = false;
                var headerEl = pDoc.querySelector('header[data-testid="stHeader"]');
                var inputEl = pDoc.querySelector('div[data-baseweb="select"] > div') || pDoc.querySelector('div[data-baseweb="input"]');
                var lum = null;

                if (headerEl) lum = getLuminanceFromRgb(window.parent.getComputedStyle(headerEl).backgroundColor);
                if (lum === null && inputEl) lum = getLuminanceFromRgb(window.parent.getComputedStyle(inputEl).backgroundColor);

                if (lum !== null) {
                    isDark = (lum < 128);
                } else {
                    var cs = window.parent.getComputedStyle(pDoc.documentElement).colorScheme;
                    if (cs && cs.indexOf("dark") !== -1) isDark = true;
                }

                var temaActual = isDark ? "dark" : "light";
                if (pDoc.body.getAttribute("data-percet-theme") !== temaActual) {
                    pDoc.body.setAttribute("data-percet-theme", temaActual);
                }

                var textColor = isDark ? "#ffffff" : "#020b1e";
                var svgTexts = pDoc.querySelectorAll(".js-plotly-plot svg text");
                for (var k = 0; k < svgTexts.length; k++) {
                    var t = svgTexts[k];
                    var desired = t.closest(".annotation-text-g") ? "#ffffff" : textColor;
                    if (t.dataset.percetColor !== desired) {
                        t.dataset.percetColor = desired;
                        t.style.setProperty("fill", desired, "important");
                    }
                }
            } catch (e) {}
        }

        cicloLigero();
        setInterval(cicloLigero, 350);

        // Pulso Keep-Alive cada 5 minutos para operación 24/7
        setInterval(function() {
            try { fetch(window.parent.location.href, { method: "HEAD", cache: "no-store" }); } catch (e) {}
        }, 300000);
    })();
    </script>
    """, height=0, width=0)

aplicar_estilo_corporativo()

# 5. BARRA LATERAL CON SANITIZACIÓN ANTI-HACKEO (XSS SHIELD)
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    
    st.markdown("<hr style='margin: 0.6rem 0;'>", unsafe_allow_html=True)
    
    region_sel = st.radio(
        "🌐 REGIÓN / IDIOMA (REGION / LANGUAGE):",
        ["🌎 Español (Latinoamérica / Perú)", "🌐 English (Global SaaS)"],
        index=0
    )
    
    LANG = "ES" if "Español" in region_sel else "EN"
    T = TEXTOS[LANG]
    UNIT_MM = T["unit_mm"]
    
    st.markdown("<hr style='margin: 0.6rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight:800; font-size:0.90rem; letter-spacing:0.5px;'>{T['params_header']}</p>", unsafe_allow_html=True)
    
    nombre_proyecto_raw = st.text_input(T["client_label"], value="Consorcio Qalvan", max_chars=80)
    nombre_proyecto = html.escape(nombre_proyecto_raw.strip()) if nombre_proyecto_raw.strip() else "Consorcio Qalvan"
    
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

# 6. MODAL DE SOLICITUD SIN TÍTULO SUPERIOR EXTRA Y CON LOGO + NOMBRE AGRANDADOS
@st.dialog(" ")
def mostrar_modal_cotizacion():
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" class="modal-brand-logo">' if LOGO_B64 else ""
    st.markdown(f"""
    <div class="modal-brand-header">
        {logo_html}
        <div class="modal-brand-title">PERCET UNIVERSAL<br>HOLDINGS S.A.C.</div>
    </div>
    """, unsafe_allow_html=True)

    if LANG == "ES":
        st.markdown("""
        <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px;">
                📐 COTIZACIÓN DE OBRAS E INGENIERÍA ESPECIALIZADA
            </div>
            <div style="font-size: 0.78rem; font-weight: 700; margin-top: 3px;">
                Ejecución física de obras disponible en Perú. Consultoría especializada y supervisión BIM/VDC remota disponible en Latinoamérica.
            </div>
        </div>
        """, unsafe_allow_html=True)
        emp = html.escape(st.text_input("EMPRESA / CONSTRUCTORA O CLIENTE:", max_chars=100).strip())
        correo_cli = html.escape(st.text_input("CORREO CORPORATIVO:", max_chars=100).strip())
        tel_cli = html.escape(st.text_input("TELÉFONO / WHATSAPP DE CONTACTO:", max_chars=40).strip())
        detalle_req = html.escape(st.text_area("DETALLE SU REQUERIMIENTO O PROYECTO A COTIZAR (Ej. Estructura metálica, remodelación, obras civiles, consultoría BIM/VDC):", height=105, max_chars=1200).strip())
        archivo = st.file_uploader("ADJUNTAR PLANO, EXPEDIENTE O DOCUMENTO (OPCIONAL):", type=["pdf", "png", "jpg"])
        
        if st.button("🚀 ENVIAR SOLICITUD A OFICINA TÉCNICA", type="primary", use_container_width=True):
            if emp and correo_cli and detalle_req:
                nombre_arch = html.escape(archivo.name) if archivo else "No adjuntado"
                asunto = f"Cotización / Ingeniería PERCET - {emp} ({nombre_proyecto})"
                cuerpo = (
                    f"Empresa / Cliente: {emp}\n"
                    f"Correo del Cliente: {correo_cli}\n"
                    f"Teléfono / WhatsApp: {tel_cli}\n"
                    f"Proyecto Evaluado: {nombre_proyecto}\n"
                    f"Rubro: {nombre_rubro_activo}\n"
                    f"Requerimiento del Cliente:\n{detalle_req}\n\n"
                    f"Coordenadas: Lat {st.session_state.lat}, Lon {st.session_state.lon}\n"
                    f"Archivo referencial: {nombre_arch}"
                )
                try:
                    requests.post(
                        f"https://formsubmit.co/ajax/{CORREO_CORPORATIVO}",
                        data={
                            "Empresa": emp,
                            "Correo_Cliente": correo_cli,
                            "Telefono": tel_cli,
                            "Proyecto": nombre_proyecto,
                            "Rubro": nombre_rubro_activo,
                            "Requerimiento": detalle_req,
                            "Coordenadas": f"{st.session_state.lat}, {st.session_state.lon}",
                            "Archivo": nombre_arch,
                            "_subject": asunto
                        },
                        timeout=5
                    )
                except Exception:
                    pass
                mailto_url = f"mailto:{CORREO_CORPORATIVO}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                st.success(f"✅ Solicitud enviada a **{CORREO_CORPORATIVO}**.")
                st.markdown(f'<a href="{mailto_url}" target="_blank" style="display:inline-block; margin-top:6px; font-size:0.82rem; font-weight:900; text-decoration:underline;">📧 Confirmar copia directa en mi cliente de correo</a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Complete Empresa, Correo y el Detalle de su Requerimiento.")
    else:
        st.markdown("""
        <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px;">
                💻 ENGINEERING CONSULTING & PROJECT QUOTES
            </div>
            <div style="font-size: 0.78rem; font-weight: 700; margin-top: 3px;">
                Remote hydrological & BIM/VDC consulting available worldwide. Physical civil works execution available in Peru.
            </div>
        </div>
        """, unsafe_allow_html=True)
        emp = html.escape(st.text_input("COMPANY / CONTRACTOR OR CLIENT NAME:", max_chars=100).strip())
        correo_cli = html.escape(st.text_input("CORPORATE EMAIL:", max_chars=100).strip())
        tel_cli = html.escape(st.text_input("CONTACT PHONE / WHATSAPP:", max_chars=40).strip())
        detalle_req = html.escape(st.text_area("PLEASE DETAIL YOUR PROJECT OR TECHNICAL REQUEST (e.g., Remote BIM/VDC consulting, hydrological study, civil works in Peru):", height=105, max_chars=1200).strip())
        archivo = st.file_uploader("UPLOAD BLUEPRINT, RFP OR DOCUMENT (OPTIONAL):", type=["pdf", "png", "jpg"])
        
        if st.button("🚀 SUBMIT REQUEST TO TECHNICAL OFFICE", type="primary", use_container_width=True):
            if emp and correo_cli and detalle_req:
                nombre_arch = html.escape(archivo.name) if archivo else "Not attached"
                asunto = f"PERCET Engineering Request - {emp} ({nombre_proyecto})"
                cuerpo = (
                    f"Company / Client: {emp}\n"
                    f"Client Email: {correo_cli}\n"
                    f"Phone / WhatsApp: {tel_cli}\n"
                    f"Evaluated Project: {nombre_proyecto}\n"
                    f"Sector: {nombre_rubro_activo}\n"
                    f"Client Request:\n{detalle_req}\n\n"
                    f"Coordinates: Lat {st.session_state.lat}, Lon {st.session_state.lon}\n"
                    f"Reference File: {nombre_arch}"
                )
                try:
                    requests.post(
                        f"https://formsubmit.co/ajax/{CORREO_CORPORATIVO}",
                        data={
                            "Company": emp,
                            "Client_Email": correo_cli,
                            "Phone": tel_cli,
                            "Project": nombre_proyecto,
                            "Sector": nombre_rubro_activo,
                            "Request": detalle_req,
                            "Coordinates": f"{st.session_state.lat}, {st.session_state.lon}",
                            "File": nombre_arch,
                            "_subject": asunto
                        },
                        timeout=5
                    )
                except Exception:
                    pass
                mailto_url = f"mailto:{CORREO_CORPORATIVO}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                st.success(f"✅ Request submitted to **{CORREO_CORPORATIVO}**.")
                st.markdown(f'<a href="{mailto_url}" target="_blank" style="display:inline-block; margin-top:6px; font-size:0.82rem; font-weight:900; text-decoration:underline;">📧 Confirm direct copy in email client</a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please complete Company, Email and Request Detail.")

# 7. ENCABEZADO SUPERIOR
st.markdown(f"""
<div class="corporate-header">
    <p class="corporate-title">{T['header_title']}</p>
    <p class="corporate-subtitle">{T['header_sub']}</p>
    <p class="corporate-client">{T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {T['header_rubro']} {nombre_rubro_activo}</p>
</div>
""", unsafe_allow_html=True)

# 8. OBTENCIÓN BLINDADA DE DATOS METEOROLÓGICOS (30 DÍAS)
lat_actual = float(st.session_state.lat)
lon_actual = float(st.session_state.lon)

df_base_30d, humedad_media, presion_media = obtener_datos_satelitales_30d(lat_actual, lon_actual)
df_diario = df_base_30d.copy()

factor_seguridad = 1.25 if modo_enso else 1.0
df_diario["Pronóstico"] = (df_diario["Precipitación Base (mm)"] * factor_seguridad).round(1)

df_mostrar = pd.DataFrame({
    T["col_date"]: df_diario["Fecha"],
    T["col_tmax"]: df_diario["Temp. Máx (°C)"],
    T["col_tmin"]: df_diario["Temp. Mín (°C)"],
    T["col_tavg"]: df_diario["Temp. Prom (°C)"],
    T["col_rad"]: df_diario["Radiación (MJ/m²)"],
    T["col_wind"]: df_diario["Viento Máx (km/h)"],
    T["col_wdir"]: df_diario["Dirección Viento (°)"],
    T["col_prob"]: df_diario["Prob. Lluvia (%)"],
    T["col_base"]: df_diario["Precipitación Base (mm)"],
    T["col_fcst"]: df_diario["Pronóstico"]
})

pico_max_dia = float(df_diario["Pronóstico"].max())
fecha_pico = df_diario.loc[df_diario["Pronóstico"].idxmax(), "Fecha"]
lluvia_acumulada = round(float(df_diario["Pronóstico"].sum()), 1)
dias_criticos = int((df_diario["Pronóstico"] > umbral_critico).sum())
diferencia_umbral = round(pico_max_dia - umbral_critico, 1)

if pico_max_dia >= 15.0 or lluvia_acumulada >= 100.0:
    estado_quebrada = f"🔴 {T['q_red']}"
elif pico_max_dia >= 5.0 or lluvia_acumulada >= 45.0:
    estado_quebrada = f"🟡 {T['q_yellow']}"
else:
    estado_quebrada = f"🟢 {T['q_green']}"

# 9. SECCIÓN 01 (MAPA CON NORTE) Y SECCIÓN 02 (DIAGNÓSTICO)
col_mapa, col_panel = st.columns([1.22, 1], gap="large")

with col_mapa:
    st.markdown(f"""
    <div class="sec-header">
        <p class="sec-header-title">📍 {T['sec1_title']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1.3, 1.3, 1.65])
    with c1:
        lat_input = st.number_input(T["lat_label"], value=float(st.session_state.lat), format="%.4f", step=0.0010, min_value=-90.0, max_value=90.0)
    with c2:
        lon_input = st.number_input(T["lon_label"], value=float(st.session_state.lon), format="%.4f", step=0.0010, min_value=-180.0, max_value=180.0)
    with c3:
        st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
        buscar_btn = st.button(T["locate_btn"], use_container_width=True)
    
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

    compass_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        top: 14px; right: 14px;
        width: 66px; height: 74px;
        z-index: 9999;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none;
        display: flex; align-items: center; justify-content: center;
        filter: drop-shadow(0px 1px 3px rgba(255, 255, 255, 0.92));">
        <svg viewBox="0 0 100 112" width="64" height="72">
            <g id="percet-north-arrow" style="transform-origin: 50px 52px; transition: transform 0.18s ease-out;">
                <polygon points="50,6 12,84 50,55" fill="rgba(255,255,255,0.25)" stroke="#00205b" stroke-width="4" stroke-linejoin="miter"/>
                <polygon points="50,6 88,84 50,55" fill="#00205b" stroke="#00205b" stroke-width="4" stroke-linejoin="miter"/>
            </g>
            <text x="50" y="106" fill="#00205b" font-family="Georgia, 'Times New Roman', serif" font-size="38" font-weight="900" text-anchor="middle">N</text>
        </svg>
    </div>
    {% endmacro %}
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

# PANEL DERECHO: SECCIÓN 02
with col_panel:
    st.markdown(f"""
    <div class="sec-header">
        <p class="sec-header-title">🧭 {T['sec2_title']}</p>
        <span class="status-badge"><span class="status-dot"></span>{T['active_badge']}</span>
    </div>
    <div class="diag-subbanner">
        {T['peak_banner'].format(fecha=fecha_pico.upper(), umbral=f"{umbral_critico:.1f}")}
    </div>
    """, unsafe_allow_html=True)

    etiqueta_dif = T["card_excess"] if diferencia_umbral > 0 else T["card_margin"]
    color_dif = "#ff5a5f" if diferencia_umbral > 0 else "#4ade80"
    signo_dif = f"+{diferencia_umbral:.1f}" if diferencia_umbral > 0 else f"{diferencia_umbral:.1f}"

    st.markdown(f"""
    <div class="mini-kpi-grid">
        <div class="mini-kpi-card" style="border-top-color: #38bdf8;">
            <div class="mini-kpi-label">{T['card_forecast']}</div>
            <div class="mini-kpi-val">{pico_max_dia:.1f}</div>
            <div class="mini-kpi-unit">{UNIT_MM}</div>
        </div>
        <div class="mini-kpi-card" style="border-top-color: #94a3b8;">
            <div class="mini-kpi-label">{T['card_threshold']}</div>
            <div class="mini-kpi-val">{umbral_critico:.1f}</div>
            <div class="mini-kpi-unit">{UNIT_MM}</div>
        </div>
        <div class="mini-kpi-card" style="border-top-color: {color_dif};">
            <div class="mini-kpi-label">{etiqueta_dif}</div>
            <div class="mini-kpi-val" style="color: {color_dif} !important;">{signo_dif}</div>
            <div class="mini-kpi-unit">{UNIT_MM}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    max_escala = max(10.0, float(np.ceil(max(pico_max_dia, umbral_critico * 2) / 2.0) * 2.0))
    paso_tick = 2 if max_escala <= 12 else round(max_escala / 5)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pico_max_dia,
        number={'suffix': f" {UNIT_MM}", 'valueformat': ".1f", 'font': {'size': 34, 'color': '#020b1e', 'family': 'Montserrat'}},
        gauge={
            'axis': {
                'range': [0, max_escala],
                'tickmode': 'linear',
                'tick0': 0,
                'dtick': paso_tick,
                'tickwidth': 2,
                'tickcolor': "#94a3b8",
                'tickfont': {'size': 13, 'color': '#020b1e', 'family': 'Montserrat'}
            },
            'bar': {'color': "#020b1e", 'thickness': 0.32},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 1,
            'bordercolor': "#64748b",
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
        margin=dict(l=26, r=26, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': 'Montserrat'}
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    st.markdown(f"""
    <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:14px; font-size:0.76rem; font-weight:800; color:var(--p-text-primary); margin-top:-6px; margin-bottom:10px;">
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

    st.markdown(f"""
    <div class="diag-alert-card">
        <div class="{badge_cls}">{badge_txt}</div>
        <div style="font-size:1.0rem; font-weight:800; color:var(--p-text-primary); margin-bottom:6px;">{nombre_rubro_activo}</div>
        <div style="font-size:0.88rem; color:var(--p-text-secondary); margin-bottom:2px; line-height:1.45;">{desc_txt}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 10. SECCIÓN 03: INDICADORES CLAVE SIN NUMERACIÓN Y 100% CENTRADOS
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
        <div class="field-kpi-value">{estado_quebrada}</div>
        <span class="field-kpi-pill">📍 {T['kpi3_sub'].format(lat=lat_actual, lon=lon_actual)}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 11. SECCIÓN 04: CRONOGRAMA DE IMPACTO (30 DÍAS)
st.markdown(f"""
<div class="sec-header">
    <p class="sec-header-title">📅 {T['sec4_title']}</p>
</div>
""", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(f"""
    <div class="exec-pill-card">
        <div class="exec-icon-circle" style="background:rgba(2, 132, 199, 0.18); color:#38bdf8;">💧</div>
        <div>
            <div style="font-size:0.78rem; font-weight:800; color:var(--p-text-muted); text-transform:uppercase;">{T['pill_peak']}</div>
            <div style="display:flex; align-items:baseline; gap:10px;">
                <span style="font-size:1.75rem; font-weight:900; color:#ff5a5f;">{pico_max_dia:.1f} <small style="font-size:0.85rem; color:var(--p-text-secondary);">{UNIT_MM}</small></span>
                <span style="font-size:0.84rem; font-weight:700; color:var(--p-text-secondary); border-left:2px solid var(--p-border-card); padding-left:8px;">📅 {fecha_pico}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown(f"""
    <div class="exec-pill-card">
        <div class="exec-icon-circle" style="background:rgba(234, 88, 12, 0.18); color:#fb923c;">🛡️</div>
        <div>
            <div style="font-size:0.78rem; font-weight:800; color:var(--p-text-muted); text-transform:uppercase;">{T['pill_days']}</div>
            <div>
                <span style="font-size:1.75rem; font-weight:900; color:#ff5a5f;">{dias_criticos}</span>
                <span style="font-size:0.88rem; font-weight:700; color:var(--p-text-secondary);"> {T['day_unit']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with p3:
    st.markdown(f"""
    <div class="exec-pill-card">
        <div class="exec-icon-circle" style="background:rgba(56, 189, 248, 0.18); color:#38bdf8;">🧭</div>
        <div>
            <div style="font-size:0.78rem; font-weight:800; color:var(--p-text-muted); text-transform:uppercase;">{T['pill_thresh']}</div>
            <div>
                <span style="font-size:1.75rem; font-weight:900; color:var(--p-text-primary);">{umbral_critico:.1f}</span>
                <span style="font-size:0.88rem; font-weight:700; color:var(--p-text-secondary);"> {UNIT_MM}</span>
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
    textfont=dict(size=10.5),
    name=T["card_forecast"]
))
fig_bar.add_trace(go.Scatter(
    x=df_diario["Fecha"],
    y=df_diario["Pronóstico"],
    mode="lines",
    line=dict(color="rgba(56, 189, 248, 0.55)", width=2, shape="spline"),
    hoverinfo="skip",
    showlegend=False
))
fig_bar.add_hline(
    y=umbral_critico,
    line_dash="dash",
    line_color="#ef4444",
    line_width=2.5,
    annotation_text=f"<b>{T['thresh_tag'].format(umbral=f'{umbral_critico:.1f}')}</b>",
    annotation_position="top right",
    annotation_font=dict(color="white", size=12, family="Montserrat"),
    annotation_bgcolor="#dc2626",
    annotation_borderpad=6
)
fig_bar.update_layout(
    height=370,
    xaxis_title=f"<b>{T['axis_x']}</b>",
    yaxis_title=f"<b>{T['axis_y']}</b>",
    xaxis=dict(tickangle=-45, tickfont=dict(size=10.5)),
    yaxis=dict(
        range=[0, max(umbral_critico * 1.6, pico_max_dia * 1.25, 5.0)],
        gridcolor="rgba(148, 163, 184, 0.22)"
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Montserrat", color="#020b1e"),
    margin=dict(l=20, r=20, t=25, b=35),
    showlegend=False
)
st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

checks_cols_html = "".join([
    f"<div class='rec-check-card'><span style='color:#ef4444; font-weight:900;'>✔</span> {r}</div>"
    for r in lista_recs
])
checks_pdf_html = "".join([f"<div style='margin-bottom:3px; font-weight:600; color:#1e293b;'><span style='color:#dc2626;'>✔</span> {r}</div>" for r in lista_recs])

bg_banner_pdf = "#fff1f2" if pico_max_dia > umbral_critico else ("#fffbeb" if pico_max_dia >= umbral_critico * 0.7 else "#f0fdf4")
border_banner_pdf = "#fecdd3" if pico_max_dia > umbral_critico else ("#fde68a" if pico_max_dia >= umbral_critico * 0.7 else "#bbf7d0")
color_titulo_pdf = "#be123c" if pico_max_dia > umbral_critico else ("#b45309" if pico_max_dia >= umbral_critico * 0.7 else "#15803d")

st.markdown(f"""
<div style="text-align:center; font-size:0.82rem; font-weight:800; color:var(--p-text-primary); margin-top:-6px; margin-bottom:12px;">
    <span style="color:#1d70b8;">●</span> {T['leg_normal']} &nbsp;&nbsp;&nbsp;
    <span style="color:#f59e0b;">●</span> {T['leg_warn']} &nbsp;&nbsp;&nbsp;
    <span style="color:#ef4444;">●</span> {T['leg_crit']}
</div>
<div class="exec-recs-only-banner">
    <div style="font-size:0.92rem; font-weight:900; color:var(--p-text-primary); text-transform:uppercase; margin-bottom:10px; letter-spacing:0.4px;">
        📋 {T['rec_title']} ({nombre_rubro_activo})
    </div>
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:12px;">
        {checks_cols_html}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 12. GENERADOR DE INFOGRAFÍA PDF EN 1 SOLA HOJA A4 CON SELLO DE FECHA Y HORA EN LA PARTE INFERIOR
def disparar_pdf_infografia_una_hoja():
    fechas_js = json.dumps(df_diario["Fecha"].tolist())
    valores_js = json.dumps(df_diario["Pronóstico"].tolist())
    colores_js = json.dumps(colores_barras)
    logo_img_tag = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:52px; border-radius:8px;">' if LOGO_B64 else "<b>PERCET</b>"
    
    hora_peru = datetime.utcnow() - timedelta(hours=5)
    fecha_emision = hora_peru.strftime("%d/%m/%Y — %H:%M:%S")
    sello_inferior_pdf = T["pdf_audit_stamp"].format(fecha_hora=fecha_emision, lat=lat_actual, lon=lon_actual)
    
    max_chart_pdf = round(max(pico_max_dia * 1.28, umbral_critico * 1.45, 4.0), 1)
    color_dif_pdf = "#dc2626" if diferencia_umbral > 0 else "#16a34a"

    filas_1_15 = "".join([
        f"<tr><td>{r['Fecha']}</td><td><b>{r['Pronóstico']}</b></td><td>{r['Prob. Lluvia (%)']}%</td><td>{r['Temp. Máx (°C)']}°</td><td>{r['Temp. Mín (°C)']}°</td><td>{r['Viento Máx (km/h)']}</td></tr>"
        for _, r in df_diario.iloc[:15].iterrows()
    ])
    filas_16_30 = "".join([
        f"<tr><td>{r['Fecha']}</td><td><b>{r['Pronóstico']}</b></td><td>{r['Prob. Lluvia (%)']}%</td><td>{r['Temp. Máx (°C)']}°</td><td>{r['Temp. Mín (°C)']}°</td><td>{r['Viento Máx (km/h)']}</td></tr>"
        for _, r in df_diario.iloc[15:30].iterrows()
    ])

    html_infografia = f"""
    <script>
    function abrirInfografiaPDF() {{
        var win = window.open("", "_blank", "width=1100,height=850");
        var fechas = {fechas_js};
        var valores = {valores_js};
        var colores = {colores_js};
        var maxVal = {max_chart_pdf};
        
        var chartTop = 20;
        var chartBottom = 142;
        var chartHeight = chartBottom - chartTop;
        var barrasSvg = "";

        for (var i = 0; i < fechas.length; i++) {{
            var x = 28 + i * 23.2;
            var h = (valores[i] / maxVal) * chartHeight;
            var y = chartBottom - h;
            barrasSvg += '<rect x="' + x + '" y="' + y + '" width="15.5" height="' + h + '" fill="' + colores[i] + '" rx="2"/>';
            barrasSvg += '<text x="' + (x + 7.75) + '" y="' + (y - 4) + '" font-size="7.2" font-weight="800" text-anchor="middle" fill="#020b1e">' + valores[i] + '</text>';
            barrasSvg += '<text x="' + (x + 7.75) + '" y="156" font-size="6.8" font-weight="700" text-anchor="middle" fill="#334155" transform="rotate(-35 ' + (x + 7.75) + ',156)">' + fechas[i] + '</text>';
        }}
        var yUmbral = chartBottom - ({umbral_critico} / maxVal) * chartHeight;

        var contenido = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>PERCET_GeoRisk_30D_{nombre_proyecto}</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>
                @page {{ size: A4 portrait; margin: 6mm; }}
                * {{ box-sizing: border-box; font-family: 'Montserrat', sans-serif; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
                body {{ margin: 0; padding: 0; background: #ffffff; color: #020b1e; }}
                .page {{ width: 100%; border: 2px solid #042454; border-radius: 10px; padding: 9px 12px; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #020b1e 0%, #042454 100%); color: white; padding: 8px 14px; border-radius: 8px; border-bottom: 4px solid #00b4d8; margin-bottom: 6px; }}
                .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 6px; }}
                .card {{ border: 1px solid #cbd5e1; border-top: 3.5px solid #042454; border-radius: 7px; padding: 5px 9px; background: #f8fafc; text-align: center; }}
                .card-title {{ font-size: 7.8px; font-weight: 800; color: #475569; text-transform: uppercase; text-align: center; }}
                .card-val {{ font-size: 14.5px; font-weight: 900; color: #020b1e; margin: 2px 0; }}
                .sec-title {{ font-size: 9.2px; font-weight: 800; color: #042454; text-transform: uppercase; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 2px; margin: 5px 0 4px 0; }}
                .chart-box {{ border: 1px solid #cbd5e1; border-radius: 7px; padding: 5px 6px 2px 6px; text-align: center; background: #ffffff; margin-bottom: 6px; }}
                .alert-box {{ background: {bg_banner_pdf}; border: 1.5px solid {border_banner_pdf}; border-radius: 8px; padding: 7px 12px; display: grid; grid-template-columns: 1.15fr 1.25fr; gap: 10px; margin-bottom: 6px; }}
                .tables-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 7px; }}
                th {{ background: #042454; color: white; padding: 2.8px 2px; text-transform: uppercase; font-weight: 700; font-size: 6.3px; }}
                td {{ border-bottom: 1px solid #e2e8f0; padding: 1.9px 2px; text-align: center; font-weight: 600; }}
                .sub-tbl-hdr {{ background: #e0f2fe; color: #0369a1; font-size: 7.3px; font-weight: 800; text-align: center; padding: 2px; border-radius: 4px 4px 0 0; border: 1px solid #bae6fd; border-bottom: none; }}
                .footer {{ font-size: 6.9px; color: #64748b; background: #f1f5f9; padding: 5px 9px; border-radius: 5px 5px 0 0; line-height: 1.25; border: 1px solid #cbd5e1; border-bottom: none; }}
                .audit-bar {{ background: #020b1e; color: #ffffff; font-size: 7.2px; padding: 5px 10px; border-radius: 0 0 5px 5px; text-align: center; letter-spacing: 0.3px; border-top: 2px solid #00b4d8; }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="header">
                    <div style="display:flex; align-items:center; gap:12px;">
                        {logo_img_tag}
                        <div>
                            <div style="font-size:13.5px; font-weight:900; letter-spacing:0.5px;">PERCET GEORISK™ | EXECUTIVE TECHNICAL REPORT (30 DAYS)</div>
                            <div style="font-size:9px; color:#38bdf8; font-weight:700; margin-top:2px;">
                                {T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {nombre_rubro_activo}
                            </div>
                            <div style="font-size:8px; color:#cbd5e1; margin-top:2px;">
                                📍 Lat: {lat_actual}, Lon: {lon_actual} &nbsp;|&nbsp; 🕒 {fecha_emision} hrs (UTC-5)
                            </div>
                        </div>
                    </div>
                </div>

                <div class="sec-title">{T['pdf_sec1_title']}</div>
                <div class="grid-3">
                    <div class="card">
                        <div class="card-title">{T['pill_peak']} ({fecha_pico})</div>
                        <div class="card-val" style="color:#dc2626;">{pico_max_dia:.1f} {UNIT_MM}</div>
                        <div style="font-size:7.8px; font-weight:700; color:#475569;">{T['kpi1_sub'].format(acum=lluvia_acumulada)}</div>
                    </div>
                    <div class="card">
                        <div class="card-title">{T['pill_thresh']} / {etiqueta_dif}</div>
                        <div class="card-val">{umbral_critico:.1f} {UNIT_MM} <span style="font-size:11px; color:{color_dif_pdf};">({signo_dif})</span></div>
                        <div style="font-size:7.8px; font-weight:700; color:#475569;">{T['pill_days']}: {dias_criticos} {T['day_unit']}</div>
                    </div>
                    <div class="card">
                        <div class="card-title">{T['kpi2_title']} & {T['pdf_quebradas']}</div>
                        <div class="card-val">{humedad_media}% HR</div>
                        <div style="font-size:7.8px; font-weight:700; color:#020b1e;">{estado_quebrada}</div>
                    </div>
                </div>

                <div class="sec-title">{T['pdf_sec2_title']}</div>
                <div class="chart-box">
                    <svg viewBox="0 0 740 168" width="100%" height="150">
                        <line x1="22" y1="142" x2="725" y2="142" stroke="#94a3b8" stroke-width="1.5"/>
                        ` + barrasSvg + `
                        <line x1="22" y1="` + yUmbral + `" x2="725" y2="` + yUmbral + `" stroke="#dc2626" stroke-width="2" stroke-dasharray="6,4"/>
                        <rect x="588" y="2" width="132" height="15" fill="#dc2626" rx="3"/>
                        <text x="654" y="12" font-size="8.5" font-weight="800" fill="#ffffff" text-anchor="middle">{T['thresh_tag'].format(umbral=f'{umbral_critico:.1f}')}</text>
                    </svg>
                </div>

                <div class="sec-title">{T['pdf_sec3_title']}</div>
                <div class="alert-box">
                    <div>
                        <div style="font-size:9.2px; font-weight:900; color:{color_titulo_pdf}; margin-bottom:2px;">{badge_txt}</div>
                        <div style="font-size:8.8px; font-weight:800; margin-bottom:2px;">{nombre_rubro_activo}</div>
                        <div style="font-size:7.8px; color:#334155; line-height:1.3;">{desc_txt}</div>
                    </div>
                    <div>
                        <div style="font-size:8.3px; font-weight:800; color:#042454; margin-bottom:2px;">{T['rec_title']}:</div>
                        <div style="font-size:7.6px; line-height:1.3;">{checks_pdf_html}</div>
                    </div>
                </div>

                <div class="sec-title">{T['pdf_sec4_title']}</div>
                <div class="tables-2col">
                    <div>
                        <div class="sub-tbl-hdr">{T['pdf_days_1_15']}</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>{T['pdf_col_date']}</th>
                                    <th>{T['pdf_col_fcst']}</th>
                                    <th>{T['pdf_col_prob']}</th>
                                    <th>{T['pdf_col_tmax']}</th>
                                    <th>{T['pdf_col_tmin']}</th>
                                    <th>{T['pdf_col_wind']}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_1_15}
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <div class="sub-tbl-hdr">{T['pdf_days_16_30']}</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>{T['pdf_col_date']}</th>
                                    <th>{T['pdf_col_fcst']}</th>
                                    <th>{T['pdf_col_prob']}</th>
                                    <th>{T['pdf_col_tmax']}</th>
                                    <th>{T['pdf_col_tmin']}</th>
                                    <th>{T['pdf_col_wind']}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_16_30}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="footer">
                    {T['disclaimer']}
                </div>
                <div class="audit-bar">
                    {sello_inferior_pdf}
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

# Botones de Exportación (CSV 30 días y PDF 1 Hoja)
col_dl1, col_dl2 = st.columns(2)
csv_data = df_mostrar.to_csv(index=False).encode('utf-8-sig')
with col_dl1:
    st.download_button(
        label=T["dl_csv"],
        data=csv_data,
        file_name=f"PERCET_GeoRisk_30D_{nombre_proyecto}_{lat_actual}_{lon_actual}.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_dl2:
    if st.button(T["dl_pdf"], use_container_width=True):
        disparar_pdf_infografia_una_hoja()

# 13. DESPLEGABLE TÉCNICO (30 DÍAS) TRADUCIDO SEGÚN EL IDIOMA
with st.expander(T["exp_title"]):
    st.markdown(f"""
{T['ml_bullet_1']}
{T['ml_bullet_2'].format(presion=presion_media)}
    """)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# 14. DISCLAIMER Y BANNER B2B MEJORADO
st.markdown(f'<div class="legal-disclaimer">{T["disclaimer"]}</div>', unsafe_allow_html=True)

if LANG == "ES":
    mensaje_wa = (
        f"👋 Hola PERCET, solicito cotización / asesoría de ingeniería para el proyecto "
        f"*{nombre_proyecto}* 📍[{lat_actual}, {lon_actual}] (🏗️ {nombre_rubro_activo})."
    )
else:
    mensaje_wa = (
        f"👋 Hello PERCET, I'd like to request engineering consulting for the project "
        f"*{nombre_proyecto}* 📍[{lat_actual}, {lon_actual}] (🏗️ {nombre_rubro_activo})."
    )

url_whatsapp = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(mensaje_wa)}"

st.markdown(f"""
<div class="b2b-banner">
    <div class="b2b-banner-title">{T['b2b_title']}</div>
    <div class="b2b-banner-sub">{T['b2b_sub']}</div>
</div>
""", unsafe_allow_html=True)

b1, b2, b3, b4 = st.columns([0.3, 2.2, 2.2, 0.3])
with b2:
    if st.button(T['btn_quote'], use_container_width=True):
        mostrar_modal_cotizacion()
with b3:
    st.link_button(T["btn_wa"], url_whatsapp, use_container_width=True)
