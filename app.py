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
import re
import urllib.parse
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="PERCET GeoRisk™ | Climate Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

CODIGOS_USADOS_FILE = "codigos_usados.json"

def cargar_codigos_usados_disco():
    if os.path.exists(CODIGOS_USADOS_FILE):
        try:
            with open(CODIGOS_USADOS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {str(x).strip().upper() for x in data if x}
        except Exception:
            pass
    return set()

def guardar_codigo_usado_disco(codigo_str):
    actuales = cargar_codigos_usados_disco()
    actuales.add(codigo_str.strip().upper())
    try:
        with open(CODIGOS_USADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(actuales)), f)
    except Exception:
        pass
    return actuales

def correo_valido(correo_str):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo_str.strip()))

if "lat" not in st.session_state:
    st.session_state.lat = -6.8112
if "lon" not in st.session_state:
    st.session_state.lon = -79.7326
if "last_click" not in st.session_state:
    st.session_state.last_click = None
if "pack_desbloqueado" not in st.session_state:
    st.session_state.pack_desbloqueado = False
if "codigo_activo_pack" not in st.session_state:
    st.session_state.codigo_activo_pack = None
if "accion_pendiente_pack" not in st.session_state:
    st.session_state.accion_pendiente_pack = None
if "disparar_pdf_ahora" not in st.session_state:
    st.session_state.disparar_pdf_ahora = False
if "codigos_usados" not in st.session_state:
    st.session_state.codigos_usados = cargar_codigos_usados_disco()

qp_used = st.query_params.get("used_codes", "")
if qp_used:
    for c in str(qp_used).split(","):
        c_clean = c.strip().upper()
        if c_clean:
            st.session_state.codigos_usados.add(c_clean)

LOGO_FILE = "logo.png"
QR_FILE = "qr_pago.png"
CORREO_CORPORATIVO = "oficina.tecnica.puh@outlook.com"
WHATSAPP_NUMERO = "51981328639"
WHATSAPP_COTIZACIONES = "51996025448"
PRECIO_PACK_PEN = 39

CODIGOS_UN_SOLO_USO = {
    "PE4K9M2", "PE7R2X8", "PE1B8V4", "PE9T3L6", "PE5W0Z1", "PE2D7N9", "PE8F4C3", "PE6H1P5", "PE3J9Q7", "PE0S5K8",
    "PE4M2R6", "PE7X8B1", "PE1V4T9", "PE9L6W3", "PE5Z1D0", "PE2N9F7", "PE8C3H4", "PE6P5J2", "PE3Q7S8", "PE0K8M1",
    "PEA49K2", "PEB72R8", "PEC18V4", "PED93L6", "PEF50Z1", "PEG27N9", "PEH84C3", "PEJ61P5", "PEK39Q7", "PEL05K8",
    "PEM42R6", "PEN78B1", "PEP14T9", "PEQ96W3", "PER51D0", "PES29F7", "PET83H4", "PEU65J2", "PEV37S8", "PEW08M1",
    "PE9A4K2", "PE7B2R8", "PE1C8V4", "PE9D3L6", "PE5F0Z1", "PE2G7N9", "PE8H4C3", "PE6J1P5", "PE3K9Q7", "PE0L5K8",
    "PE4M8R2", "PE7N1B6", "PE1P9T4", "PE9Q3W8", "PE5R0D1", "PE2S7F9", "PE8T4H3", "PE6U1J5", "PE3V9S7", "PE0W5M8",
    "PE48A2K", "PE71B8R", "PE19C4V", "PE93D6L", "PE50F1Z", "PE27G9N", "PE84H3C", "PE61J5P", "PE39K7Q", "PE05L8K",
    "PE42M6R", "PE78N1B", "PE14P9T", "PE96Q3W", "PE51R0D", "PE29S7F", "PE83T4H", "PE65U1J", "PE37V9S", "PE08W5M",
    "PEAK492", "PEBR728", "PECV184", "PEDL936", "PEFZ501", "PEGN279", "PEHC843", "PEJP615", "PEKQ397", "PELK058",
    "PEMR426", "PENB781", "PEPT149", "PEQW963", "PERD510", "PESF297", "PETH834", "PEUJ652", "PEVS378", "PEWM081",
    "PE2A8C9", "PE4B1D7", "PE6E3F5", "PE8G5H3", "PE0J7K1", "PE1L9M8", "PE3N2P6", "PE5Q4R4", "PE7S6T2", "PE9U8V0",
    "PE2W0X9", "PE4Y2Z7", "PE6A4B5", "PE8C6D3", "PE0E8F1", "PE1G0H8", "PE3J2K6", "PE5L4M4", "PE7N6P2", "PE9Q8R0",
    "PE2S1T9", "PE4U3V7", "PE6W5X5", "PE8Y7Z3", "PE0A9B1", "PE1C1D8", "PE3E3F6", "PE5G5H4", "PE7J7K2", "PE9L9M0",
    "PE2N1P8", "PE4Q3R6", "PE6S5T4", "PE8U7V2", "PE0W9X0", "PE1Y1Z8", "PE3A3B6", "PE5C5D4", "PE7E7F2", "PE9G9H0",
    "PE2J2K8", "PE4L4M6", "PE6N6P4", "PE8Q8R2", "PE0S0T0", "PE1U2V8", "PE3W4X6", "PE5Y6Z4", "PE7A8B2", "PE9C0D0",
    "PE2E3F8", "PE4G5H6", "PE6J7K4", "PE8L9M2", "PE0N1P0", "PE1Q3R8", "PE3S5T6", "PE5U7V4", "PE7W9X2", "PE9Y1Z0",
    "PE2A4B8", "PE4C6D6", "PE6E8F4", "PE8G0H2", "PE0J2K0", "PE1L4M8", "PE3N6P6", "PE5Q8R4", "PE7S0T2", "PE9U2V0",
    "PE2W5X8", "PE4Y7Z6", "PE6A9B4", "PE8C1D2", "PE0E3F0", "PE1G5H8", "PE3J7K6", "PE5L9M4", "PE7N1P2", "PE9Q3R0",
    "PE2S6T8", "PE4U8V6", "PE6W0X4", "PE8Y2Z2", "PE0A4B0", "PE1C6D8", "PE3E8F6", "PE5G0H4", "PE7J2K2", "PE9L4M0",
    "PE2N7P8", "PE4Q9R6", "PE6S1T4", "PE8U3V2", "PE0W5X0", "PE1Y7Z8", "PE3A9B6", "PE5C1D4", "PE7E3F2", "PE9G5H0",
    "PEA12B3", "PEB23C4", "PEC34D5", "PED45E6", "PEE56F7", "PEF67G8", "PEG78H9", "PEH89J0", "PEJ90K1", "PEK01L2",
    "PEL12M3", "PEM23N4", "PEN34P5", "PEP45Q6", "PEQ56R7", "PER67S8", "PES78T9", "PET89U0", "PEU90V1", "PEV01W2",
    "PEW12X3", "PEX23Y4", "PEY34Z5", "PEZ45A6", "PEA56B7", "PEB67C8", "PEC78D9", "PED89E0", "PEE90F1", "PEF01G2",
    "PEG12H3", "PEH23J4", "PEJ34K5", "PEK45L6", "PEL56M7", "PEM67N8", "PEN78P9", "PEP89Q0", "PEQ90R1", "PER01S2",
    "PES12T3", "PET23U4", "PEU34V5", "PEV45W6", "PEW56X7", "PEX67Y8", "PEY78Z9", "PEZ89A0", "PEA90B1", "PEB01C2",
    "PEC12D3", "PED23E4", "PEE34F5", "PEF45G6", "PEG56H7", "PEH67J8", "PEJ78K9", "PEK89L0", "PEL90M1", "PEM01N2",
    "PEN12P3", "PEP23Q4", "PEQ34R5", "PER45S6", "PES56T7", "PET67U8", "PEU78V9", "PEV89W0", "PEW90X1", "PEX01Y2",
    "PEY12Z3", "PEZ23A4", "PEA34B5", "PEB45C6", "PEC56D7", "PED67E8", "PEE78F9", "PEF89G0", "PEG90H1", "PEH01J2",
    "PEJ12K3", "PEK23L4", "PEL34M5", "PEM45N6", "PEN56P7", "PEP67Q8", "PEQ78R9", "PER89S0", "PES90T1", "PET01U2",
    "PEU12V3", "PEV23W4", "PEW34X5", "PEX45Y6", "PEY56Z7", "PEZ67A8", "PEA78B9", "PEB89C0", "PEC90D1", "PE11A22",
    "PE22B33", "PE33C44", "PE44D55", "PE55E66", "PE66F77", "PE77G88", "PE88H99", "PE99J00", "PE00K11", "PE12L34",
    "PE23M45", "PE34N56", "PE45P67", "PE56Q78", "PE67R89", "PE78S90", "PE89T01", "PE90U12", "PE01V23", "PE13W57",
    "PE24X68", "PE35Y79", "PE46Z80", "PE57A91", "PE68B02", "PE79C13", "PE80D24", "PE91E35", "PE02F46", "PE14G70",
    "PE25H81", "PE36J92", "PE47K03", "PE58L14", "PE69M25", "PE70N36", "PE81P47", "PE92Q58", "PE03R69", "PE15S93",
    "PE26T04", "PE37U15", "PE48V26", "PE59W37", "PE60X48", "PE71Y59", "PE82Z60", "PE93A71", "PE04B82", "PE16C15",
    "PE27D26", "PE38E37", "PE49F48", "PE50G59", "PE61H60", "PE72J71", "PE83K82", "PE94L93", "PE05M04", "PE17N37",
    "PE28P48", "PE39Q59", "PE40R60", "PE51S71", "PE62T82", "PE73U93", "PE84V04", "PE95W15", "PE06X26", "PE18Y59",
    "PE29Z60", "PE30A71", "PE41B82", "PE52C93", "PE63D04", "PE74E15", "PE85F26", "PE96G37", "PE07H48", "PE19J71",
    "PE20K82", "PE31L93", "PE42M04", "PE53N15", "PE64P26", "PE75Q37", "PE86R48", "PE97S59", "PE08T60", "PE10U93",
    "PE21V04", "PE32W15", "PE43X26", "PE54Y37", "PE65Z48", "PE76A59", "PE87B60", "PE98C71", "PE09D82", "PEAB123",
    "PECD234", "PEEF345", "PEGH456", "PEJK567", "PELM678", "PENP789", "PEQR890", "PEST901", "PEUV012", "PEWX123",
    "PEYZ234", "PEAC345", "PEBD456", "PECE567", "PEDF678", "PEEG789", "PEFH890", "PEGJ901", "PEHK012", "PEJL123",
    "PEKM234", "PELN345", "PEMP456", "PENQ567", "PEPR678", "PEQS789", "PERT890", "PESU901", "PETV012", "PEUW123",
    "PEVX234", "PEWY345", "PEXZ456", "PEYA567", "PEZB678", "PEAD789", "PEBE890", "PECF901", "PEDG012", "PEEH123",
    "PEFJ234", "PEGK345", "PEHL456", "PEJM567", "PEKN678", "PELP789", "PEMQ890", "PENR901", "PEPS012", "PEQT123",
    "PERU234", "PESV345", "PETW456", "PEUX567", "PEVY678", "PEWZ789", "PEXA890", "PEYB901", "PEZC012", "PEAE123",
    "PEBF234", "PECG345", "PEDH456", "PEEJ567", "PEFK678", "PEGL789", "PEHM890", "PEJN901", "PEKP012", "PELQ123",
    "PEMR234", "PENS345", "PEPT456", "PEQU567", "PERV678", "PESW789", "PETX890", "PEUY901", "PEVZ012", "PEWA123",
    "PEXB234", "PEYC345", "PEZD456", "PEAF567", "PEBG678", "PECH789", "PEDJ890", "PEEK901", "PEFL012", "PEGM123",
    "PEHN234", "PEJP345", "PEKQ456", "PELR567", "PEMS678", "PENT789", "PEPU890", "PEQV901", "PERW012", "PE9X8Y7",
    "PE8W7V6", "PE7U6T5", "PE6S5R4", "PE5Q4P3", "PE4N3M2", "PE3L2K1", "PE2J1H0", "PE1G0F9", "PE0E9D8", "PE9C8B7",
    "PE8A7Z6", "PE7Y6X5", "PE6W5V4", "PE5U4T3", "PE4S3R2", "PE3Q2P1", "PE2N1M0", "PE1L0K9", "PE0J9H8", "PE9G8F7",
    "PE8E7D6", "PE7C6B5", "PE6A5Z4", "PE5Y4X3", "PE4W3V2", "PE3U2T1", "PE2S1R0", "PE1Q0P9", "PE0N9M8", "PE9L8K7",
    "PE8J7H6", "PE7G6F5", "PE6E5D4", "PE5C4B3", "PE4A3Z2", "PE3Y2X1", "PE2W1V0", "PE1U0T9", "PE0S9R8", "PE9Q8P7",
    "PE8N7M6", "PE7L6K5", "PE6J5H4", "PE5G4F3", "PE4E3D2", "PE3C2B1", "PE2A1Z0", "PE1Y0X9", "PE0W9V8", "PE9U8T7",
    "PE8S7R6", "PE7Q6P5", "PE6N5M4", "PE5L4K3", "PE4J3H2", "PE3G2F1", "PE2E1D0", "PE1C0B9", "PE0A9Z8", "PE9Y8X7",
    "PE8W7V5", "PE7U6T4", "PE6S5R3", "PE5Q4P2", "PE4N3M1", "PE3L2K0", "PE2J1H9", "PE1G0F8", "PE0E9D7", "PE9C8B6",
    "PE8A7Z5", "PE7Y6X4", "PE6W5V3", "PE5U4T2", "PE4S3R1", "PE3Q2P0", "PE2N1M9", "PE1L0K8", "PE0J9H7", "PE9G8F6",
    "PE8E7D5", "PE7C6B4", "PE6A5Z3", "PE5Y4X2", "PE4W3V1", "PE3U2T0", "PE2S1R9", "PE1Q0P8", "PE0N9M7", "PE9L8K6",
    "PE8J7H5", "PE7G6F4", "PE6E5D3", "PE5C4B2", "PE4A3Z1", "PE3Y2X0", "PE2W1V9", "PE1U0T8", "PE0S9R7", "PE7A1B9",
    "PE7C2D8", "PE7E3F7", "PE7G4H6", "PE7J5K5", "PE7L6M4", "PE7N7P3", "PE7Q8R2", "PE7S9T1", "PE7U0V0", "PE8A2B8",
    "PE8C3D7", "PE8E4F6", "PE8G5H5", "PE8J6K4", "PE8L7M3", "PE8N8P2", "PE8Q9R1", "PE8S0T0", "PE8U1V9", "PE9A3B7",
    "PE9C4D6", "PE9E5F5", "PE9G6G4", "PE9J7K3", "PE9L8M2", "PE9N9P1", "PE9Q0R0", "PE9S1T9", "PE9U2V8", "PE0A4B6",
    "PE0C5D5", "PE0E6F4", "PE0G7H3", "PE0J8K2", "PE0L9M1", "PE0N0P0", "PE0Q1R9", "PE0S2T8", "PE0U3V7", "PE1A5B5",
    "PE1C6D4", "PE1E7F3", "PE1G8H2", "PE1J9K1", "PE1L0M0", "PE1N1P9", "PE1Q2R8", "PE1S3T7", "PE1U4V6", "PE2A6B4",
    "PE2C7D3", "PE2E8F2", "PE2G9H1", "PE2J0K0", "PE2L1M9", "PE2N2P8", "PE2Q3R7", "PE2S4T6", "PE2U5V5", "PE3A7B3",
    "PE3C8D2", "PE3E9F1", "PE3G0H0", "PE3J1K9", "PE3L2M8", "PE3N3P7", "PE3Q4R6", "PE3S5T5", "PE3U6V4", "PE4A8B2",
    "PE4C9D1", "PE4E0F0", "PE4G1H9", "PE4J2K8", "PE4L3M7", "PE4N4P6", "PE4Q5R5", "PE4S6T4", "PE4U7V3", "PE5A9B1",
    "PE5C0D0", "PE5E1F9", "PE5G2H8", "PE5J3K7", "PE5L4M6", "PE5N5P5", "PE5Q6R4", "PE5S7T3", "PE5U8V2", "PE6A0B0",
    "PE6C1D9", "PE6E2F8", "PE6G3H7", "PE6J4K6", "PE6L5M5", "PE6N6P4", "PE6Q7R3", "PE6S8T2", "PE6U9V1", "PE891AB",
    "PE782CD", "PE673EF", "PE564GH", "PE455JK", "PE346LM", "PE237NP", "PE128QR", "PE019ST", "PE900UV", "PE892WX",
    "PE783YZ", "PE674AC", "PE565BD", "PE456CE", "PE347DF", "PE238EG", "PE129FH", "PE010GJ", "PE901HK", "PE893JL",
    "PE784KM", "PE675LN", "PE566MP", "PE457NQ", "PE348PR", "PE239QS", "PE120RT", "PE011SU", "PE902TV", "PE894UW",
    "PE785VX", "PE676WY", "PE567XZ", "PE458YA", "PE349ZB", "PE230AD", "PE121BE", "PE012CF", "PE903DG", "PE895EH",
    "PE786FJ", "PE677GK", "PE568HL", "PE459JM", "PE340KN", "PE231LP", "PE122MQ", "PE013NR", "PE904PS", "PE896QT",
    "PE787RU", "PE678SV", "PE569TW", "PE450UX", "PE341VY", "PE232WZ", "PE123XA", "PE014YB", "PE905ZC", "PE897AE",
    "PE788BF", "PE679CG", "PE560DH", "PE451EJ", "PE342FK", "PE233GL", "PE124HM", "PE015JN", "PE906KP", "PE898LQ",
    "PE789MR", "PE670NS", "PE561PT", "PE452QU", "PE343RV", "PE234SW", "PE125TX", "PE016UY", "PE907VZ", "PE899WA",
    "PE780XB", "PE671YC", "PE562ZD", "PE453AF", "PE344BG", "PE235CH", "PE126DJ", "PE017EK", "PE908FL", "PE890GM",
    "PE781HN", "PE672JP", "PE563KQ", "PE454LR", "PE345MS", "PE236NT", "PE127PU", "PE018QV", "PE909RW", "PE891SX",
    "PE782TY", "PE673UZ", "PE564VA", "PE455WB", "PE346XC", "PE237YD", "PE128ZE", "PE019AG", "PE900BH", "PE892CJ",
    "PE783DK", "PE674EL", "PE565FM", "PE456GN", "PE347HP", "PE238JQ", "PE129KR", "PE010LS", "PE901MT", "PE893NU",
    "PE784PV", "PE675QW", "PE566RX", "PE457SY", "PE348TZ", "PE239UA", "PE120VB", "PE011WC", "PE902XD", "PE894YE",
    "PE785ZF", "PE676AH", "PE567BJ", "PE458CK", "PE349DL", "PE230EM", "PE121FN", "PE012GP", "PE903HQ", "PE895JR",
    "PE786KS", "PE677LT", "PE568MU", "PE459NV", "PE340PW", "PE231QX", "PE122RY", "PE013SZ", "PE904TA", "PE896UB",
    "PE787VC", "PE678WD", "PE569XE", "PE450YF", "PE341ZG", "PE232AJ", "PE123BK", "PE014CL", "PE905DM", "PE897EN",
    "PE788FP", "PE679GQ", "PE560HR", "PE451JS", "PE342KT", "PE233LU", "PE124MV", "PE015NW", "PE906PX", "PE898QY",
    "PE789RZ", "PE670SA", "PE561TB", "PE452UC", "PE343VD", "PE234WE", "PE125XF", "PE016YG", "PE907ZH", "PE899AK",
    "PE780BL", "PE671CM", "PE562DN", "PE453EP", "PE344FQ", "PE235GR", "PE126HS", "PE017JT", "PE908KU", "PE890LV",
    "PE781MW", "PE672NX", "PE563PY", "PE454QZ", "PE345RA", "PE236SB", "PE127TC", "PE018UD", "PE909VE", "PEZ19X8",
    "PEY28W7", "PEX37V6", "PEW46U5", "PEV55T4", "PEU64S3", "PET73R2", "PES82Q1", "PER91P0", "PEQ09N8", "PEP18M7",
    "PEN27L6", "PEM36K5", "PEL45J4", "PEK54H3", "PEJ63G2", "PEH72F1", "PEG81E0", "PEF90D9", "PEE09C7", "PED18B6",
    "PEC27A5", "PEB36Z4", "PEA45Y3", "PEZ54X2", "PEY63W1", "PEX72V0", "PEW81U9", "PEV90T8", "PEU09S6", "PET18R5",
    "PES27Q4", "PER36P3", "PEQ45N2", "PEP54M1", "PEN63L0", "PEM72K9", "PEL81J8", "PEK90H7", "PEJ09G5", "PEH18F4",
    "PEG27E3", "PEF36D2", "PEE45C1", "PED54B0", "PEC63A9", "PEB72Z8", "PEA81Y7", "PEZ90X6", "PEY09W4", "PEX18V3",
    "PEW27U2", "PEV36T1", "PEU45S0", "PET54R9", "PES63Q8", "PER72P7", "PEQ81N6", "PEP90M5", "PEN09L3", "PEM18K2",
    "PEL27J1", "PEK36H0", "PEJ45G9", "PEH54F8", "PEG63E7", "PEF72D6", "PEE81C5", "PED90B4", "PEC09A2", "PEB18Z1",
    "PEA27Y0", "PEZ36X9", "PEY45W8", "PEX54V7", "PEW63U6", "PEV72T5", "PEU81S4", "PET90R3", "PES09Q1", "PER18P0",
    "PEQ27N9", "PEP36M8", "PEN45L7", "PEM54K6", "PEL63J5", "PEK72H4", "PEJ81G3", "PEH90F2", "PEG09E0", "PEF18D9",
    "PEE27C8", "PED36B7", "PEC45A6", "PEB54Z5", "PEA63Y4", "PEZ72X3", "PEY81W2", "PEX90V1"
}

