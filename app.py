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
# SIDEBAR: WIZARD DE INPUTS
# ==========================================
st.sidebar.markdown("### 0. Lógica de Negocio")
pago_recurrente = st.sidebar.radio("¿El cliente te paga más de una vez?", ["Sí", "No"], key="q_recurrencia")
producto_fisico = st.sidebar.radio("¿Vendes un producto físico o un entregable único de alto valor?", ["Sí", "No"], key="q_producto")

modelo = "Desconocido"
if pago_recurrente == "Sí" and producto_fisico == "No":
    modelo = "Recurrencia"
elif pago_recurrente == "Sí" and producto_fisico == "Sí":
    modelo = "Transacción de Volumen"
elif pago_recurrente == "No" and producto_fisico == "Sí":
    modelo = "Proyecto o Capital"
elif pago_recurrente == "No" and producto_fisico == "No":
    modelo = "Capacidad Humana"

st.sidebar.info(f"**Modelo:** {modelo}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 1. Mercado (El Límite)")
tam_volumen = st.sidebar.number_input("TAM (Total Absoluto)", min_value=1, value=100000, step=1000, help="Número total de clientes potenciales.")
sam_filtro_porcentaje = st.sidebar.number_input("SAM (Filtro Operativo %)", min_value=0.0, max_value=1.0, value=0.20, step=0.01)
som_penetracion_porcentaje = st.sidebar.number_input("SOM (Penetración Meta %)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Monetización")
precio_min = st.sidebar.number_input("Precio mínimo del mercado ($)", min_value=0.0, value=50.0)
precio_avg = st.sidebar.number_input("Precio promedio del mercado ($)", min_value=0.0, value=100.0)
precio_max = st.sidebar.number_input("Precio máximo del mercado ($)", min_value=0.0, value=200.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. Tracción")
nuevos_clientes_mes = st.sidebar.number_input("Clientes nuevos por mes que estimas capturar", min_value=0, value=50)

st.sidebar.markdown("---")
st.sidebar.markdown("### 4. Costos")
capex = st.sidebar.number_input("Costos de arranque (CAPEX) ($)", min_value=0.0, value=20000.0)
opex = st.sidebar.number_input("Costos fijos mensuales (OPEX) ($)", min_value=0.0, value=5000.0)

costo_unitario = 0.0
costo_hora = 0.0
if modelo == "Transacción de Volumen":
    costo_unitario = st.sidebar.number_input("Costo unitario del producto ($)", min_value=0.0, value=20.0)
elif modelo == "Capacidad Humana":
    costo_hora = st.sidebar.number_input("Costo por hora de tu equipo ($)", min_value=0.0, value=15.0)

# ==========================================
# MOTOR FINANCIERO (3 Escenarios)
# ==========================================
tam = tam_volumen
sam = tam * sam_filtro_porcentaje

def simular_escenario(precio, som_perc, nuevos_por_mes):
    som_absoluto = sam * som_perc
    
    clientes_activos = 0
    total_clientes_historicos = 0
    caja_disponible = -capex # Arranca en -CAPEX
    
    meses_data = []
    break_even_month = None
    
    for mes in range(1, 25):
        if total_clientes_historicos >= som_absoluto:
            nuevos_este_mes = 0
        else:
            nuevos_este_mes = min(nuevos_por_mes, som_absoluto - total_clientes_historicos)
            
        total_clientes_historicos += nuevos_este_mes
        
        if modelo == "Recurrencia":
            clientes_activos += nuevos_este_mes
        elif modelo in ["Transacción de Volumen", "Proyecto o Capital", "Capacidad Humana"]:
            clientes_activos = nuevos_este_mes
            
        mrr = clientes_activos * precio
        
        costos_variables = 0
        if modelo == "Transacción de Volumen":
            costos_variables = clientes_activos * costo_unitario
        elif modelo == "Capacidad Humana":
            costos_variables = clientes_activos * costo_hora
            
        costos_totales = opex + costos_variables
        net_burn = mrr - costos_totales
        caja_disponible += net_burn
        
        if caja_disponible >= 0 and break_even_month is None:
            break_even_month = mes
            
        meses_data.append({
            "Mes": mes,
            "Ingresos": mrr,
            "Costos Totales": costos_totales,
            "Caja Disponible": caja_disponible,
            "Clientes Activos": clientes_activos
        })
        
    return pd.DataFrame(meses_data), break_even_month

df_pesimista, be_pesimista = simular_escenario(precio_min, som_penetracion_porcentaje * 0.30, nuevos_clientes_mes)
df_base, be_base = simular_escenario(precio_avg, som_penetracion_porcentaje * 0.60, nuevos_clientes_mes)
df_optimista, be_optimista = simular_escenario(precio_max, som_penetracion_porcentaje * 1.0, nuevos_clientes_mes)

# ==========================================
# RENDERIZADO UI (Outputs)
# ==========================================
st.markdown("## Análisis de Viabilidad a 24 Meses")

col1, col2 = st.columns(2)

# Output 2: Semáforo de Viabilidad
with col1:
    if be_base is None:
        color = "🔴"
        mensaje = "Rojo (No se alcanza)"
    elif be_base <= 18:
        color = "🟢"
        mensaje = f"Verde (Mes {be_base})"
    else:
        color = "🟡"
        mensaje = f"Amarillo (Mes {be_base})"
        
    st.metric("Punto de Equilibrio (Escenario Base)", f"{color} {mensaje}")

# Output 3: Indicador Clave
with col2:
    if modelo == "Recurrencia":
        ltv = precio_avg * 24
        st.metric("Indicador Clave", f"LTV: ${ltv:,.2f} | CAC: N/A")
    elif modelo == "Transacción de Volumen":
        margen = precio_avg - costo_unitario
        st.metric("Margen por Unidad", f"${margen:,.2f}")
    elif modelo == "Proyecto o Capital":
        st.metric("Valor Contrato vs CAC", f"Valor: ${precio_avg:,.2f} | CAC: N/A")
    elif modelo == "Capacidad Humana":
        st.metric("Precio vs Costo (por hora/unidad)", f"Precio: ${precio_avg:,.2f} | Costo: ${costo_hora:,.2f}")

st.markdown("---")

# Output 1: Gráfica
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_pesimista['Mes'], y=df_pesimista['Caja Disponible'],
    mode='lines', line=dict(color='#FF3366', width=2, dash='dot'), name='Pesimista (Min)'
))

