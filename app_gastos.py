import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Aquí usamos el conector oficial de Streamlit para Sheets
url = "https://docs.google.com/spreadsheets/d/1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4/edit?gid=0#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5], ttl="0")

def guardar_gasto(fecha, cat, desc, monto, usuario, pago):
    df_existente = cargar_datos()
    nuevo_gasto = pd.DataFrame([[str(fecha), cat, desc, monto, usuario, pago]], 
                                columns=["Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"])
    df_final = pd.concat([df_existente, nuevo_gasto], ignore_index=True)
    conn.update(spreadsheet=url, data=df_final)

# --- EL RESTO DEL CÓDIGO SIGUE IGUAL ---
CATEGORIAS = ["🛒 Súper / Despensa", "🏠 Renta / Hipoteca", "⚡ Servicios", "🚗 Transporte", "🍕 Comida fuera", "💊 Salud", "🎓 Educación", "🛡️ Seguros", "🎈 Ocio", "🎁 Otros"]
METODOS_PAGO = ["💳 Tarjeta de Crédito", "🏦 Tarjeta de Débito", "💵 Efectivo", "📱 Transferencia / App"]

st.title("🏡 Finanzas en la Nube")

with st.form("nuevo_gasto_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("¿Cuándo?", datetime.now())
        monto = st.number_input("Monto ($)", min_value=0.0, step=1.0, format="%.2f")
        pago = st.selectbox("Método de Pago", METODOS_PAGO)
    with col2:
        usuario = st.radio("¿Quién pagó?", ["Esposo", "Esposa"], horizontal=True)
        categoria = st.selectbox("Categoría", CATEGORIAS)
    
    descripcion = st.text_input("Nota")
    
    if st.form_submit_button("Registrar Gasto"):
        if monto > 0:
            guardar_gasto(fecha, categoria, descripcion, monto, usuario, pago)
            st.cache_data.clear() # Limpiar cache para ver el dato nuevo
            st.balloons()
            st.success("¡Guardado en Google Sheets!")

# Mostrar datos
try:
    df = cargar_datos()
    if not df.empty:
        st.divider()
        st.metric("Total Acumulado", f"${df['Monto'].sum():,.2f}")
        st.subheader("Historial (Google Sheets)")
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
except:
    st.info("Conectando con la base de datos...")
