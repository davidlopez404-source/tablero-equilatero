import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decimal import Decimal, getcontext
import math

# ==========================================
# CONFIGURACIÓN Y BRANDING (Equilátero)
# ==========================================
st.set_page_config(
    page_title="Equilátero | Tablero de Viabilidad",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema Visual (CSS Inject)
# Background: #0A1F1A (Base)
# Cards: #060F0D (Tarjetas y Sidebar)
# Accents: #00FFCC (Acentos neón)
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #0A1F1A;
        color: #FFFFFF;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #060F0D !important;
        border-right: 1px solid #00FFCC22;
    }
    
    /* Headers and Text */
    h1, h2, h3, p, label, .stMarkdown {
        color: #E0E0E0 !important;
    }
    h1 {
        color: #00FFCC !important;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Inputs y Controles */
    .stNumberInput input, .stTextInput input, .stSelectbox select {
        background-color: #0A1F1A !important;
        color: #00FFCC !important;
        border: 1px solid #00FFCC44 !important;
        border-radius: 4px;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border: 1px solid #00FFCC !important;
        box-shadow: 0 0 5px #00FFCC55;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: transparent !important;
        color: #00FFCC !important;
        border: 2px solid #00FFCC !important;
        border-radius: 8px !important;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00FFCC !important;
        color: #060F0D !important;
        box-shadow: 0 0 15px #00FFCC88;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00FFCC !important;
        font-weight: 900;
    }
    [data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Radio Buttons (Segmented Controls) */
    .stRadio [role="radiogroup"] {
        background-color: #060F0D;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #00FFCC33;
    }
    .stRadio label {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo en el header (Placeholder usando HTML para layout)
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #00FFCC; font-size: 2.5rem; margin:0;">EQUILÁTERO</h1>
    <p style="color: #00FFCC; opacity: 0.6; font-size: 0.8rem; letter-spacing: 2px; margin:0;">FINANCIAL ENGINE</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# GESTIÓN DE ESTADO (Fase 1 y 2)
# ==========================================
# Inicialización de variables con Benchmarks por defecto (Template SaaS)
defaults = {
    "template": "SaaS B2B",
    "tam_volumen": 100000,
    "sam_filtro_porcentaje": 0.20,
    "som_penetracion_porcentaje": 0.05,
    "precio_basico": 99.0,
    "precio_pro": 299.0,
    "dist_basico": 0.70,
    "dist_pro": 0.30,
    "presupuesto_marketing": 5000.0,
    "trafico_leads": 10000,
    "tasa_conversion": 0.02,
    "churn_rate": 0.05,
    "capital_semilla": 100000.0,
    "capex": 20000.0,
    "opex_mensual": 15000.0,
    "cogs_unitario": 5.0,
    "pasarela_pago": 0.03
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def load_template():
    t = st.session_state.template_selector
    st.session_state.template = t
    if t == "SaaS B2B":
        st.session_state.update({
            "tasa_conversion": 0.02, "churn_rate": 0.05, "cogs_unitario": 5.0, "pasarela_pago": 0.03, "precio_basico": 99.0, "precio_pro": 299.0
        })
    elif t == "E-commerce D2C":
        st.session_state.update({
            "tasa_conversion": 0.03, "churn_rate": 0.0, "cogs_unitario": 40.0, "pasarela_pago": 0.05, "precio_basico": 80.0, "precio_pro": 150.0
        })
    elif t == "Agencia / Servicios":
        st.session_state.update({
            "tasa_conversion": 0.01, "churn_rate": 0.10, "cogs_unitario": 0.0, "pasarela_pago": 0.0, "precio_basico": 1500.0, "precio_pro": 5000.0
        })

# ==========================================
# SIDEBAR: WIZARD DE INPUTS (Fase 1 y 2)
# ==========================================
st.sidebar.markdown("### 0. Plantilla Base")
st.sidebar.selectbox("Arquetipo de Negocio", ["SaaS B2B", "E-commerce D2C", "Agencia / Servicios"], key="template_selector", on_change=load_template)

st.sidebar.markdown("---")
st.sidebar.markdown("### 1. Mercado (El Límite)")
st.session_state.tam_volumen = st.sidebar.number_input("TAM (Total Absoluto)", min_value=1, value=st.session_state.tam_volumen, step=1000, help="Número total de clientes potenciales.")
st.session_state.sam_filtro_porcentaje = st.sidebar.number_input("SAM (Filtro Operativo %)", min_value=0.0, max_value=1.0, value=st.session_state.sam_filtro_porcentaje, step=0.01)
st.session_state.som_penetracion_porcentaje = st.sidebar.number_input("SOM (Penetración Meta %)", min_value=0.0, max_value=1.0, value=st.session_state.som_penetracion_porcentaje, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Monetización")
col1, col2 = st.sidebar.columns(2)
st.session_state.precio_basico = col1.number_input("Precio Básico ($)", min_value=0.0, value=float(st.session_state.precio_basico))
st.session_state.dist_basico = col2.number_input("Adopción Básico (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.dist_basico))
col3, col4 = st.sidebar.columns(2)
st.session_state.precio_pro = col3.number_input("Precio Pro ($)", min_value=0.0, value=float(st.session_state.precio_pro))
st.session_state.dist_pro = col4.number_input("Adopción Pro (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.dist_pro))

# Sanity Check: Distribución de planes
if abs((st.session_state.dist_basico + st.session_state.dist_pro) - 1.0) > 0.001:
    st.sidebar.error("⚠️ La adopción de planes debe sumar exactamente 1.0 (100%)")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. Tracción y Retención")
st.session_state.presupuesto_marketing = st.sidebar.number_input("Ppto. Marketing Mensual ($)", min_value=0.0, value=float(st.session_state.presupuesto_marketing))
st.session_state.trafico_leads = st.sidebar.number_input("Leads / Tráfico Mensual", min_value=0, value=int(st.session_state.trafico_leads))
st.session_state.tasa_conversion = st.sidebar.number_input("Conversión (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.tasa_conversion), help="💡 Benchmark: SaaS B2B suele ser 1%-3%")
st.session_state.churn_rate = st.sidebar.number_input("Churn Mensual (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.churn_rate), help="💡 Benchmark: B2C masivo 5-7%, B2B 1-3%")

# CAC Calculado Bloqueado
nuevos_clientes = st.session_state.trafico_leads * st.session_state.tasa_conversion
cac_implicito = (st.session_state.presupuesto_marketing / nuevos_clientes) if nuevos_clientes > 0 else 0.0
st.sidebar.text_input("CAC Implícito Calculado ($)", value=f"${cac_implicito:,.2f}", disabled=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 4. Estructura de Costos")
st.session_state.capital_semilla = st.sidebar.number_input("Capital Semilla (Liquidez $)", min_value=0.0, value=float(st.session_state.capital_semilla))
st.session_state.capex = st.sidebar.number_input("CAPEX Inicial ($)", min_value=0.0, value=float(st.session_state.capex))
st.session_state.opex_mensual = st.sidebar.number_input("OPEX Fijo Mensual ($)", min_value=0.0, value=float(st.session_state.opex_mensual))
st.session_state.cogs_unitario = st.sidebar.number_input("COGS Unitario Fijo ($)", min_value=0.0, value=float(st.session_state.cogs_unitario))
st.session_state.pasarela_pago = st.sidebar.number_input("Costo Pasarela (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.pasarela_pago))

# ==========================================
# MAIN AREA: CONTROLES Y MOTOR (Fase 3 y 4)
# ==========================================
st.markdown("## Análisis de Estrés y Proyección a 24 Meses")

# Selector de Escenarios
escenario = st.radio("Control de Sensibilidad (Stress Test)", ["Escenario Base", "Escenario Optimista (Happy Path)", "Escenario Pesimista (Estrés)"], horizontal=True)

# Copiar inputs al contexto local para aplicar multiplicadores sin pisar el estado (Fase 2)
v = dict(st.session_state)

if escenario == "Escenario Optimista (Happy Path)":
    v['tasa_conversion'] = min(v['tasa_conversion'] * 1.20, 1.0)
    v['churn_rate'] = v['churn_rate'] * 0.80
    v['cogs_unitario'] = v['cogs_unitario'] * 0.90
elif escenario == "Escenario Pesimista (Estrés)":
    v['tasa_conversion'] = v['tasa_conversion'] * 0.70
    v['churn_rate'] = min(v['churn_rate'] * 1.50, 1.0)
    v['trafico_leads'] = v['trafico_leads'] * 0.80
    v['opex_mensual'] = v['opex_mensual'] * 1.20

# ---- MOTOR FINANCIERO (Fase 3) ----
# A. Mercado
tam = v['tam_volumen']
sam = tam * v['sam_filtro_porcentaje']
som_absoluto = sam * v['som_penetracion_porcentaje']

# B. Tracción
nuevos_clientes_mensuales = v['trafico_leads'] * v['tasa_conversion']
cac = (v['presupuesto_marketing'] / nuevos_clientes_mensuales) if nuevos_clientes_mensuales > 0 else 0

# Ponderación ARPU
arpu = (v['precio_basico'] * v['dist_basico']) + (v['precio_pro'] * v['dist_pro'])

# LTV
ltv = (arpu / v['churn_rate']) if v['churn_rate'] > 0 else (arpu * 24) # Tope 24m si no hay churn

# Inicialización Bucle
clientes_activos = 0
total_clientes_historicos = 0
caja_disponible = v['capital_semilla'] - v['capex']

meses_data = []
break_even_month = None
cash_burn_initial = 0
runway_final = 0
quiebra_marcada = False

for mes in range(1, 25):
    # Freno SOM
    total_clientes_historicos += nuevos_clientes_mensuales
    if total_clientes_historicos >= som_absoluto:
        nuevos_mensuales = 0
    else:
        nuevos_mensuales = nuevos_clientes_mensuales
        
    # Cohortes
    clientes_activos = (clientes_activos * (1.0 - v['churn_rate'])) + nuevos_mensuales
    
    # P&L
    mrr = clientes_activos * arpu
    cogs_totales = (clientes_activos * v['cogs_unitario']) + (mrr * v['pasarela_pago'])
    costos_totales = v['opex_mensual'] + cogs_totales + v['presupuesto_marketing']
    
    net_burn = mrr - costos_totales
    caja_disponible += net_burn
    
    # Track Break-even
    if net_burn > 0 and break_even_month is None:
        break_even_month = mes
        
    if break_even_month is None:
        cash_burn_initial += net_burn
        
    # Track Runway (Si no ha quebrado en el bucle)
    if not quiebra_marcada and net_burn < 0:
        if caja_disponible <= 0:
            runway_final = mes
            quiebra_marcada = True
            
    meses_data.append({
        "Mes": mes,
        "MRR": mrr,
        "Costos Totales": costos_totales,
        "Net Burn": net_burn,
        "Caja Disponible": caja_disponible,
        "Clientes Activos": clientes_activos
    })

df = pd.DataFrame(meses_data)

# Calculo de Runway si nunca quebramos pero seguimos quemando, usamos el mes 1 para estimar
if not quiebra_marcada:
    primer_mes_burn = df.iloc[0]['Net Burn']
    if primer_mes_burn < 0:
        runway_final = (v['capital_semilla'] - v['capex']) / abs(primer_mes_burn)
    else:
        runway_final = float('inf')

# ---- RENDERIZADO UI (Fase 4) ----
st.markdown("---")

# 1. KPIs
ratio_ltv_cac = (ltv / cac) if cac > 0 else 0
col1, col2, col3, col4 = st.columns(4)

# Formato Condicional LTV:CAC
if ratio_ltv_cac > 3:
    color_ratio = "🟢"
elif ratio_ltv_cac < 1:
    color_ratio = "🔴"
else:
    color_ratio = "🟡"

col1.metric("Ratio LTV:CAC", f"{color_ratio} {ratio_ltv_cac:.1f}x")

if runway_final == float('inf'):
    str_runway = "Infinito 🚀"
elif quiebra_marcada:
    str_runway = f"{runway_final} Meses 💀"
else:
    str_runway = f"{int(runway_final)} Meses"
col2.metric("Runway (Supervivencia)", str_runway)

str_be = f"Mes {break_even_month}" if break_even_month else "No se alcanza ⛔"
col3.metric("Break-even (Pto. Equilibrio)", str_be)

col4.metric("Cash Burn (Antes B.E.)", f"${cash_burn_initial:,.0f}")

st.markdown("---")

# 2. SANITY CHECKS (Alertas Educativas)
alertas = []
if total_clientes_historicos >= som_absoluto:
    st.error("🛑 **Alerta de Mercado (Saturación):** Tus clientes capturados superan el límite del SOM en el periodo. Estás asumiendo una captación irreal para tu cuota de mercado.")
if ltv < cac and cac > 0:
    st.error("🛑 **Alerta de Rentabilidad (Economía Unitaria Rota):** Tu LTV es menor a tu CAC. Estás pagando por trabajar. Cada cliente nuevo que entra acelera tu quiebra.")
if runway_final != float('inf') and runway_final < 6 and break_even_month is None:
    st.warning("⚠️ **Alerta de Liquidez (Riesgo Inminente):** Tu Runway es menor a 6 meses. Riesgo inminente de quiebra operativa. Necesitas levantar capital, aumentar precios o reducir OPEX drásticamente.")


# 3. GRÁFICO: EL VALLEY OF DEATH
fig = go.Figure()

# Línea de Costos (Roja)
fig.add_trace(go.Scatter(
    x=df['Mes'], y=df['Costos Totales'],
    mode='lines',
    line=dict(color='#FF3366', width=3),
    name='Costos Totales'
))

# Línea de MRR (Verde Neón)
fig.add_trace(go.Scatter(
    x=df['Mes'], y=df['MRR'],
    mode='lines',
    line=dict(color='#00FFCC', width=3),
    name='Ingresos (MRR)',
    fill='tonexty', # Sombrear área entre líneas
    fillcolor='rgba(255, 51, 102, 0.2)' # Color de Valley of death (rojo transparente)
))

# Ocultar fill donde MRR > Costos (Truco: trazar un área base o usar fill condicional no es directo en Scatter,
# pero en Plotly tonexty rellena hasta la traza anterior. Si la curva verde supera a la roja, el fill
# será del color definido. Lo ideal para aislar el Valley of Death:
# Lo manejamos trazando una línea cero, etc., pero para este MVP dejamos el sombreado de cruce estándar.

fig.update_layout(
    title='Proyección de Viabilidad: Valley of Death',
    plot_bgcolor='#060F0D',
    paper_bgcolor='#0A1F1A',
    font=dict(color='#E0E0E0'),
    xaxis=dict(title='Mes', showgrid=True, gridcolor='#00FFCC22'),
    yaxis=dict(title='USD ($)', showgrid=True, gridcolor='#00FFCC22'),
    hovermode="x unified",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# Data Table Opcional
with st.expander("Ver Datos Mes a Mes"):
    st.dataframe(df.style.format({
        "MRR": "${:,.2f}",
        "Costos Totales": "${:,.2f}",
        "Net Burn": "${:,.2f}",
        "Caja Disponible": "${:,.2f}",
        "Clientes Activos": "{:,.0f}"
    }), use_container_width=True)
