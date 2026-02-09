import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="centered")

# --- 1. CONFIGURACIÓN (RELLENA ESTO) ---
SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

# URLs de conexión
READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
SUBMIT_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

def enviar_a_google(fecha, cat, desc, monto, usuario, pago):
    # REEMPLAZA LOS NÚMEROS CON TUS 6 CÓDIGOS ENTRY
    payload = {
        "entry.1460713451": str(fecha),
        "entry.1410133594": cat,
        "entry.344685481": desc,
        "entry.324330457": str(monto),
        "entry.745504096": usuario,
        "entry.437144806": pago
    }
    try:
        # Usamos requests puro, sin librerías de Streamlit para evitar bloqueos
        response = requests.post(SUBMIT_URL, data=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error de conexión: {e}")
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
            # Aquí llamamos a la función que usa el Formulario
            if enviar_a_google(fecha, categoria, descripcion, monto, usuario, pago):
                st.balloons()
                st.success("¡Gasto guardado con éxito!")
                st.cache_data.clear() 
            else:
                st.error("No se pudo guardar. Verifica los IDs y la conexión.")
        else:
            st.warning("Por favor, ingresa un monto mayor a 0.")

# --- TABLA DE DATOS (LECTURA) ---
st.divider()
st.subheader("Historial de Gastos")
try:
    # IMPORTANTE: La hoja debe estar en 'Cualquier persona con el enlace puede ver'
    df = pd.read_csv(READ_URL)
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
except:
    st.info("Los datos aparecerán aquí en unos segundos después de tu primer registro.")
