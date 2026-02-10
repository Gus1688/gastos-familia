import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="wide")

# --- 2. ESTILO VISUAL REFORZADO (CONTRASTE TOTAL) ---
st.markdown("""
    <style>
    /* Fondo de la app: Gris muy claro para que no brille tanto */
    .stApp {
        background-color: #F0F2F5 !important;
    }

    /* Forzar color de texto en toda la app a Negro/Gris Oscuro */
    html, body, [class*="View"], p, div, label, h1, h2, h3 {
        color: #1A202C !important;
    }

    /* TARJETAS DE MÉTRICAS: Fondo blanco, letras negras y borde grueso */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    [data-testid="stMetricValue"] {
        color: #2D3748 !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #4A5568 !important;
    }

    /* BOTÓN DE GUARDAR: Azul Marino con Texto Blanco Brillante */
    .stButton>button {
        width: 100% !important;
        background-color: #1A365D !important; /* Azul muy oscuro */
        color: #FFFFFF !important; /* Blanco puro */
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2A4365 !important;
        border-color: #3182CE !important;
    }

    /* Estilo para las barras de progreso */
    .stProgress > div > div > div > div {
        background-color: #3182CE !important;
    }

    /* Ocultar elementos de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

LIMITES = {
    "🎓 Educacion": 1500.0,
    "⚡ Servicios": 321.0,
    "🛠️ Mantenimiento": 500.0,
    "🛡️ Seguros": 630.0,
    "📺 Suscripciones": 123.0,
    "🚗 Transporte": 350.0,
    "🏦 Prestamo": 5600.0,
    "⚖️ Impuestos": 150.0,
    "🛒 Comida+Super": 2500.0,
    "🍕 Salidas": 600.0,
    "🎁 Otros": 200.0
}

READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
SUBMIT_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

def enviar_a_google(fecha, cat, desc, monto, usuario, pago):
    payload = {
        "entry.1460713451": str(fecha),
        "entry.1410133594": cat,
        "entry.344685481": desc,
        "entry.324330457": str(monto),
        "entry.745504096": usuario,
        "entry.437144806": pago
    }
    try:
        response = requests.post(SUBMIT_URL, data=payload)
        return response.status_code < 400
    except:
        return False

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📝 Registrar Gasto")
    with st.form("nuevo_gasto", clear_on_submit=False):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
        d = st.text_input("Nota")
        
        submit = st.form_submit_button("GUARDAR GASTO")
        if submit:
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.success("✅ Guardado correctamente")
                    st.balloons()
                    st.cache_data.clear()
                else:
                    st.error("❌ Error al guardar. Revisa conexión.")
            else:
                st.warning("Escribe un monto.")

# --- 5. DASHBOARD ---
st.title("🏡 Finanzas Gustavo & Fabiola")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    gastado = df_mes["Monto"].sum()
    presupuesto = sum(LIMITES.values())
    disponible = presupuesto - gastado

    # MÉTRICAS EN TARJETAS BLANCAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Gasto Total", f"${gastado:,.2f}")
    m2.metric("Presupuesto", f"${presupuesto:,.2f}")
    m3.metric("Disponible", f"${disponible:,.2f}")

    st.markdown("---")

    col_izq, col_der = st.columns([1.2, 1])

    with col_izq:
        st.subheader("📊 Análisis por Categoría")
        gastos_cat = df_mes.groupby("Categoría")["Monto"].sum()
        for cat, lim in LIMITES.items():
            valor = gastos_cat.get(cat, 0)
            pct = min(valor / lim, 1.0)
            st.write(f"**{cat}** (${valor:,.2f} / ${lim:,.2f})")
            st.progress(pct)

    with col_der:
        st.subheader("🍕 Distribución")
        if gastado > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', hole=0.5)
            fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📑 Últimos Movimientos")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

except:
    st.info("Registra tu primer gasto para ver los gráficos.")
