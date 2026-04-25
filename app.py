import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

# Logo en el header
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #00FFCC; font-size: 2.5rem; margin:0;">EQUILÁTERO</h1>
    <p style="color: #00FFCC; opacity: 0.6; font-size: 0.8rem; letter-spacing: 2px; margin:0;">FINANCIAL ENGINE</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR: WIZARD DE INPUTS
# ==========================================
st.sidebar.markdown("### 0. Tipo de negocio")
pago_recurrente = st.sidebar.radio("¿Tu cliente te paga de forma repetida? (suscripción, arriendo, membresía)", ["Sí", "No"], key="q_recurrencia")
producto_fisico = st.sidebar.radio("¿Lo que vendés se fabrica o se construye cada vez que alguien te compra? (máquina, mueble, consultoría por proyecto)", ["Sí", "No"], key="q_producto")

modelo = "Desconocido"
if pago_recurrente == "Sí" and producto_fisico == "No":
    modelo = "Recurrencia"
elif pago_recurrente == "Sí" and producto_fisico == "Sí":
    modelo = "Transacción de Volumen"
elif pago_recurrente == "No" and producto_fisico == "Sí":
    modelo = "Proyecto o Capital"
elif pago_recurrente == "No" and producto_fisico == "No":
    modelo = "Capacidad Humana"

