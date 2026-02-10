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
    /* Forzar fondo claro para evitar conflictos de modo oscuro */
    .stApp { background-color: #f8f9fa !important; }
    
    /* Texto siempre oscuro */
    h1, h2, h3, p, b, span, label { color: #1a1a1a !important; }

    /* Tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #dee2e6 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* Botón de Guardar: Azul con letras blancas */
    .stButton>button {
        width: 100%;
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        border: none !important;
    }
    
    /* Ajustes para Google Sites */
    .block-container { padding-top: 1rem !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IDs Y LÍMITES ---
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

# URL Corregida a docs.google.com
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
        # Si el código es 200 o similar, fue exitoso
        if response.status_code < 400:
            return True
        else:
            st.error(f"Error de Google: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# --- 4. BARRA LATERAL (REGISTRO) ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    # clear_on_submit=False temporalmente para no perder datos si falla
    with st.form("nuevo_gasto", clear_on_submit=False):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
        d = st.text_input("Nota / Descripción")
        
        btn_guardar = st.form_submit_button("GUARDAR GASTO")
        
        if btn_guardar:
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.success("✅ ¡Gasto Guardado correctamente!")
                    st.balloons()
                    st.cache_data.clear()
                    # No usamos rerun para que veas el mensaje de éxito
                else:
                    st.error("❌ No se pudo guardar. Revisa los IDs.")
            else:
                st.warning("Por favor ingresa un monto.")

# --- 5. CUERPO PRINCIPAL ---
st.title("🏡 Finanzas Familiares G&F")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    total_gastado = df_mes["Monto"].sum()
    presupuesto_total = sum(LIMITES.values())
    balance = presupuesto_total - total_gastado
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Gasto Total", f"${total_gastado:,.2f}")
    m2.metric("Presupuesto", f"${presupuesto_total:,.2f}")
    m3.metric("Disponible", f"${balance:,.2f}")

    st.divider()

    col_izq, col_der = st.columns([1.2, 1])

    with col_izq:
        st.subheader("📊 Control por Categoría")
        gastos_cat = df_mes.groupby("Categoría")["Monto"].sum()
        for cat, limite in LIMITES.items():
            gastado = gastos_cat.get(cat, 0)
            progreso = min(gastado / limite, 1.0)
            st.write(f"**{cat}** — ${gastado:,.2f} de ${limite:,.2f}")
            st.progress(progreso)

    with col_der:
        st.subheader("🍕 Distribución")
        if total_gastado > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', hole=0.5)
            fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin gastos este mes.")

    st.divider()
    st.subheader("📑 Historial")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

except Exception as e:
    st.warning("Sistema listo. Esperando primer registro del mes.")
    st.metric("Balance Inicial", f"${sum(LIMITES.values()):,.2f}")