def obtener_imagen_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = obtener_imagen_base64(LOGO_FILE)
QR_B64 = obtener_imagen_base64(QR_FILE)

# 2. DICCIONARIO BILINGÜE (HORIZONTE 14 DÍAS REALES - ESPAÑOL & ENGLISH)
TEXTOS = {
    "ES": {
        "unit_mm": "mm/día",
        "lang_label": "🌐 REGIÓN / IDIOMA:",
        "params_header": "⚙️ PARÁMETROS DEL PROYECTO",
        "client_label": "NOMBRE DEL CLIENTE / OBRA:",
        "rubro_label": "PARTIDA CRÍTICA EN EJECUCIÓN (RUBROS MACRO):",
        "thresh_input_label": "UMBRAL ADMISIBLE DE LLUVIA (EDITABLE)",
        "threshold_caption": "Origen: Criterio PERCET / Editable según Expediente Técnico.",
        "enso_label": "ESCENARIO CONSERVADOR EL NIÑO (+25%)",
        "enso_help": "Aplica un factor preventivo de seguridad (+25%) sobre el modelo base satelital para evaluar el umbral. No constituye un pronóstico meteorológico directo.",
        "enso_mode_active": "Evaluando con: Escenario Conservador ENSO (+25%)",
        "enso_mode_base": "Evaluando con: Modelo Base Satelital (Sin ajuste)",
        "header_title": "PERCET GEORISK™ | PLATAFORMA DE INTELIGENCIA CLIMÁTICA PARA LA CONSTRUCCIÓN",
        "header_sub": "Monitoreo satelital multibanda y analítica referencial de riesgos hidroclimáticos para proyectos de ingeniería e infraestructura.",
        "header_client": "CLIENTE / PROYECTO ACTUAL:",
        "header_rubro": "RUBRO:",
        "sec1_title": "01. LOCALIZACIÓN TÉCNICA DE LA OBRA",
        "lat_label": "LATITUD (DECIMAL)",
        "lon_label": "LONGITUD (DECIMAL)",
        "locate_btn": "📍 LOCALIZAR OBRA",
        "map_hint": "Ingrese coordenadas de planos/GPS o haga clic directamente sobre cualquier punto del mapa.",
        "sea_warning": "⚠️ Coordenada ubicada fuera de continente o sobre el océano. Verifique el punto GPS de la obra.",
        "sec2_title": "02. EVALUACIÓN OPERATIVA REFERENCIAL",
        "pdf_report_main_title": "PERCET GEORISK™ | INFORME TÉCNICO REFERENCIAL DE RIESGO CLIMÁTICO (14 DÍAS)",
        "pdf_sec1_title": "01. RESUMEN EJECUTIVO DE INDICADORES & ESCENARIO EVALUADO (14 DÍAS)",
        "pdf_sec2_title": "02. CRONOGRAMA PLUVIAL: PRONÓSTICO (DÍAS 1–7) Y TENDENCIA (DÍAS 8–14) VS. UMBRAL",
        "pdf_sec3_title": "03. EVALUACIÓN TÉCNICA REFERENCIAL & ACCIONES PREVENTIVAS SUGERIDAS",
        "pdf_sec4_title": "04. RESUMEN DE MATRIZ METEOROLÓGICA COMPLETA (14 DÍAS)",
        "active_badge": "MONITOREO ACTIVO",
        "peak_banner": "PICO MÁXIMO · {fecha} · UMBRAL {umbral} mm/día",
        "card_forecast": "VALOR EVALUADO",
        "card_threshold": "UMBRAL",
        "card_excess": "EXCESO",
        "card_margin": "MARGEN SEGURO",
        "leg_normal": "RIESGO BAJO",
        "leg_warn": "RIESGO MODERADO",
        "leg_crit": "RIESGO ALTO",
        "alert_crit_badge": "ALERTA PREVENTIVA · RIESGO ELEVADO",
        "alert_warn_badge": "AVISO OPERATIVO · RIESGO MODERADO",
        "alert_ok_badge": "OPERACIÓN ESTÁNDAR · RIESGO BAJO",
        "diag_crit_desc": "Se estima un pico de <b>{pico} mm/día</b> el <b>{fecha}</b> ({modo_txt}), superando el umbral admisible de <b>{umbral} mm/día</b> en <b>+{exceso} mm/día</b>.",
        "diag_warn_desc": "Se estima un pico de <b>{pico} mm/día</b> el <b>{fecha}</b> ({modo_txt}), próximo al umbral establecido de <b>{umbral} mm/día</b>.",
        "diag_ok_desc": "Se estima un pico máximo de <b>{pico} mm/día</b> ({modo_txt}), manteniéndose dentro del margen seguro inferior al umbral de <b>{umbral} mm/día</b>.",
        "rec_title": "ACCIONES PREVENTIVAS SUGERIDAS PARA EL FRENTE DE OBRA (REFERENCIAL)",
        "peak_detected": "Pico detectado",
        "days_affected": "Días afectados",
        "day_unit": "sobre el umbral",
        "sec3_title": "03. INDICADORES CLAVE DE INGENIERÍA DE CAMPO (HORIZONTE 14 DÍAS)",
        "kpi1_title": "PRECIPITACIÓN EVALUADA (PICO / ACUM.)",
        "kpi1_sub": "Acumulado 14 días: {acum} mm | Base: {base_acum} mm",
        "kpi2_title": "HUMEDAD RELATIVA MEDIA DEL AMBIENTE",
        "kpi2_sub": "Monitoreo referencial de saturación",
        "kpi3_title": "ÍNDICE PLUVIAL REFERENCIAL / QUEBRADAS",
        "kpi3_sub": "Estimación por lluvia acumulada (No reemplaza monitoreo local)",
        "q_red": "ALTO (Precaución por Escorrentía)",
        "q_yellow": "MODERADO (Vigilancia Preventiva)",
        "q_green": "BAJO (Condición Estable)",
        "sec4_title": "04. CRONOGRAMA PLUVIAL: PRONÓSTICO (DÍAS 1–7) Y TENDENCIA (DÍAS 8–14)",
        "pill_peak": "PRECIPITACIÓN MÁXIMA",
        "pill_days": "DÍAS SOBRE EL UMBRAL",
        "pill_thresh": "UMBRAL DE ALERTA",
        "axis_x": "DÍAS 1 AL 7: PRONÓSTICO OPERATIVO  |  DÍAS 8 AL 14: TENDENCIA REFERENCIAL",
        "axis_y": "PRECIPITACIÓN (mm/día)",
        "thresh_tag": "Umbral: {umbral} mm/día",
        "chart_div_left": "◀ PRONÓSTICO (D1-D7)",
        "chart_div_right": "TENDENCIA (D8-D14) ▶",
        "dl_csv": "📥 DESCARGAR MATRIZ 14 DÍAS (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORTAR INFORME TÉCNICO PDF (1 HOJA)",
        "pack_badge_txt": "PACK TÉCNICO (PDF + CSV) · S/ 39 · CÓDIGO DE UN SOLO USO",
        "pack_unlocked_txt": "✅ Pack Técnico (PDF + CSV) desbloqueado con código ({codigo}).",
        "qr_modal_sub": "Incluye <b>Informe PDF (1 hoja)</b> + <b>Matriz CSV/Excel (14 días)</b> con un solo pago de <b>S/ 39</b> (código de un solo uso).",
        "qr_step_1": "1. Escanea el QR y paga <b>S/ 39</b>.",
        "qr_step_2": "2. Envía tu comprobante por WhatsApp para recibir tu código de un solo uso.",
        "qr_step_3": "3. Ingresa aquí tu código de desbloqueo (solo 1 uso):",
        "qr_btn_wa": "📲 ENVIAR COMPROBANTE POR WHATSAPP",
        "qr_code_label": "CÓDIGO DE DESBLOQUEO (UN SOLO USO):",
        "qr_unlock_btn": "🔓 DESBLOQUEAR PACK (PDF + CSV)",
        "qr_code_err": "⚠️ Código no válido o ya utilizado. Solicita un código nuevo por WhatsApp tras confirmar el pago.",
        "qr_missing_file": "Sube el archivo qr_pago.png a tu repositorio para mostrar aquí tu código QR.",
        "exp_title": "🛠️ VER METODOLOGÍA, FUENTES Y MATRIZ METEOROLÓGICA COMPLETA (14 DÍAS)",
        "ml_bullet_1": "* **Fuente Meteorológica en Vivo:** Datos satelitales y modelos numéricos provistos por **Open-Meteo.com (CC BY 4.0)**. Días 1–7 corresponden a Pronóstico Operativo; Días 8–14 corresponden a Tendencia Referencial.",
        "ml_bullet_2": "* **Nota sobre Investigación ML PERCET & Presión Media:** Los parámetros $R^2 = 0.947$, $\\text{{RMSE}} = 0.599\\text{{ mm/día}}$, $\\text{{MAE}} = 0.394\\text{{ mm/día}}$ ($y = 0.871x + 0.163$) corresponden al modelo base de validación científica desarrollado por PERCET. | **Presión Superficial Media:** `{presion} hPa`.",
        "disclaimer": "<b>🛡️ AVISO LEGAL Y ATRIBUCIÓN:</b> PERCET GeoRisk™ es una herramienta analítica referencial de apoyo a la toma de decisiones. No constituye un dictamen pericial ni sustituye los protocolos oficiales de seguridad, supervisión de obra ni estudios definitivos. El factor El Niño (+25%) es un margen preventivo de seguridad configurable por el usuario. Datos meteorológicos: <i>Weather data by Open-Meteo.com (CC BY 4.0)</i>.",
        "pdf_sig_box": "✍️ <b>REVISADO EN OBRA POR:</b> ______________________________________ &nbsp;&nbsp;|&nbsp;&nbsp; <b>ING. RESIDENTE / CIP N°:</b> ______________________",
        "pdf_audit_stamp": "🆔 <b>ID INFORME:</b> {rep_id} &nbsp;|&nbsp; 🕒 <b>EMISIÓN:</b> {fecha_hora} hrs (UTC-5) &nbsp;|&nbsp; 📍 <b>COORD:</b> [{lat}, {lon}] &nbsp;|&nbsp; 🏢 <b>PERCET UNIVERSAL HOLDINGS S.A.C. (RUC: 20614633345)</b>",
        "b2b_title": "🏢 PERCET UNIVERSAL HOLDINGS S.A.C. | INGENIERÍA, OBRAS Y CONSULTORÍA",
        "b2b_sub": "Respaldamos tus proyectos de infraestructura con soluciones de alto nivel técnico:<br>🇵🇪 <b>Perú:</b> Cotización y ejecución física de obras civiles, estructuras metálicas, remodelaciones y supervisión BIM/VDC en campo.<br>🌎 <b>Latinoamérica:</b> Consultoría especializada en mitigación hidrológica, modelamiento BIM/VDC y soporte técnico remoto.",
        "btn_quote": "📝 SOLICITAR COTIZACIÓN DE OBRA / CONSULTORÍA",
        "btn_feedback": "💡 SUGERENCIAS / MEJORAS DE LA PÁGINA",
        "privacy_check": "Acepto el tratamiento de mis datos para fines comerciales y técnicos conforme a la Ley N° 29733 (Ley de Protección de Datos Personales - Perú).",
        "privacy_warn": "⚠️ Debe aceptar la cláusula de Protección de Datos Personales (Ley N° 29733), ingresar un correo válido y completar los campos obligatorios.",
        "api_err_msg": "⚠️ El servicio satelital Open-Meteo no devolvió datos completos en este momento. Por política de integridad técnica (cero datos inventados), reintente la consulta en unos segundos.",
        "col_date": "Fecha",
        "col_horizon": "Horizonte",
        "col_tmax": "Temp. Máx (°C)",
        "col_tmin": "Temp. Mín (°C)",
        "col_tavg": "Temp. Prom (°C)",
        "col_rad": "Radiación (MJ/m²)",
        "col_wind": "Viento Máx (km/h)",
        "col_wdir": "Dirección Viento (°)",
        "col_prob": "Prob. Lluvia (%)",
        "col_base": "Modelo Base (mm/día)",
        "col_enso": "Escenario ENSO +25% (mm/día)",
        "col_fcst": "Valor Evaluado (mm/día)",
        "pdf_col_date": "FECHA",
        "pdf_col_base": "BASE (mm/d)",
        "pdf_col_fcst": "EVAL. (mm/d)",
        "pdf_col_prob": "PROB. (%)",
        "pdf_col_tmax": "T.MÁX (°C)",
        "pdf_col_wind": "VIENTO (km/h)",
        "pdf_quebradas": "ÍNDICE PLUVIAL",
        "pdf_days_1_7": "DÍAS 01 AL 07 — PRONÓSTICO OPERATIVO",
        "pdf_days_8_14": "DÍAS 08 AL 14 — TENDENCIA REFERENCIAL"
    },
    "EN": {
        "unit_mm": "mm/day",
        "lang_label": "🌎 REGION / LANGUAGE:",
        "params_header": "⚙️ PROJECT PARAMETERS",
        "client_label": "CLIENT / PROJECT NAME:",
        "rubro_label": "CRITICAL WORK PACKAGE (MACRO SECTORS):",
        "thresh_input_label": "ALLOWABLE RAINFALL THRESHOLD (EDITABLE)",
        "threshold_caption": "Origin: PERCET Criterion / Editable per Project Specifications.",
        "enso_label": "EL NIÑO CONSERVATIVE SCENARIO (+25%)",
        "enso_help": "Applies a preventive safety factor (+25%) over the base satellite model for threshold evaluation. Not a direct meteorological forecast.",
        "enso_mode_active": "Evaluated with: Conservative ENSO Scenario (+25%)",
        "enso_mode_base": "Evaluated with: Base Satellite Model (Unadjusted)",
        "header_title": "PERCET GEORISK™ | CLIMATE INTELLIGENCE PLATFORM FOR CONSTRUCTION",
        "header_sub": "Multi-band satellite monitoring and referential hydro-climatic risk analytics for infrastructure projects.",
        "header_client": "CURRENT CLIENT / PROJECT:",
        "header_rubro": "SECTOR:",
        "sec1_title": "01. TECHNICAL SITE LOCATION",
        "lat_label": "LATITUDE (DECIMAL)",
        "lon_label": "LONGITUDE (DECIMAL)",
        "locate_btn": "📍 LOCATE SITE",
        "map_hint": "Enter blueprint/GPS coordinates or click directly on any point on the map.",
        "sea_warning": "⚠️ Coordinate appears to be offshore or over the ocean. Please verify the site GPS point.",
        "sec2_title": "02. REFERENTIAL OPERATIONAL ASSESSMENT",
        "pdf_report_main_title": "PERCET GEORISK™ | REFERENTIAL TECHNICAL CLIMATE RISK REPORT (14 DAYS)",
        "pdf_sec1_title": "01. EXECUTIVE KPI SUMMARY & EVALUATED SCENARIO (14 DAYS)",
        "pdf_sec2_title": "02. RAINFALL SCHEDULE: FORECAST (DAYS 1–7) & TREND (DAYS 8–14) VS. THRESHOLD",
        "pdf_sec3_title": "03. REFERENTIAL TECHNICAL ASSESSMENT & SUGGESTED PREVENTIVE ACTIONS",
        "pdf_sec4_title": "04. METEOROLOGICAL DATA MATRIX SUMMARY (14 DAYS)",
        "active_badge": "ACTIVE MONITORING",
        "peak_banner": "MAXIMUM PEAK · {fecha} · THRESHOLD {umbral} mm/day",
        "card_forecast": "EVALUATED VALUE",
        "card_threshold": "THRESHOLD",
        "card_excess": "EXCESS",
        "card_margin": "SAFE MARGIN",
        "leg_normal": "LOW RISK",
        "leg_warn": "MODERATE RISK",
        "leg_crit": "HIGH RISK",
        "alert_crit_badge": "PREVENTIVE ALERT · HIGH RISK",
        "alert_warn_badge": "OPERATIONAL NOTICE · MODERATE RISK",
        "alert_ok_badge": "STANDARD OPERATION · LOW RISK",
        "diag_crit_desc": "A peak of <b>{pico} mm/day</b> is estimated on <b>{fecha}</b> ({modo_txt}), exceeding the allowable threshold of <b>{umbral} mm/day</b> by <b>+{exceso} mm/day</b>.",
        "diag_warn_desc": "A peak of <b>{pico} mm/day</b> is estimated on <b>{fecha}</b> ({modo_txt}), approaching the established threshold of <b>{umbral} mm/day</b>.",
        "diag_ok_desc": "A maximum peak of <b>{pico} mm/day</b> is estimated ({modo_txt}), remaining safely below the threshold of <b>{umbral} mm/day</b>.",
        "rec_title": "SUGGESTED PREVENTIVE FIELD ACTIONS (REFERENTIAL)",
        "peak_detected": "Peak detected",
        "days_affected": "Affected days",
        "day_unit": "above threshold",
        "sec3_title": "03. KEY FIELD ENGINEERING INDICATORS (14-DAY HORIZON)",
        "kpi1_title": "EVALUATED PRECIPITATION (PEAK / ACCUM.)",
        "kpi1_sub": "14-day accum: {acum} mm | Base: {base_acum} mm",
        "kpi2_title": "MEAN AMBIENT RELATIVE HUMIDITY",
        "kpi2_sub": "Referential saturation monitoring",
        "kpi3_title": "REFERENTIAL PLUVIAL / RUNOFF INDEX",
        "kpi3_sub": "Estimated from cumulative rainfall (Does not replace local gauges)",
        "q_red": "HIGH (Runoff Caution)",
        "q_yellow": "MODERATE (Preventive Watch)",
        "q_green": "LOW (Stable Condition)",
        "sec4_title": "04. RAINFALL SCHEDULE: FORECAST (DAYS 1–7) & TREND (DAYS 8–14)",
        "pill_peak": "MAXIMUM PRECIPITATION",
        "pill_days": "DAYS ABOVE THRESHOLD",
        "pill_thresh": "ALERT THRESHOLD",
        "axis_x": "DAYS 1 TO 7: OPERATIONAL FORECAST  |  DAYS 8 TO 14: REFERENTIAL TREND",
        "axis_y": "PRECIPITATION (mm/day)",
        "thresh_tag": "Threshold: {umbral} mm/day",
        "chart_div_left": "◀ FORECAST (D1-D7)",
        "chart_div_right": "TREND (D8-D14) ▶",
        "dl_csv": "📥 DOWNLOAD 14-DAY MATRIX (EXCEL / CSV)",
        "dl_pdf": "📄 EXPORT TECHNICAL PDF REPORT (1 PAGE)",
        "pack_badge_txt": "TECHNICAL PACK (PDF + CSV) · S/ 39 · SINGLE-USE CODE",
        "pack_unlocked_txt": "✅ Technical Pack (PDF + CSV) unlocked with code ({codigo}).",
        "qr_modal_sub": "Includes <b>1-Page PDF Report</b> + <b>14-Day CSV/Excel Matrix</b> with a single payment of <b>S/ 39</b> (single-use code).",
        "qr_step_1": "1. Scan the QR code and pay <b>S/ 39</b>.",
        "qr_step_2": "2. Send your payment receipt via WhatsApp to receive your single-use code.",
        "qr_step_3": "3. Enter your unlock code here (single use only):",
        "qr_btn_wa": "📲 SEND RECEIPT VIA WHATSAPP",
        "qr_code_label": "UNLOCK CODE (SINGLE USE):",
        "qr_unlock_btn": "🔓 UNLOCK PACK (PDF + CSV)",
        "qr_code_err": "⚠️ Invalid or already used code. Request a new code via WhatsApp after payment confirmation.",
        "qr_missing_file": "Upload qr_pago.png to your repository to display your QR code here.",
        "exp_title": "🛠️ VIEW METHODOLOGY, SOURCES & FULL METEOROLOGICAL MATRIX (14 DAYS)",
        "ml_bullet_1": "* **Live Meteorological Source:** Satellite and numerical weather prediction data provided by **Open-Meteo.com (CC BY 4.0)**. Days 1–7 represent Operational Forecast; Days 8–14 represent Referential Trend.",
        "ml_bullet_2": "* **PERCET ML Calibration Research & Mean Pressure:** Metrics $R^2 = 0.947$, $\\text{{RMSE}} = 0.599\\text{{ mm/day}}$, $\\text{{MAE}} = 0.394\\text{{ mm/day}}$ ($y = 0.871x + 0.163$) correspond to PERCET's scientific calibration model. | **Mean Surface Pressure:** `{presion} hPa`.",
        "disclaimer": "<b>🛡️ LEGAL DISCLAIMER & ATTRIBUTION:</b> PERCET GeoRisk™ is a referential analytical support tool. Results constitute technical estimates and do not replace official safety protocols, on-site engineering supervision, or local building codes. The El Niño (+25%) factor is a user-configurable safety margin. Meteorological data: <i>Weather data by Open-Meteo.com (CC BY 4.0)</i>.",
        "pdf_sig_box": "✍️ <b>REVIEWED ON SITE BY:</b> ______________________________________ &nbsp;&nbsp;|&nbsp;&nbsp; <b>RESIDENT ENG. / LICENSE N°:</b> ______________________",
        "pdf_audit_stamp": "🆔 <b>REPORT ID:</b> {rep_id} &nbsp;|&nbsp; 🕒 <b>ISSUED:</b> {fecha_hora} hrs (UTC-5) &nbsp;|&nbsp; 📍 <b>COORD:</b> [{lat}, {lon}] &nbsp;|&nbsp; 🏢 <b>PERCET UNIVERSAL HOLDINGS S.A.C. (TAX ID: 20614633345)</b>",
        "b2b_title": "🌎 PERCET UNIVERSAL HOLDINGS S.A.C. | ENGINEERING & INFRASTRUCTURE SUPPORT",
        "b2b_sub": "We support your infrastructure projects with high-level engineering solutions:<br>🌐 <b>Latin America & Global:</b> Remote hydrological risk consulting, climate modeling, and BIM/VDC digital supervision.<br>🇵🇪 <b>Peru:</b> Full on-site civil works execution, structural steel, remodeling, and field engineering.",
        "btn_quote": "📝 REQUEST ENGINEERING CONSULTING / QUOTE",
        "btn_feedback": "💡 PAGE SUGGESTIONS / IMPROVEMENTS",
        "privacy_check": "I accept the processing of my data for commercial and technical purposes in accordance with Data Protection Law N° 29733 (Peru).",
        "privacy_warn": "⚠️ Please accept the Data Protection clause (Law N° 29733), enter a valid email, and complete all required fields.",
        "api_err_msg": "⚠️ Open-Meteo satellite service did not return complete data at this moment. Per our strict data integrity policy (zero fabricated data), please retry in a few seconds.",
        "col_date": "Date",
        "col_horizon": "Horizon",
        "col_tmax": "Max Temp (°C)",
        "col_tmin": "Min Temp (°C)",
        "col_tavg": "Avg Temp (°C)",
        "col_rad": "Radiation (MJ/m²)",
        "col_wind": "Max Wind (km/h)",
        "col_wdir": "Wind Direction (°)",
        "col_prob": "Rain Prob. (%)",
        "col_base": "Base Model (mm/day)",
        "col_enso": "ENSO Scenario +25% (mm/day)",
        "col_fcst": "Evaluated Value (mm/day)",
        "pdf_col_date": "DATE",
        "pdf_col_base": "BASE (mm/d)",
        "pdf_col_fcst": "EVAL. (mm/d)",
        "pdf_col_prob": "PROB. (%)",
        "pdf_col_tmax": "T.MAX (°C)",
        "pdf_col_wind": "WIND (km/h)",
        "pdf_quebradas": "PLUVIAL INDEX",
        "pdf_days_1_7": "DAYS 01 TO 07 — OPERATIONAL FORECAST",
        "pdf_days_8_14": "DAYS 08 TO 14 — REFERENTIAL TREND"
    }
}