st.sidebar.markdown(f"**Tipo detectado:** {modelo}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 1. Mercado")
tam = st.sidebar.number_input("TAM — número total de clientes potenciales", min_value=1, value=100000, step=1000)
sam = st.sidebar.number_input("SAM — clientes a los que puedes llegar operativamente", min_value=1, value=20000, step=1000)
som = st.sidebar.number_input("SOM — clientes meta realistamente", min_value=1, value=1000, step=100)

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Precios del mercado")
precio_min = st.sidebar.number_input("Precio mínimo del mercado (COP)", min_value=0.0, value=100000.0, step=10000.0)
precio_avg = st.sidebar.number_input("Precio promedio del mercado (COP)", min_value=0.0, value=200000.0, step=10000.0)
precio_max = st.sidebar.number_input("Precio máximo del mercado (COP)", min_value=0.0, value=300000.0, step=10000.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. Supuestos de penetración")
pen_pesimista = st.sidebar.number_input("Penetración pesimista (% del SOM)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
pen_base = st.sidebar.number_input("Penetración base (% del SOM)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
pen_optimista = st.sidebar.number_input("Penetración optimista (% del SOM)", min_value=0.0, max_value=100.0, value=100.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 4. Costos")
capex = st.sidebar.number_input("Costos de arranque — CAPEX (COP)", min_value=0.0, value=20000000.0, step=1000000.0)
opex = st.sidebar.number_input("Costos fijos mensuales — OPEX (COP)", min_value=0.0, value=5000000.0, step=500000.0)


# ==========================================
# MOTOR FINANCIERO
# ==========================================

# Costo Variable (Calculado en base al escenario base)
# Dividimos el OPEX mensual entre el número de clientes del escenario base (mensual)
clientes_totales_base = som * (pen_base / 100.0)
clientes_mensuales_base = clientes_totales_base / 24.0

costo_por_cliente = 0.0
if clientes_mensuales_base > 0:
    costo_por_cliente = opex / clientes_mensuales_base

def simular_escenario(precio, pen_perc):
    clientes_totales = som * (pen_perc / 100.0)
    nuevos_por_mes = clientes_totales / 24.0
    
    clientes_activos = 0
    caja_disponible = -capex # Arranca en -CAPEX
    
    meses_data = []
    break_even_month = None
    
    for mes in range(1, 25):
        if modelo == "Recurrencia":
            clientes_activos += nuevos_por_mes
        else:
            clientes_activos = nuevos_por_mes
            
        ingresos = clientes_activos * precio
        costos_variables = clientes_activos * costo_por_cliente
        costos_totales = opex + costos_variables
        
        net_burn = ingresos - costos_totales
        caja_disponible += net_burn
        
        if caja_disponible >= 0 and break_even_month is None:
            break_even_month = mes
            
        meses_data.append({
            "Mes": mes,
            "Ingresos": ingresos,
            "Costos Totales": costos_totales,
            "Caja Disponible": caja_disponible,
            "Clientes Activos": clientes_activos
        })
        
    return pd.DataFrame(meses_data), break_even_month

df_pesimista, be_pesimista = simular_escenario(precio_min, pen_pesimista)
df_base, be_base = simular_escenario(precio_avg, pen_base)
df_optimista, be_optimista = simular_escenario(precio_max, pen_optimista)

# ==========================================
# RENDERIZADO UI (Outputs)
# ==========================================
st.markdown("## Análisis de Viabilidad a 24 Meses")

# OUTPUT 1: Gráfica de caja disponible a 24 meses
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_pesimista['Mes'], y=df_pesimista['Caja Disponible'],
    mode='lines', line=dict(color='#FF3366', width=2), name='Pesimista'
))

fig.add_trace(go.Scatter(
    x=df_base['Mes'], y=df_base['Caja Disponible'],
    mode='lines', line=dict(color='#FFD700', width=3), name='Base'
))

fig.add_trace(go.Scatter(
    x=df_optimista['Mes'], y=df_optimista['Caja Disponible'],
    mode='lines', line=dict(color='#39FF14', width=3), name='Optimista'
))

fig.add_hline(y=0, line_dash="dash", line_color="#A0A0A0", annotation_text="Punto de Equilibrio ($0)")

fig.update_layout(
    title='Proyección de Caja Disponible Acumulada',
    plot_bgcolor='#060F0D',
    paper_bgcolor='#0A1F1A',
    font=dict(color='#E0E0E0'),
    xaxis=dict(title='Mes', showgrid=True, gridcolor='rgba(0, 255, 204, 0.13)'),
    yaxis=dict(title='Caja Disponible (COP)', showgrid=True, gridcolor='rgba(0, 255, 204, 0.13)'),
    hovermode="x unified",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

# OUTPUT 2: Semáforo de viabilidad
with col1:
    if be_base is None:
        color = "🔴"
        mensaje = "Rojo: El proyecto no logra recuperar la inversión inicial (CAPEX) en los primeros 24 meses bajo el escenario base. Requiere ajustes en precios, reducción de costos o mayor penetración."
    elif be_base <= 18:
        color = "🟢"
        mensaje = f"Verde: Proyecto viable. El punto de equilibrio se alcanza en el mes {be_base}, es decir, antes de los 18 meses, lo que representa un tiempo de recuperación ideal."
    else:
        color = "🟡"
        mensaje = f"Amarillo: Viabilidad moderada. El punto de equilibrio se alcanza en el mes {be_base}. Esto significa que tomará entre 18 y 24 meses recuperar la inversión inicial."
        
    st.markdown(f"### Semáforo de Viabilidad")
    st.info(f"{color} **{mensaje}**")

# OUTPUT 3: Indicador clave según el tipo de negocio
with col2:
    st.markdown("### Indicador Clave de tu Modelo")
    if modelo == "Recurrencia":
        st.metric("Ingreso vs Costo (Mensual por Cliente)", f"Ingreso: ${precio_avg:,.0f}", f"Costo: ${costo_por_cliente:,.0f}", delta_color="off")
    elif modelo == "Transacción de Volumen":
        st.metric("Ingreso vs Costo (Por Cliente)", f"Ingreso: ${precio_avg:,.0f}", f"Costo: ${costo_por_cliente:,.0f}", delta_color="off")
    elif modelo == "Proyecto o Capital":
        st.metric("Valor del Contrato vs Costo de Operación", f"Contrato: ${precio_avg:,.0f}", f"Costo Mensual: ${opex:,.0f}", delta_color="off")
    elif modelo == "Capacidad Humana":
        st.metric("Precio vs Costo (Por Cliente)", f"Precio: ${precio_avg:,.0f}", f"Costo: ${costo_por_cliente:,.0f}", delta_color="off")

st.markdown("---")

# Expander de datos mes a mes al final
with st.expander("Ver Datos Mes a Mes (Escenario Base)"):
    st.dataframe(df_base.style.format({
        "Ingresos": "${:,.0f}",
        "Costos Totales": "${:,.0f}",
        "Caja Disponible": "${:,.0f}",
        "Clientes Activos": "{:,.1f}"
    }), use_container_width=True)
