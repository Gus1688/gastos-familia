import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="wide")

# --- 2. ESTILO VISUAL REFORZADO (CONTRASTE ALTO) ---
st.markdown("""
    <style>
    /* Fondo principal gris claro */
    .stApp { 
        background-color: #f8f9fa !important; 
    }
    
    /* Forzar que los textos principales sean oscuros */
    h1, h2, h3, p, b, span { 
        color: #1a1a1a !important; 
    }

    /* Tarjetas de métricas con fondo blanco sólido y borde */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* Ajuste de etiquetas de métricas */
    [data-testid="stMetricLabel"] {
        color: #6c757d !important;
        font-weight: bold !important;
    }

    /* Botón con color llamativo */
    .stButton>button {
        width: 100%;
        background-color: #2b6cb0 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        height: 3em !important;
    }
    
    /* Sidebar con fondo un poco más oscuro para contraste */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #dee2e6;
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
        return response.status_code == 200
    except:
        return False

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("nuevo_gasto", clear_on_submit=True):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
        d = st.text_input("Nota")
        
        if st.form_submit_button("Registrar Gasto"):
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.balloons()
                    st.success("¡Guardado!")
                    st.cache_data.clear()
                    st.rerun()

# --- 5. CUERPO PRINCIPAL ---
st.title("🏡 Resumen Financiero Familiar")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    total_gastado = df_mes["Monto"].sum()
    presupuesto_total = sum(LIMITES.values())
    balance = presupuesto_total - total_gastado
    
    # MÉTRICAS CON COLOR FORZADO
    m1, m2, m3 = st.columns(3)
    m1.metric("Gasto Mes", f"${total_gastado:,.2f}")
    m2.metric("Presupuesto", f"${presupuesto_total:,.2f}")
    m3.metric("Balance Disponible", f"${balance:,.2f}")

    st.divider()

    col_izq, col_