RUBROS_DATA = [
    {
        "umbral": 3.0,
        "es_name": "1. Geotecnia y Movimiento de Tierras",
        "en_name": "1. Geotechnics & Earthworks",
        "es_recs_crit": [
            "Suspender preventivamente la compactación de subrasante por posible saturación.",
            "Perfilar y proteger taludes expuestos con coberturas plásticas o geomembranas.",
            "Verificar operatividad de bombeo en zanjas y cunetas de coronación."
        ],
        "es_recs_warn": [
            "Controlar el contenido de humedad natural antes de compactar capas granulares.",
            "Cubrir acopios de material de préstamo y agregados en cancha."
        ],
        "es_recs_ok": [
            "Condiciones favorables para excavación masiva y conformación de terraplenes.",
            "Mantener inspección rutinaria de drenaje superficial en canteras."
        ],
        "en_recs_crit": [
            "Preventively suspend subgrade compaction due to potential soil saturation.",
            "Protect exposed slopes with plastic tarps or geomembranes.",
            "Verify trench pumping and perimeter runoff drainage readiness."
        ],
        "en_recs_warn": [
            "Verify soil moisture content prior to granular layer compaction.",
            "Cover borrow material and aggregate stockpiles on site."
        ],
        "en_recs_ok": [
            "Favorable conditions for mass excavation and embankment grading.",
            "Maintain routine surface drainage inspection on site."
        ]
    },
    {
        "umbral": 2.0,
        "es_name": "2. Estructuras de Concreto y Acero",
        "en_name": "2. Concrete & Steel Structures",
        "es_recs_crit": [
            "Evaluar reprogramación de vaciados expuestos de losas y elementos horizontales.",
            "Disponer mantas impermeables y carpas sobre elementos recién vaciados.",
            "Controlar humedad superficial de agregados para proteger la relación a/c."
        ],
        "es_recs_warn": [
            "Prever coberturas preventivas sobre frentes de vaciado activo.",
            "Proteger acero de refuerzo habilitado contra humedad prolongada."
        ],
        "es_recs_ok": [
            "Condiciones favorables para colocación y curado de concreto estructural.",
            "Continuar con encofrado y montaje de armaduras según programación."
        ],
        "en_recs_crit": [
            "Evaluate rescheduling exposed slab and horizontal concrete pours.",
            "Deploy waterproof tarps over freshly poured structural elements.",
            "Monitor aggregate surface moisture to protect the water/cement ratio."
        ],
        "en_recs_warn": [
            "Stage preventive tents over active concrete pouring fronts.",
            "Protect staged rebar against prolonged moisture exposure."
        ],
        "en_recs_ok": [
            "Favorable conditions for structural concrete placement and curing.",
            "Proceed with formwork and rebar assembly per schedule."
        ]
    },
    {
        "umbral": 1.0,
        "es_name": "3. Arquitectura y Cierre de Envolvente",
        "en_name": "3. Architecture & Building Envelope",
        "es_recs_crit": [
            "Posponer aplicación de pintura exterior, empastes y selladores en fachada.",
            "Suspender instalación de mantos impermeabilizantes a la intemperie.",
            "Resguardar paneles de drywall, maderas y acabados en almacén techado."
        ],
        "es_recs_warn": [
            "Restringir acabados en fachadas expuestas al viento húmedo.",
            "Priorizar avance de partidas de tabiquería y acabados interiores."
        ],
        "es_recs_ok": [
            "Condición seca favorable para pintura exterior y sellado de envolvente.",
            "Ejecutar instalación de recubrimientos e impermeabilización según plan."
        ],
        "en_recs_crit": [
            "Postpone exterior painting, plastering, and facade sealant application.",
            "Suspend outdoor roof waterproofing membrane installation.",
            "Secure drywall panels, timber, and finishes in covered storage."
        ],
        "en_recs_warn": [
            "Restrict facade finishes exposed to wind-driven moisture.",
            "Prioritize interior drywall and finishing work packages."
        ],
        "en_recs_ok": [
            "Dry conditions favorable for exterior painting and envelope sealing.",
            "Execute roof waterproofing membrane installation as planned."
        ]
    },
    {
        "umbral": 5.0,
        "es_name": "4. Instalaciones y Redes de Servicio",
        "en_name": "4. MEP Installations & Utility Networks",
        "es_recs_crit": [
            "Aislar energía temporal en frentes descubiertos por seguridad eléctrica.",
            "Suspender tendido de tuberías y termofusión en zanjas expuestas a aniego.",
            "Asegurar grupos electrógenos y tableros provisionales con protección IP65."
        ],
        "es_recs_warn": [
            "Revisar aislamiento de empalmes y tableros eléctricos provisionales.",
            "Entibar y proteger zanjas de redes sanitarias e hidráulicas."
        ],
        "es_recs_ok": [
            "Operación segura para montaje electromecánico y tendido de tuberías.",
            "Realizar pruebas hidráulicas y de hermeticidad con normalidad."
        ],
        "en_recs_crit": [
            "Isolate temporary power in open fronts for electrical safety.",
            "Suspend pipe laying and fusion in trenches prone to waterlogging.",
            "Secure generators and temporary switchboards with IP65 protection."
        ],
        "en_recs_warn": [
            "Inspect insulation on splices and temporary distribution boards.",
            "Shore and protect sanitary and hydraulic pipeline trenches."
        ],
        "en_recs_ok": [
            "Safe operation for MEP assembly and utility network laying.",
            "Perform hydraulic and pressure testing as scheduled."
        ]
    }
]

