import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="centered")

# --- 1. CONFIGURACIÓN DE ENLACES (RELLENA ESTO) ---
# ID de tu hoja de Google (el que está en la URL entre /d/ y /edit)
SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
# ID de tu formulario (el que está en la URL de enviar entre /d/e/ y /formResponse)
FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

# URL para LEER los datos
READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
# URL para ENVIAR los datos
SUBMIT_URL = f"https://forms.google.com/forms/d/e/{FORM_ID}/formResponse"

def enviar_a_google(fecha, cat, desc, monto, usuario, pago):
    # SUSTITUYE LOS NÚMEROS POR TUS 6 CÓDIGOS ENTRY
    payload = {
        "entry.1460713451": str(fecha),   # Fecha
        "entry.1410133594": cat,          # Categoría
        "entry.344685481": desc,         # Descripción
        "entry.324330457": str(monto),   # Monto
        "entry.745504096": usuario,      # Usuario
        "entry.437144806": pago          # Pago
    }
    try:
        r = requests.post(SUBMIT_URL, data=payload)
        return r.status_code == 200
    except:
        return False

# --- INTERFAZ ---
st.title("🏡 Finanzas Familiares")
st.markdown("---")

with st.form("nuevo_gasto", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        monto = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        pago = st.selectbox("Método de Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
    with col2:
        usuario = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        categoria = st.selectbox("Categoría", ["🛒 Súper", "🏠 Renta", "⚡ Servicios", "🚗 Transporte", "🍕 Comida", "🎁 Otros"])
    
    descripcion = st.text_input("Nota")
    
    if st.form_submit_button("Registrar Gasto"):
        if monto > 0:
            if enviar_a_google(fecha, categoria, descripcion, monto, usuario, pago):
                st.balloons()
                st.success("¡Gasto guardado en la nube!")
                st.cache_data.clear() # Refrescar tabla
            else:
                st.error("Error al conectar con Google.")

# --- MOSTRAR DATOS ---
st.divider()
try:
    df = pd.read_csv(READ_URL)
    # Ajustamos nombres de columnas si Google Forms les puso otros
    st.metric("Total Mes", f"${df.iloc[:, 4].sum():,.2f}") # Suma la columna del monto
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
except:
    st.info("Aún no hay datos registrados o la hoja no es pública.")