fig.add_trace(go.Scatter(
    x=df_base['Mes'], y=df_base['Caja Disponible'],
    mode='lines', line=dict(color='#00FFCC', width=4), name='Base (Avg)'
))

fig.add_trace(go.Scatter(
    x=df_optimista['Mes'], y=df_optimista['Caja Disponible'],
    mode='lines', line=dict(color='#33FF55', width=2, dash='dot'), name='Optimista (Max)'
))

fig.add_hline(y=0, line_dash="dash", line_color="#A0A0A0", annotation_text="Punto de Equilibrio ($0)")

fig.update_layout(
    title='Proyección de Caja Disponible Acumulada',
    plot_bgcolor='#060F0D',
    paper_bgcolor='#0A1F1A',
    font=dict(color='#E0E0E0'),
    xaxis=dict(title='Mes', showgrid=True, gridcolor='rgba(0, 255, 204, 0.13)'),
    yaxis=dict(title='Caja Disponible USD ($)', showgrid=True, gridcolor='rgba(0, 255, 204, 0.13)'),
    hovermode="x unified",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver Datos Mes a Mes (Escenario Base)"):
    st.dataframe(df_base.style.format({
        "Ingresos": "${:,.2f}",
        "Costos Totales": "${:,.2f}",
        "Caja Disponible": "${:,.2f}",
        "Clientes Activos": "{:,.0f}"
    }), use_container_width=True)