# 3. MOTOR SATELITAL DE 14 DÍAS REALES (CERO DATOS INVENTADOS / CON REINTENTOS Y CACHÉ 1 HORA)
@st.cache_data(ttl=3600, show_spinner=False)
def obtener_datos_satelitales_14d(lat_val, lon_val):
    lat_r = round(float(lat_val), 4)
    lon_r = round(float(lon_val), 4)
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat_r}&longitude={lon_r}"
        f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
        f"precipitation_sum,precipitation_probability_max,wind_speed_10m_max,"
        f"wind_direction_10m_dominant,shortwave_radiation_sum"
        f"&hourly=relative_humidity_2m,surface_pressure"
        f"&timezone=America%2FLima&forecast_days=14"
    )

    ultimo_error = None
    for _ in range(3):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            daily = data.get("daily", {})
            hourly = data.get("hourly", {})

            fechas_raw = daily.get("time", [])
            if not fechas_raw or len(fechas_raw) < 14:
                raise ValueError("Incomplete daily time series from Open-Meteo")

            fechas_base = pd.to_datetime(fechas_raw[:14])

            def extraer_serie_real(clave, decimales=1, es_entero=False):
                lista = daily.get(clave, [])[:14]
                salida = []
                calidad_ok = True
                for x in lista:
                    if x is None or (isinstance(x, float) and np.isnan(x)):
                        salida.append(np.nan)
                        calidad_ok = False
                    else:
                        val = float(x)
                        salida.append(int(round(val)) if es_entero else round(val, decimales))
                return salida, calidad_ok

            tmax_s, ok1 = extraer_serie_real("temperature_2m_max", 1)
            tmin_s, ok2 = extraer_serie_real("temperature_2m_min", 1)
            tmean_s, ok3 = extraer_serie_real("temperature_2m_mean", 1)
            rad_s, ok4 = extraer_serie_real("shortwave_radiation_sum", 2)
            wind_s, ok5 = extraer_serie_real("wind_speed_10m_max", 1)
            wdir_s, ok6 = extraer_serie_real("wind_direction_10m_dominant", 0, es_entero=True)
            prob_s, ok7 = extraer_serie_real("precipitation_probability_max", 0, es_entero=True)
            prec_s, ok8 = extraer_serie_real("precipitation_sum", 1)

            hum_validos = [float(x) for x in hourly.get("relative_humidity_2m", []) if x is not None and not np.isnan(float(x))]
            pres_validos = [float(x) for x in hourly.get("surface_pressure", []) if x is not None and not np.isnan(float(x))]

            humedad_media = round(float(np.mean(hum_validos)), 1) if hum_validos else None
            presion_media = round(float(np.mean(pres_validos)), 1) if pres_validos else None

            df_res = pd.DataFrame({
                "Fecha": fechas_base.strftime('%d-%b'),
                "Temp. Máx (°C)": tmax_s,
                "Temp. Mín (°C)": tmin_s,
                "Temp. Prom (°C)": tmean_s,
                "Radiación (MJ/m²)": rad_s,
                "Viento Máx (km/h)": wind_s,
                "Dirección Viento (°)": wdir_s,
                "Prob. Lluvia (%)": prob_s,
                "Precipitación Base (mm)": prec_s
            })

            aviso_calidad = not all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8])
            return df_res, humedad_media, presion_media, aviso_calidad, None

        except Exception as e:
            ultimo_error = str(e)

    return None, None, None, False, ultimo_error

