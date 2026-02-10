import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="wide")

# --- 2. ESTILO VISUAL SIMPLIFICADO Y LEGIBLE ---
st.markdown("""
    <style>
    /* Tarjetas de métricas con bordes definidos para que no se pierdan */
    div[data-testid="stMetric"] {
        border: 2px solid #4a5568 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        background-color: rgba(128, 128, 128, 0.05) !important;
    }
    
    /* Forzar que el texto de las métricas sea siempre visible */
    [data-testid="stMetricValue"] {
        font-weight: bold !important;
    }

    /* Botones con color sólido y texto blanco garantizado */
    .stButton>button {
        width: 100%;
        background-color: #3182ce !important;
        color: #ffffff !important;
        border: 2px solid #2b6cb0 !important;
        font-weight: bold !important;
        height: 3.5em !important;
    }

    /* Estilo para las barras de progreso */
    .stProgress > div > div > div > div {
        background-color: #3182ce !important;
    }
    
    /* Títulos con margen para evitar amontonamiento */
    h1, h2, h3 {
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE DATOS ---
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
SUBMIT_URL = f"https://forms.google.com/forms/d/e/{FORM_ID}/formResponse"

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
        if response.status_code != 200:
            st.error(f"Error de Google: {response.status_code}") # Esto te dirá si la URL falla
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False
    #try:
        #response = requests.post(SUBMIT_URL, data=payload)
        #return response.status_code == 200
    #except:
        #return False#

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.header("📝 Registrar Gasto")
    with st.form("nuevo_gasto", clear_on_submit=True):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Método de Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
        d = st.text_input("Nota / Descripción")
        
        if st.form_submit_button("GUARDAR GASTO"):
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.balloons()
                    st.success("¡Gasto Guardado!")
                    st.cache_data.clear()
                    st.rerun()

# --- 5. CUERPO PRINCIPAL ---
st.title("🏡 Finanzas Gustavo & Fabiola")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    total_gastado = df_mes["Monto"].sum()
    presupuesto_total = sum(LIMITES.values())
    balance = presupuesto_total - total_gastado
    
    # MÉTRICAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Gasto Total Mes", f"${total_gastado:,.2f}")
    m2.metric("Presupuesto Total", f"${presupuesto_total:,.2f}")
    m3.metric("Balance Restante", f"${balance:,.2f}", delta=f"${balance}", delta_color="normal")

    st.divider()

    col_izq, col_der = st.columns([1.2, 1])

    with col_izq:
        st.subheader("📊 Límites Mensuales")
        gastos_cat = df_mes.groupby("Categoría")["Monto"].sum()
        for cat, limite in LIMITES.items():
            gastado = gastos_cat.get(cat, 0)
            progreso = min(gastado / limite, 1.0)
            st.write(f"**{cat}**")
            st.progress(progreso)
            st.caption(f"${gastado:,.2f} / ${limite:,.2f}")

    with col_der:
        st.subheader("🍕 Distribución")
        if total_gastado > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(
                margin=dict(t=30, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📑 Historial de Movimientos")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

except Exception as e:
    st.info("Cargando base de datos...")