# 4. SISTEMA DE ESTILOS ADAPTATIVO (LIGHT & DARK MODE + MENÚ DE 3 PUNTOS LIMPIO + PERSISTENCIA EN NAVEGADOR)
def aplicar_estilo_corporativo():
    codigos_json_str = json.dumps(sorted(list(st.session_state.codigos_usados)))
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

    .block-container,
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        padding-top: 1.1rem !important;
        padding-bottom: 2rem !important;
    }

    header[data-testid="stHeader"] {
        background-color: var(--p-bg-main) !important;
        height: 2.3rem !important;
        min-height: 2.3rem !important;
    }

    #MainMenu,
    [data-testid="stMainMenu"],
    [data-testid="stMainMenu"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    [data-testid="stMainMenuDivider"],
    [data-baseweb="popover"] hr,
    [data-baseweb="popover"] [role="separator"],
    [data-baseweb="popover"] ul[role="option"] > li,
    [data-baseweb="popover"] [data-testid="stMainMenuList"] > li,
    [data-baseweb="popover"] hr,
    [data-baseweb="popover"] [role="separator"],
    [data-baseweb="popover"] ul > li {
        display: none !important;
    }

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
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: var(--p-bg-main) !important;
        color: var(--p-text-primary) !important;
    }

    section[data-testid="stSidebar"],
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
    .mini-kpi-val-excess {
        font-size: 1.55rem;
        font-weight: 900;
        color: #ff5a5f !important;
        line-height: 1.15;
        margin: 4px 0 2px 0;
    }
    .mini-kpi-val-margin {
        font-size: 1.55rem;
        font-weight: 900;
        color: #4ade80 !important;
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
        font-size: 0.75rem !important;
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

    .pack-status-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        background-color: var(--p-bg-card);
        border: 1px solid var(--p-border-card);
        border-left: 5px solid #00b4d8;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 12px;
        font-size: 0.82rem;
        font-weight: 800;
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

    .qr-box-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.96);
        border: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 12px;
        margin: 8px auto 12px auto;
        max-width: 240px;
    }
    .qr-box-center img {
        width: 185px;
        height: 185px;
        object-fit: contain;
        border-radius: 8px;
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
    body[data-percet-theme="light"] div[role="dialog"] .qr-box-center span,
    body[data-percet-theme="light"] div[role="dialog"] .qr-box-center p {
        color: #020b1e !important;
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

    components.html(f"""
    <script>
    (function() {{
        var WA_URL = "https://wa.me/51981328639?text=Hola%20PERCET%2C%20solicito%20informacion%20sobre%20PERCET%20GeoRisk";
        var SERVER_USED = {codigos_json_str};

        try {{
            var prevRaw = window.parent.localStorage.getItem("percet_used_codes") || "[]";
            var prevArr = JSON.parse(prevRaw);
            if (!Array.isArray(prevArr)) prevArr = [];
            var merged = Array.from(new Set(prevArr.concat(SERVER_USED).map(function(x) {{ return String(x).toUpperCase().trim(); }}).filter(Boolean)));
            window.parent.localStorage.setItem("percet_used_codes", JSON.stringify(merged));

            var pUrl = new URL(window.parent.location.href);
            var curParam = (pUrl.searchParams.get("used_codes") || "").split(",").map(function(x) {{ return x.toUpperCase().trim(); }}).filter(Boolean);
            var allCodes = Array.from(new Set(merged.concat(curParam)));
            if (allCodes.length > 0 && curParam.join(",") !== allCodes.join(",")) {{
                pUrl.searchParams.set("used_codes", allCodes.join(","));
                window.parent.history.replaceState({{}}, "", pUrl.toString());
            }}
        }} catch (e) {{}}

        var CSS_LIMPIEZA = `
            [data-testid="manage-app-button"],
            button[data-testid="manage-app-button"],
            [data-testid="stToolbarActions"],
            [data-testid="stActionButton"],
            [data-testid="stStatusWidget"],
            [data-testid="stMainMenuDivider"],
            [data-baseweb="popover"] hr,
            [data-baseweb="popover"] [role="separator"],
            [data-baseweb="popover"] ul[role="option"] > li,
            [data-baseweb="popover"] [data-testid="stMainMenuList"] > li,
            [data-baseweb="popover"] hr,
            [data-baseweb="popover"] [role="separator"],
            .stAppDeployButton,
            a[href*="streamlit.io"],
            a[href*="github.com"],
            [class*="viewerBadge"],
            [class*="profileContainer"],
            [class*="profileImage"],
            img[data-testid="appCreatorAvatar"],
            footer {{
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
            }}
        `;

        function getLuminanceFromRgb(rgbStr) {{
            if (!rgbStr) return null;
            var nums = rgbStr.match(/\\d+/g);
            if (nums && nums.length >= 3) {{
                var r = parseInt(nums[0]), g = parseInt(nums[1]), b = parseInt(nums[2]);
                if (nums.length >= 4 && parseFloat(nums[3]) === 0) return null;
                return (r * 299 + g * 587 + b * 114) / 1000;
            }}
            return null;
        }}

        function detectarModoOscuro(pDoc) {{
            var cajas = pDoc.querySelectorAll('div[data-baseweb="base-input"], div[data-baseweb="input"], [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input');
            for (var i = 0; i < cajas.length; i++) {{
                var el = cajas[i];
                if (el.closest('[role="dialog"]')) continue;
                var bg = window.parent.getComputedStyle(el).backgroundColor;
                var lum = getLuminanceFromRgb(bg);
                if (lum !== null) {{
                    return (lum < 128);
                }}
            }}
            try {{
                for (var k = 0; k < window.parent.localStorage.length; k++) {{
                    var key = window.parent.localStorage.key(k);
                    if (key && key.indexOf("stActiveTheme") !== -1) {{
                        var val = window.parent.localStorage.getItem(key) || "";
                        if (val.indexOf('"Dark"') !== -1 || val.indexOf('#0e1117') !== -1) return true;
                        if (val.indexOf('"Light"') !== -1 || val.indexOf('#ffffff') !== -1) return false;
                    }}
                }}
            }} catch (e) {{}}
            return false;
        }}

        function ocultarInsigniaExterna(el) {{
            if (!el || el.dataset.percetHidden === "1") return;
            if (el.closest('[data-baseweb="popover"], [data-testid="stMainMenuPopover"], [data-testid="stMainMenu"]')) return;
            el.dataset.percetHidden = "1";
            try {{
                if (el.tagName === "A") el.href = WA_URL;
                el.onclick = function(e) {{
                    if (e) {{ e.preventDefault(); e.stopPropagation(); }}
                    window.open(WA_URL, "_blank");
                    return false;
                }};
            }} catch (err) {{}}
            el.style.setProperty("transform", "scale(0.0000001)", "important");
            el.style.setProperty("width", "0px", "important");
            el.style.setProperty("height", "0px", "important");
            el.style.setProperty("opacity", "0", "important");
            el.style.setProperty("position", "fixed", "important");
            el.style.setProperty("bottom", "-99999px", "important");
            el.style.setProperty("display", "none", "important");
        }}

        function limpiarMenuTresPuntos(pDoc) {{
            var popovers = pDoc.querySelectorAll('[data-baseweb="popover"], [data-testid="stMainMenuPopover"], [data-testid="stMainMenuList"], ul[role="option"], ul[role="menu"]');
            for (var p = 0; p < popovers.length; p++) {{
                var pop = popovers[p];
                var sep = pop.querySelectorAll('hr, [role="separator"], [data-testid="stMainMenuDivider"]');
                for (var s = 0; s < sep.length; s++) {{
                    sep[s].style.setProperty("display", "none", "important");
                }}
                var items = pop.querySelectorAll('li, button, a, footer');
                for (var i = 0; i < items.length; i++) {{
                    var it = items[i];
                    if (it.dataset.percetItemHidden === "1") continue;
                    var txt = (it.innerText || it.textContent || "").trim().toLowerCase();
                    if (!txt) continue;

                    if (txt.indexOf("system") !== -1 || txt.indexOf("light") !== -1 || txt.indexOf("dark") !== -1) {{
                        continue;
                    }}

                    if (
                        txt.indexOf("rerun") === 0 ||
                        txt.indexOf("clear cache") === 0 ||
                        txt === "print" ||
                        txt.indexOf("record screen") === 0 ||
                        txt.indexOf("made with streamlit") !== -1 ||
                        txt.indexOf("streamlit v") !== -1 ||
                        txt.indexOf("developer options") === 0 ||
                        txt === "about" ||
                        txt.indexOf("report a bug") === 0 ||
                        txt.indexOf("get help") === 0
                    ) {{
                        var target = it.closest("li") || it;
                        var targetTxt = (target.innerText || target.textContent || "").toLowerCase();
                        if (targetTxt.indexOf("system") === -1 && targetTxt.indexOf("light") === -1 && targetTxt.indexOf("dark") === -1) {{
                            target.dataset.percetItemHidden = "1";
                            target.style.setProperty("display", "none", "important");
                        }}
                    }}
                }}
            }}
        }}

        function cicloPrincipal() {{
            try {{
                var pDoc = window.parent.document;
                if (!pDoc) return;

                if (pDoc.head && !pDoc.getElementById("percet-fast-css")) {{
                    var st = pDoc.createElement("style");
                    st.id = "percet-fast-css";
                    st.innerHTML = CSS_LIMPIEZA;
                    pDoc.head.appendChild(st);
                }}
                try {{
                    if (window.top && window.top.document && window.top.document.head && !window.top.document.getElementById("percet-fast-css-top")) {{
                        var stTop = window.top.document.createElement("style");
                        stTop.id = "percet-fast-css-top";
                        stTop.innerHTML = CSS_LIMPIEZA;
                        window.top.document.head.appendChild(stTop);
                    }}
                }} catch (e) {{}}

                limpiarMenuTresPuntos(pDoc);

                var links = pDoc.querySelectorAll('a[href*="streamlit.io"], [data-testid="manage-app-button"]');
                for (var j = 0; j < links.length; j++) {{
                    ocultarInsigniaExterna(links[j]);
                }}

                var isDark = detectarModoOscuro(pDoc);
                var temaActual = isDark ? "dark" : "light";
                if (pDoc.body.getAttribute("data-percet-theme") !== temaActual) {{
                    pDoc.body.setAttribute("data-percet-theme", temaActual);
                }}

                var textColor = isDark ? "#ffffff" : "#020b1e";
                var svgTexts = pDoc.querySelectorAll(".js-plotly-plot svg text");
                for (var k = 0; k < svgTexts.length; k++) {{
                    var t = svgTexts[k];
                    var desired = t.closest(".annotation-text-g") ? "#ffffff" : textColor;
                    if (t.dataset.percetColor !== desired) {{
                        t.dataset.percetColor = desired;
                        t.style.setProperty("fill", desired, "important");
                    }}
                }}
            }} catch (e) {{}}
        }}

        cicloPrincipal();
        setInterval(cicloPrincipal, 200);

        setInterval(function() {{
            try {{ fetch(window.parent.location.href, {{ method: "HEAD", cache: "no-store" }}); }} catch (e) {{}}
        }}, 300000);
    }})();
    </script>
    """, height=0, width=0)

aplicar_estilo_corporativo()

# 5. BARRA LATERAL CON UMBRAL EDITABLE POR EL USUARIO Y SEPARACIÓN DEL FACTOR ENSO (+25%)
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
    
    umbral_critico = st.number_input(
        T["thresh_input_label"],
        min_value=0.2,
        max_value=50.0,
        value=float(rubro_actual["umbral"]),
        step=0.5,
        format="%.1f",
        key=f"umbral_editable_{idx_rubro}"
    )
    st.caption(f"ℹ️ {T['threshold_caption']}")
    
    modo_enso = st.toggle(T["enso_label"], value=True, help=T["enso_help"])
    st.caption(f"📌 **{T['enso_mode_active'] if modo_enso else T['enso_mode_base']}**")

# 6. MODAL DE PAGO CON QR (qr_pago.png) Y CÓDIGOS DE UN SOLO USO PARA DESBLOQUEAR EL PACK (S/ 39)
@st.dialog(" ")
def mostrar_modal_pago_pack():
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" class="modal-brand-logo">' if LOGO_B64 else ""
    st.markdown(f"""
    <div class="modal-brand-header">
        {logo_html}
        <div class="modal-brand-title">PACK TÉCNICO<br>PERCET · S/ {PRECIO_PACK_PEN}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 10px;">
        <div style="font-size: 0.84rem; font-weight: 800; line-height: 1.4;">
            {T['qr_modal_sub']}
        </div>
        <div style="font-size: 0.78rem; font-weight: 700; margin-top: 6px; line-height: 1.45;">
            {T['qr_step_1']}<br>
            {T['qr_step_2']}<br>
            {T['qr_step_3']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if QR_B64:
        st.markdown(f"""
        <div class="qr-box-center">
            <img src="data:image/png;base64,{QR_B64}" alt="QR de Pago PERCET">
            <span style="font-size:0.75rem; font-weight:900; margin-top:6px;">PACK PDF + CSV · S/ {PRECIO_PACK_PEN}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(T["qr_missing_file"])

    msg_pago_wa = (
        f"Hola PERCET, realice el pago de S/ {PRECIO_PACK_PEN} por el Pack Tecnico (PDF + CSV) "
        f"para el proyecto *{nombre_proyecto}* | Coord. [{st.session_state.lat}, {st.session_state.lon}] "
        f"({nombre_rubro_activo}). Adjunto mi comprobante para recibir mi codigo de un solo uso."
    )
    link_pago_wa = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg_pago_wa)}"
    st.link_button(T["qr_btn_wa"], link_pago_wa, use_container_width=True)

    codigo_ingresado = st.text_input(T["qr_code_label"], placeholder="Ej. PE7M4Q9", max_chars=20).strip().upper()
    if st.button(T["qr_unlock_btn"], type="primary", use_container_width=True):
        usados_actuales = st.session_state.codigos_usados.union(cargar_codigos_usados_disco())
        st.session_state.codigos_usados = usados_actuales
        if codigo_ingresado in CODIGOS_UN_SOLO_USO and codigo_ingresado not in usados_actuales:
            guardar_codigo_usado_disco(codigo_ingresado)
            st.session_state.codigos_usados.add(codigo_ingresado)
            st.session_state.pack_desbloqueado = True
            st.session_state.codigo_activo_pack = codigo_ingresado
            if st.session_state.accion_pendiente_pack == "pdf":
                st.session_state.disparar_pdf_ahora = True
            st.session_state.accion_pendiente_pack = None
            st.rerun()
        else:
            st.warning(T["qr_code_err"])

# 7. MODAL DE SOLICITUD REDIRIGIDO A WHATSAPP (+51 996 025 448) SIN CARGADOR DE PDF EN LA WEB
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
                Se generará tu ficha de cotización ordenada para enviarla por WhatsApp (adjunta tus planos o PDFs directamente en el chat).
            </div>
        </div>
        """, unsafe_allow_html=True)
        emp = st.text_input("EMPRESA / CONSTRUCTORA O CLIENTE:", max_chars=100).strip()
        correo_cli_raw = st.text_input("CORREO CORPORATIVO:", placeholder="cliente@empresa.com", max_chars=100).strip()
        tel_cli = st.text_input("TELÉFONO / WHATSAPP DE CONTACTO:", max_chars=40).strip()
        detalle_req = st.text_area(
            "DETALLE SU REQUERIMIENTO O PROYECTO A COTIZAR (Ej. Estructura metálica, remodelación, obras civiles, consultoría BIM/VDC):",
            height=105,
            max_chars=1200
        ).strip()
        consentimiento_ley = st.checkbox(T["privacy_check"], value=True)
        
        if st.button("🚀 GENERAR COTIZACIÓN PARA WHATSAPP", type="primary", use_container_width=True):
            if emp and correo_cli_raw and correo_valido(correo_cli_raw) and detalle_req and consentimiento_ley:
                mensaje_cotizacion_wa = (
                    f"*SOLICITUD DE COTIZACION - PERCET GEORISK (ES)*\n"
                    f"----------------------------------------\n"
                    f"*1. DATOS DEL CLIENTE / EMPRESA*\n"
                    f"- Empresa / Cliente: {emp}\n"
                    f"- Correo: {correo_cli_raw}\n"
                    f"- Telefono / WhatsApp: {tel_cli if tel_cli else 'No indicado'}\n\n"
                    f"*2. CONTEXTO DE OBRA / EVALUACION*\n"
                    f"- Proyecto / Obra: {nombre_proyecto}\n"
                    f"- Rubro: {nombre_rubro_activo}\n"
                    f"- Umbral configurado: {umbral_critico:.1f} mm/dia\n"
                    f"- Coordenadas: [{st.session_state.lat}, {st.session_state.lon}]\n\n"
                    f"*3. REQUERIMIENTOS A COTIZAR*\n"
                    f"{detalle_req}\n\n"
                    f"*4. ADJUNTOS Y CONFORMIDAD*\n"
                    f"- Planos o PDFs: Adjuntarlos directamente en este chat de WhatsApp si aplica\n"
                    f"- Proteccion de datos (Ley N 29733): Aceptada"
                )
                wa_cot_url = f"https://wa.me/{WHATSAPP_COTIZACIONES}?text={urllib.parse.quote(mensaje_cotizacion_wa)}"
                st.success("✅ Cotización lista para enviar por WhatsApp.")
                st.link_button("📲 ABRIR WHATSAPP Y ENVIAR COTIZACIÓN", wa_cot_url, use_container_width=True)
            else:
                st.warning(T["privacy_warn"])
    else:
        st.markdown("""
        <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px;">
                💻 ENGINEERING CONSULTING & PROJECT QUOTES
            </div>
            <div style="font-size: 0.78rem; font-weight: 700; margin-top: 3px;">
                A structured quote message will be prepared to send via WhatsApp (attach drawings or PDFs directly in WhatsApp).
            </div>
        </div>
        """, unsafe_allow_html=True)
        emp = st.text_input("COMPANY / CONTRACTOR OR CLIENT NAME:", max_chars=100).strip()
        correo_cli_raw = st.text_input("CORPORATE EMAIL:", placeholder="client@company.com", max_chars=100).strip()
        tel_cli = st.text_input("CONTACT PHONE / WHATSAPP:", max_chars=40).strip()
        detalle_req = st.text_area(
            "PLEASE DETAIL YOUR PROJECT OR TECHNICAL REQUEST (e.g., Remote BIM/VDC consulting, hydrological study, civil works in Peru):",
            height=105,
            max_chars=1200
        ).strip()
        consentimiento_ley = st.checkbox(T["privacy_check"], value=True)
        
        if st.button("🚀 GENERATE QUOTE FOR WHATSAPP", type="primary", use_container_width=True):
            if emp and correo_cli_raw and correo_valido(correo_cli_raw) and detalle_req and consentimiento_ley:
                mensaje_cotizacion_wa = (
                    f"*QUOTE REQUEST - PERCET GEORISK (EN)*\n"
                    f"----------------------------------------\n"
                    f"*1. CLIENT / COMPANY DETAILS*\n"
                    f"- Company / Client: {emp}\n"
                    f"- Email: {correo_cli_raw}\n"
                    f"- Phone / WhatsApp: {tel_cli if tel_cli else 'Not provided'}\n\n"
                    f"*2. PROJECT & SITE CONTEXT*\n"
                    f"- Project / Site: {nombre_proyecto}\n"
                    f"- Sector: {nombre_rubro_activo}\n"
                    f"- Configured Threshold: {umbral_critico:.1f} mm/day\n"
                    f"- Coordinates: [{st.session_state.lat}, {st.session_state.lon}]\n\n"
                    f"*3. PROJECT REQUIREMENTS*\n"
                    f"{detalle_req}\n\n"
                    f"*4. ATTACHMENTS & CONSENT*\n"
                    f"- Drawings / PDFs: Attach directly in this WhatsApp chat if applicable\n"
                    f"- Data Protection (Law N 29733): Accepted"
                )
                wa_cot_url = f"https://wa.me/{WHATSAPP_COTIZACIONES}?text={urllib.parse.quote(mensaje_cotizacion_wa)}"
                st.success("✅ Quote ready to send via WhatsApp.")
                st.link_button("📲 OPEN WHATSAPP AND SEND QUOTE", wa_cot_url, use_container_width=True)
            else:
                st.warning(T["privacy_warn"])

# 7B. MODAL INTERACTIVO DE SUGERENCIAS Y MEJORAS HACIA WHATSAPP (+51 981328639) CON ESTRELLAS (1 A 5)
@st.dialog(" ")
def mostrar_modal_sugerencias():
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" class="modal-brand-logo">' if LOGO_B64 else ""
    st.markdown(f"""
    <div class="modal-brand-header">
        {logo_html}
        <div class="modal-brand-title">SUGERENCIAS<br>PERCET GEORISK™</div>
    </div>
    """, unsafe_allow_html=True)

    if LANG == "ES":
        st.markdown("""
        <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px;">
                💡 MEJORAS DE LA PÁGINA (WHATSAPP +51 981 328 639)
            </div>
            <div style="font-size: 0.78rem; font-weight: 700; margin-top: 3px;">
                Envía tus sugerencias o ideas de mejora para ir perfeccionando la plataforma paso a paso.
            </div>
        </div>
        """, unsafe_allow_html=True)
        nombre_sug = st.text_input("TU NOMBRE / ROL (Ej. Ing. Residente, Supervisor):", max_chars=80).strip()
        area_mejora = st.selectbox(
            "SECCIÓN A MEJORAR:",
            ["Mapa y coordenadas", "Gráficos y umbrales", "Informe PDF / Matriz CSV", "Nueva partida o rubro", "Experiencia / diseño general"]
        )
        st.markdown("<div style='font-size:0.78rem; font-weight:800; margin-top:4px; margin-bottom:2px;'>VALORACIÓN DE LA PÁGINA (1 A 5 ESTRELLAS):</div>", unsafe_allow_html=True)
        estrellas_sel = st.feedback("stars", key="stars_feedback_es")
        comentario_sug = st.text_area(
            "ESCRIBE TU SUGERENCIA O IDEA DE MEJORA:",
            placeholder="Ej. Me gustaría ajustar el tamaño de fuente o agregar un dato extra...",
            height=95,
            max_chars=800
        ).strip()

        if st.button("🚀 GENERAR SUGERENCIA PARA WHATSAPP (+51 981 328 639)", type="primary", use_container_width=True):
            if comentario_sug:
                valor_estrellas = (estrellas_sel + 1) if estrellas_sel is not None else 5
                estrellas_visual = "*" * valor_estrellas
                texto_sug = (
                    f"*SUGERENCIA / MEJORA - PERCET GEORISK*\n"
                    f"----------------------------------------\n"
                    f"- Nombre / Rol: {nombre_sug if nombre_sug else 'Visitante'}\n"
                    f"- Seccion: {area_mejora}\n"
                    f"- Valoracion: {valor_estrellas}/5 ({estrellas_visual})\n"
                    f"- Proyecto / Coord.: {nombre_proyecto} [{st.session_state.lat}, {st.session_state.lon}]\n"
                    f"- Sugerencia:\n{comentario_sug}"
                )
                wa_sug_url = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(texto_sug)}"
                st.success("✅ Sugerencia lista para enviar al **+51 981 328 639**.")
                st.link_button("📲 ENVIAR SUGERENCIA POR WHATSAPP (+51 981 328 639)", wa_sug_url, use_container_width=True)
            else:
                st.warning("⚠️ Escribe una sugerencia o comentario antes de continuar.")
    else:
        st.markdown("""
        <div style="background: rgba(0, 180, 216, 0.20); border-left: 5px solid #00b4d8; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px;">
                💡 PAGE IMPROVEMENTS (WHATSAPP +51 981 328 639)
            </div>
            <div style="font-size: 0.78rem; font-weight: 700; margin-top: 3px;">
                Share suggestions or ideas to improve the platform step by step.
            </div>
        </div>
        """, unsafe_allow_html=True)
        nombre_sug = st.text_input("YOUR NAME / ROLE (e.g., Site Engineer, PM):", max_chars=80).strip()
        area_mejora = st.selectbox(
            "SECTION TO IMPROVE:",
            ["Map & Coordinates", "Charts & Thresholds", "PDF Report / CSV Matrix", "New Work Sector", "General UX / Design"]
        )
        st.markdown("<div style='font-size:0.78rem; font-weight:800; margin-top:4px; margin-bottom:2px;'>PAGE RATING (1 TO 5 STARS):</div>", unsafe_allow_html=True)
        estrellas_sel = st.feedback("stars", key="stars_feedback_en")
        comentario_sug = st.text_area(
            "WRITE YOUR SUGGESTION OR IMPROVEMENT IDEA:",
            placeholder="e.g., Adjust font sizing or add an extra metric...",
            height=95,
            max_chars=800
        ).strip()

        if st.button("🚀 GENERATE SUGGESTION FOR WHATSAPP (+51 981 328 639)", type="primary", use_container_width=True):
            if comentario_sug:
                valor_estrellas = (estrellas_sel + 1) if estrellas_sel is not None else 5
                estrellas_visual = "*" * valor_estrellas
                texto_sug = (
                    f"*PAGE SUGGESTION - PERCET GEORISK*\n"
                    f"----------------------------------------\n"
                    f"- Name / Role: {nombre_sug if nombre_sug else 'Visitor'}\n"
                    f"- Section: {area_mejora}\n"
                    f"- Rating: {valor_estrellas}/5 ({estrellas_visual})\n"
                    f"- Project / Coord.: {nombre_proyecto} [{st.session_state.lat}, {st.session_state.lon}]\n"
                    f"- Suggestion:\n{comentario_sug}"
                )
                wa_sug_url = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(texto_sug)}"
                st.success("✅ Suggestion ready to send to **+51 981 328 639**.")
                st.link_button("📲 SEND SUGGESTION VIA WHATSAPP (+51 981 328 639)", wa_sug_url, use_container_width=True)
            else:
                st.warning("⚠️ Please enter a suggestion or comment before continuing.")

# 8. ENCABEZADO SUPERIOR
st.markdown(f"""
<div class="corporate-header">
    <p class="corporate-title">{T['header_title']}</p>
    <p class="corporate-subtitle">{T['header_sub']}</p>
    <p class="corporate-client">{T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {T['header_rubro']} {nombre_rubro_activo}</p>
</div>
""", unsafe_allow_html=True)

# 9. OBTENCIÓN DE DATOS SATELITALES REALES (14 DÍAS: 1–7 PRONÓSTICO Y 8–14 TENDENCIA)
lat_actual = float(st.session_state.lat)
lon_actual = float(st.session_state.lon)

df_base_14d, humedad_media, presion_media, aviso_calidad, err_api = obtener_datos_satelitales_14d(lat_actual, lon_actual)

if df_base_14d is None:
    st.warning(T["api_err_msg"])
    st.stop()

df_diario = df_base_14d.copy()

df_diario["Modelo Base"] = df_diario["Precipitación Base (mm)"].round(1)
df_diario["Escenario ENSO (+25%)"] = (df_diario["Precipitación Base (mm)"] * 1.25).round(1)
df_diario["Pronóstico"] = df_diario["Escenario ENSO (+25%)"] if modo_enso else df_diario["Modelo Base"]

horizonte_etiquetas = [
    ("Pronóstico (D1-D7)" if i < 7 else "Tendencia (D8-D14)") if LANG == "ES"
    else ("Forecast (D1-D7)" if i < 7 else "Trend (D8-D14)")
    for i in range(len(df_diario))
]
df_diario["Horizonte"] = horizonte_etiquetas

df_mostrar = pd.DataFrame({
    T["col_date"]: df_diario["Fecha"],
    T["col_horizon"]: df_diario["Horizonte"],
    T["col_base"]: df_diario["Modelo Base"],
    T["col_enso"]: df_diario["Escenario ENSO (+25%)"],
    T["col_fcst"]: df_diario["Pronóstico"],
    T["col_prob"]: df_diario["Prob. Lluvia (%)"],
    T["col_tmax"]: df_diario["Temp. Máx (°C)"],
    T["col_tmin"]: df_diario["Temp. Mín (°C)"],
    T["col_tavg"]: df_diario["Temp. Prom (°C)"],
    T["col_rad"]: df_diario["Radiación (MJ/m²)"],
    T["col_wind"]: df_diario["Viento Máx (km/h)"],
    T["col_wdir"]: df_diario["Dirección Viento (°)"]
})

pico_max_dia = float(df_diario["Pronóstico"].max())
fecha_pico = df_diario.loc[df_diario["Pronóstico"].idxmax(), "Fecha"]
lluvia_acumulada = round(float(df_diario["Pronóstico"].sum()), 1)
lluvia_base_acum = round(float(df_diario["Modelo Base"].sum()), 1)
dias_criticos = int((df_diario["Pronóstico"] > umbral_critico).sum())
diferencia_umbral = round(pico_max_dia - umbral_critico, 1)

humedad_txt = f"{humedad_media}" if humedad_media is not None else "S/D"
presion_txt = f"{presion_media}" if presion_media is not None else "S/D"

if pico_max_dia >= 15.0 or lluvia_acumulada >= 55.0:
    estado_quebrada = f"🔴 {T['q_red']}"
elif pico_max_dia >= 5.0 or lluvia_acumulada >= 22.0:
    estado_quebrada = f"🟡 {T['q_yellow']}"
else:
    estado_quebrada = f"🟢 {T['q_green']}"

codigo_unico_id = f"PG-{datetime.now().strftime('%Y')}-{abs(hash(f'{nombre_proyecto}_{lat_actual}_{lon_actual}_{fecha_pico}')) % 90000 + 10000}"

# 10. SECCIÓN 01 (MAPA CON NORTE) Y SECCIÓN 02 (EVALUACIÓN OPERATIVA)
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
    if lon_actual < -81.4 or (lat_actual < -14.0 and lon_actual < -76.8):
        st.caption(f"<span style='color:#f59e0b; font-weight:700;'>{T['sea_warning']}</span>", unsafe_allow_html=True)
    
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
    clase_val_dif = "mini-kpi-val-excess" if diferencia_umbral > 0 else "mini-kpi-val-margin"
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
            <div class="{clase_val_dif}">{signo_dif}</div>
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

    modo_eval_corto = ("Escenario ENSO +25%" if modo_enso else "Modelo Base") if LANG == "ES" else ("ENSO Scenario +25%" if modo_enso else "Base Model")

    if pico_max_dia > umbral_critico:
        badge_cls = "diag-badge-crit"
        badge_txt = f"🚨 {T['alert_crit_badge']}"
        desc_txt = T["diag_crit_desc"].format(pico=f"{pico_max_dia:.1f}", fecha=fecha_pico, modo_txt=modo_eval_corto, umbral=f"{umbral_critico:.1f}", exceso=f"{diferencia_umbral:.1f}")
        lista_recs = rubro_actual["es_recs_crit"] if LANG == "ES" else rubro_actual["en_recs_crit"]
    elif pico_max_dia >= umbral_critico * 0.7:
        badge_cls = "diag-badge-warn"
        badge_txt = f"⚠️ {T['alert_warn_badge']}"
        desc_txt = T["diag_warn_desc"].format(pico=f"{pico_max_dia:.1f}", fecha=fecha_pico, modo_txt=modo_eval_corto, umbral=f"{umbral_critico:.1f}")
        lista_recs = rubro_actual["es_recs_warn"] if LANG == "ES" else rubro_actual["en_recs_warn"]
    else:
        badge_cls = "diag-badge-ok"
        badge_txt = f"✅ {T['alert_ok_badge']}"
        desc_txt = T["diag_ok_desc"].format(pico=f"{pico_max_dia:.1f}", modo_txt=modo_eval_corto, umbral=f"{umbral_critico:.1f}")
        lista_recs = rubro_actual["es_recs_ok"] if LANG == "ES" else rubro_actual["en_recs_ok"]

    st.markdown(f"""
    <div class="diag-alert-card">
        <div class="{badge_cls}">{badge_txt}</div>
        <div style="font-size:1.0rem; font-weight:800; color:var(--p-text-primary); margin-bottom:6px;">{nombre_rubro_activo}</div>
        <div style="font-size:0.88rem; color:var(--p-text-secondary); margin-bottom:2px; line-height:1.45;">{desc_txt}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 11. SECCIÓN 03: INDICADORES CLAVE SIN NUMERACIÓN Y 100% CENTRADOS (14 DÍAS)
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
        <span class="field-kpi-pill">🌧️ {T['kpi1_sub'].format(acum=lluvia_acumulada, base_acum=lluvia_base_acum)}</span>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="field-kpi-card">
        <div class="field-kpi-title">{T['kpi2_title']}</div>
        <div class="field-kpi-value">{humedad_txt} %</div>
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

# 12. SECCIÓN 04: CRONOGRAMA DE IMPACTO (DÍAS 1–7 PRONÓSTICO Y DÍAS 8–14 TENDENCIA)
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
opacidad_barras = [1.0 if i < 7 else 0.68 for i in range(len(df_diario))]

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=df_diario["Fecha"],
    y=df_diario["Pronóstico"],
    marker=dict(color=colores_barras, opacity=opacidad_barras),
    text=[f"<b>{v:.1f}</b>" if v > 0 else "0" for v in df_diario["Pronóstico"]],
    textposition="outside",
    textfont=dict(size=11),
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
fig_bar.add_vline(
    x=6.5,
    line_dash="dot",
    line_color="#64748b",
    line_width=2
)
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
y_top_chart = max(umbral_critico * 1.6, pico_max_dia * 1.28, 5.0)
fig_bar.update_layout(
    height=360,
    xaxis_title=f"<b>{T['axis_x']}</b>",
    yaxis_title=f"<b>{T['axis_y']}</b>",
    xaxis=dict(tickfont=dict(size=11)),
    yaxis=dict(
        range=[0, y_top_chart],
        gridcolor="rgba(148, 163, 184, 0.22)"
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Montserrat", color="#020b1e"),
    margin=dict(l=20, r=20, t=25, b=30),
    showlegend=False
)
st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

checks_cols_html = "".join([
    f"<div class='rec-check-card'><span style='color:#ef4444; font-weight:900;'>✔</span> {r}</div>"
    for r in lista_recs
])
checks_pdf_html = "".join([f"<div style='margin-bottom:4px; font-weight:600; color:#1e293b;'><span style='color:#dc2626;'>✔</span> {r}</div>" for r in lista_recs])

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

# 13. GENERADOR DE INFORME TÉCNICO REFERENCIAL PDF (HOJA A4 VERTICAL 100% COMPLETA SIN ABOUT:BLANK)
def disparar_pdf_infografia_una_hoja():
    fechas_js = json.dumps(df_diario["Fecha"].tolist())
    valores_js = json.dumps(df_diario["Pronóstico"].tolist())
    colores_js = json.dumps(colores_barras)
    logo_img_tag = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:58px; border-radius:8px;">' if LOGO_B64 else "<b>PERCET</b>"
    
    hora_peru = datetime.utcnow() - timedelta(hours=5)
    fecha_emision = hora_peru.strftime("%d/%m/%Y — %H:%M:%S")
    sello_inferior_pdf = T["pdf_audit_stamp"].format(rep_id=codigo_unico_id, fecha_hora=fecha_emision, lat=lat_actual, lon=lon_actual)
    
    max_chart_pdf = round(max(pico_max_dia * 1.28, umbral_critico * 1.45, 4.0), 1)
    color_dif_pdf = "#dc2626" if diferencia_umbral > 0 else "#16a34a"

    filas_1_7 = "".join([
        f"<tr><td>{r['Fecha']}</td><td>{r['Modelo Base']}</td><td><b>{r['Pronóstico']}</b></td><td>{r['Prob. Lluvia (%)']}%</td><td>{r['Temp. Máx (°C)']}°</td><td>{r['Viento Máx (km/h)']}</td></tr>"
        for _, r in df_diario.iloc[:7].iterrows()
    ])
    filas_8_14 = "".join([
        f"<tr><td>{r['Fecha']}</td><td>{r['Modelo Base']}</td><td><b>{r['Pronóstico']}</b></td><td>{r['Prob. Lluvia (%)']}%</td><td>{r['Temp. Máx (°C)']}°</td><td>{r['Viento Máx (km/h)']}</td></tr>"
        for _, r in df_diario.iloc[7:14].iterrows()
    ])

    html_infografia = f"""
    <script>
    function abrirInfografiaPDF() {{
        var win = window.open("", "_blank", "width=1100,height=900");
        var fechas = {fechas_js};
        var valores = {valores_js};
        var colores = {colores_js};
        var maxVal = {max_chart_pdf};
        
        var chartTop = 28;
        var chartBottom = 182;
        var chartHeight = chartBottom - chartTop;
        var barrasSvg = "";

        for (var i = 0; i < fechas.length; i++) {{
            var x = 35 + i * 48;
            var h = (valores[i] / maxVal) * chartHeight;
            var y = chartBottom - h;
            var op = (i < 7) ? "1.0" : "0.68";
            barrasSvg += '<rect x="' + x + '" y="' + y + '" width="30" height="' + h + '" fill="' + colores[i] + '" fill-opacity="' + op + '" rx="3.5"/>';
            barrasSvg += '<text x="' + (x + 15) + '" y="' + (y - 6) + '" font-size="10" font-weight="800" text-anchor="middle" fill="#020b1e">' + valores[i] + '</text>';
            barrasSvg += '<text x="' + (x + 15) + '" y="200" font-size="9.2" font-weight="700" text-anchor="middle" fill="#334155">' + fechas[i] + '</text>';
        }}
        var yUmbral = chartBottom - ({umbral_critico} / maxVal) * chartHeight;
        var xDivisor = 35 + 6 * 48 + 39;

        var contenido = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>{codigo_unico_id}_{nombre_proyecto}</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">
            <style>
                @page {{ size: A4 portrait; margin: 0mm; }}
                * {{ box-sizing: border-box; font-family: 'Montserrat', sans-serif; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
                html, body {{ width: 210mm; height: 297mm; margin: 0; padding: 8mm 9mm; background: #ffffff; color: #020b1e; }}
                .page {{ width: 100%; height: 281mm; border: 2.2px solid #042454; border-radius: 12px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #020b1e 0%, #042454 100%); color: white; padding: 12px 18px; border-radius: 9px; border-bottom: 4px solid #00b4d8; }}
                .sec-block {{ display: flex; flex-direction: column; }}
                .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
                .card {{ border: 1px solid #cbd5e1; border-top: 4px solid #042454; border-radius: 8px; padding: 10px 12px; background: #f8fafc; text-align: center; }}
                .card-title {{ font-size: 8.5px; font-weight: 800; color: #475569; text-transform: uppercase; text-align: center; }}
                .card-val {{ font-size: 17px; font-weight: 900; color: #020b1e; margin: 4px 0; }}
                .sec-title {{ font-size: 10px; font-weight: 800; color: #042454; text-transform: uppercase; border-bottom: 1.8px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 7px; letter-spacing: 0.3px; }}
                .chart-box {{ border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 10px 6px 10px; text-align: center; background: #ffffff; }}
                .alert-box {{ background: {bg_banner_pdf}; border: 1.5px solid {border_banner_pdf}; border-radius: 9px; padding: 12px 16px; display: grid; grid-template-columns: 1.12fr 1.28fr; gap: 14px; align-items: center; }}
                .tables-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 8.4px; }}
                th {{ background: #042454; color: white; padding: 5.5px 3px; text-transform: uppercase; font-weight: 700; font-size: 7.2px; }}
                td {{ border-bottom: 1px solid #cbd5e1; padding: 5.2px 3px; text-align: center; font-weight: 600; }}
                .sub-tbl-hdr {{ background: #e0f2fe; color: #0369a1; font-size: 8.2px; font-weight: 800; text-align: center; padding: 4.5px; border-radius: 5px 5px 0 0; border: 1px solid #bae6fd; border-bottom: none; }}
                .bottom-group {{ display: flex; flex-direction: column; gap: 6px; }}
                .sig-bar {{ background: #f8fafc; color: #020b1e; font-size: 8.2px; padding: 9px 12px; border: 1.2px dashed #64748b; border-radius: 6px; text-align: center; }}
                .footer {{ font-size: 7.4px; color: #475569; background: #f1f5f9; padding: 7px 11px; border-radius: 6px 6px 0 0; line-height: 1.35; border: 1px solid #cbd5e1; border-bottom: none; }}
                .audit-bar {{ background: #020b1e; color: #ffffff; font-size: 7.6px; padding: 6.5px 12px; border-radius: 0 0 6px 6px; text-align: center; letter-spacing: 0.3px; border-top: 2.5px solid #00b4d8; }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="header">
                    <div style="display:flex; align-items:center; gap:14px;">
                        {logo_img_tag}
                        <div>
                            <div style="font-size:13.2px; font-weight:900; letter-spacing:0.4px;">{T['pdf_report_main_title']}</div>
                            <div style="font-size:9.5px; color:#38bdf8; font-weight:700; margin-top:3px;">
                                {T['header_client']} {nombre_proyecto} &nbsp;|&nbsp; {nombre_rubro_activo} &nbsp;|&nbsp; ID: {codigo_unico_id}
                            </div>
                            <div style="font-size:8.4px; color:#cbd5e1; margin-top:3px;">
                                📍 Lat: {lat_actual}, Lon: {lon_actual} &nbsp;|&nbsp; ⚙️ {modo_eval_corto} &nbsp;|&nbsp; 🕒 {fecha_emision} hrs (UTC-5)
                            </div>
                        </div>
                    </div>
                </div>

                <div class="sec-block">
                    <div class="sec-title">{T['pdf_sec1_title']}</div>
                    <div class="grid-3">
                        <div class="card">
                            <div class="card-title">{T['pill_peak']} ({fecha_pico})</div>
                            <div class="card-val" style="color:#dc2626;">{pico_max_dia:.1f} {UNIT_MM}</div>
                            <div style="font-size:8.2px; font-weight:700; color:#475569;">{T['kpi1_sub'].format(acum=lluvia_acumulada, base_acum=lluvia_base_acum)}</div>
                        </div>
                        <div class="card">
                            <div class="card-title">{T['pill_thresh']} / {etiqueta_dif}</div>
                            <div class="card-val">{umbral_critico:.1f} {UNIT_MM} <span style="font-size:12px; color:{color_dif_pdf};">({signo_dif})</span></div>
                            <div style="font-size:8.2px; font-weight:700; color:#475569;">{T['pill_days']}: {dias_criticos} {T['day_unit']}</div>
                        </div>
                        <div class="card">
                            <div class="card-title">{T['kpi2_title']} & {T['pdf_quebradas']}</div>
                            <div class="card-val">{humedad_txt}% HR</div>
                            <div style="font-size:8.2px; font-weight:700; color:#020b1e;">{estado_quebrada}</div>
                        </div>
                    </div>
                </div>

                <div class="sec-block">
                    <div class="sec-title">{T['pdf_sec2_title']}</div>
                    <div class="chart-box">
                        <svg viewBox="0 0 740 210" width="100%" height="195">
                            <line x1="22" y1="182" x2="725" y2="182" stroke="#94a3b8" stroke-width="1.5"/>
                            ` + barrasSvg + `
                            <line x1="` + xDivisor + `" y1="12" x2="` + xDivisor + `" y2="182" stroke="#64748b" stroke-width="1.6" stroke-dasharray="4,4"/>
                            <text x="` + (xDivisor - 8) + `" y="16" font-size="8.5" font-weight="800" fill="#042454" text-anchor="end">{T['chart_div_left']}</text>
                            <text x="` + (xDivisor + 8) + `" y="16" font-size="8.5" font-weight="800" fill="#475569" text-anchor="start">{T['chart_div_right']}</text>
                            <line x1="22" y1="` + yUmbral + `" x2="725" y2="` + yUmbral + `" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4"/>
                            <rect x="585" y="2" width="135" height="16" fill="#dc2626" rx="3"/>
                            <text x="652.5" y="13" font-size="8.8" font-weight="800" fill="#ffffff" text-anchor="middle">{T['thresh_tag'].format(umbral=f'{umbral_critico:.1f}')}</text>
                        </svg>
                    </div>
                </div>

                <div class="sec-block">
                    <div class="sec-title">{T['pdf_sec3_title']}</div>
                    <div class="alert-box">
                        <div>
                            <div style="font-size:10px; font-weight:900; color:{color_titulo_pdf}; margin-bottom:3px;">{badge_txt}</div>
                            <div style="font-size:9.5px; font-weight:800; margin-bottom:3px;">{nombre_rubro_activo}</div>
                            <div style="font-size:8.4px; color:#334155; line-height:1.4;">{desc_txt}</div>
                        </div>
                        <div>
                            <div style="font-size:8.8px; font-weight:800; color:#042454; margin-bottom:4px;">{T['rec_title']}:</div>
                            <div style="font-size:8.2px; line-height:1.4;">{checks_pdf_html}</div>
                        </div>
                    </div>
                </div>

                <div class="sec-block">
                    <div class="sec-title">{T['pdf_sec4_title']}</div>
                    <div class="tables-2col">
                        <div>
                            <div class="sub-tbl-hdr">{T['pdf_days_1_7']}</div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>{T['pdf_col_date']}</th>
                                        <th>{T['pdf_col_base']}</th>
                                        <th>{T['pdf_col_fcst']}</th>
                                        <th>{T['pdf_col_prob']}</th>
                                        <th>{T['pdf_col_tmax']}</th>
                                        <th>{T['pdf_col_wind']}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filas_1_7}
                                </tbody>
                            </table>
                        </div>
                        <div>
                            <div class="sub-tbl-hdr">{T['pdf_days_8_14']}</div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>{T['pdf_col_date']}</th>
                                        <th>{T['pdf_col_base']}</th>
                                        <th>{T['pdf_col_fcst']}</th>
                                        <th>{T['pdf_col_prob']}</th>
                                        <th>{T['pdf_col_tmax']}</th>
                                        <th>{T['pdf_col_wind']}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filas_8_14}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="bottom-group">
                    <div class="sig-bar">
                        {T['pdf_sig_box']}
                    </div>
                    <div>
                        <div class="footer">
                            {T['disclaimer']}
                        </div>
                        <div class="audit-bar">
                            {sello_inferior_pdf}
                        </div>
                    </div>
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

if st.session_state.disparar_pdf_ahora:
    st.session_state.disparar_pdf_ahora = False
    disparar_pdf_infografia_una_hoja()

cabecera_csv = (
    f"# PERCET GeoRisk - Informe Tecnico Referencial | ID: {codigo_unico_id}\n"
    f"# Proyecto: {nombre_proyecto} | Rubro: {nombre_rubro_activo} | Umbral: {umbral_critico} {UNIT_MM}\n"
    f"# Coordenada: Lat {lat_actual}, Lon {lon_actual} | Fuente: Weather data by Open-Meteo.com (CC BY 4.0)\n"
)
csv_data = (cabecera_csv + df_mostrar.to_csv(index=False)).encode('utf-8-sig')

estado_pack_html = (
    f'<span style="color:#16a34a;">{T["pack_unlocked_txt"].format(codigo=st.session_state.codigo_activo_pack)}</span>'
    if st.session_state.pack_desbloqueado
    else f'<span>🔒 {T["pack_badge_txt"]}</span>'
)
st.markdown(f'<div class="pack-status-bar">{estado_pack_html}</div>', unsafe_allow_html=True)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    if st.session_state.pack_desbloqueado:
        st.download_button(
            label=T["dl_csv"],
            data=csv_data,
            file_name=f"{codigo_unico_id}_PERCET_GeoRisk_14D_{nombre_proyecto}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        if st.button(T["dl_csv"], key="btn_pack_csv", use_container_width=True):
            st.session_state.accion_pendiente_pack = "csv"
            mostrar_modal_pago_pack()

with col_dl2:
    if st.session_state.pack_desbloqueado:
        if st.button(T["dl_pdf"], key="btn_pack_pdf_ok", use_container_width=True):
            disparar_pdf_infografia_una_hoja()
    else:
        if st.button(T["dl_pdf"], key="btn_pack_pdf_lock", use_container_width=True):
            st.session_state.accion_pendiente_pack = "pdf"
            mostrar_modal_pago_pack()

# 14. DESPLEGABLE TÉCNICO (14 DÍAS REALES + METODOLOGÍA Y ORIGEN DEL MODELO ML)
with st.expander(T["exp_title"]):
    st.markdown(f"""
{T['ml_bullet_1']}
{T['ml_bullet_2'].format(presion=presion_txt)}
    """)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# 15. DISCLAIMER Y BANNER B2B CON DOS ACCIONES CLARAS Y COMPLEMENTARIAS
st.markdown(f'<div class="legal-disclaimer">{T["disclaimer"]}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="b2b-banner">
    <div class="b2b-banner-title">{T['b2b_title']}</div>
    <div class="b2b_banner-sub">{T['b2b_sub']}</div>
</div>
""", unsafe_allow_html=True)

b1, b2, b3, b4 = st.columns([0.3, 2.2, 2.2, 0.3])
with b2:
    if st.button(T['btn_quote'], use_container_width=True):
        mostrar_modal_cotizacion()
with b3:
    if st.button(T["btn_feedback"], use_container_width=True):
        mostrar_modal_sugerencias()
