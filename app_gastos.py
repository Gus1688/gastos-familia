import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="centered")

# --- CONFIGURACIÓN DE LA HOJA ---
# Asegúrate de que la URL termine en /export?format=csv o sea la URL normal
SHEET_ID = "Datos_gastos_familia" # Instrucciones abajo
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def cargar_datos():
    try:
        # Lee la hoja de Google como si fuera un CSV público
        return pd.read_csv(url)
    except:
        return pd.DataFrame(columns=["Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"])

def guardar_gasto(fecha, cat, desc, monto, usuario, pago):
    # Para guardar datos de forma gratuita y fácil sin errores de permisos, 
    # usaremos un Google Form o una técnica de Google Apps Script.
    # Pero para no complicarte, intentaremos la vía corregida de conexión:
    df_existente = cargar_datos()
    nuevo_gasto = pd.DataFrame([[str(fecha), cat, desc, monto, usuario, pago]], 
                                columns=["Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"])
    df_final = pd.concat([df_existente, nuevo_gasto], ignore_index=True)
    
    # Aquí es donde el error ocurría. Vamos a usar el conector simple:
    try:
        conn = st.connection("gsheets", type="streamlit_gsheets.GSheetsConnection")
        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- EL RESTO DE TU INTERFAZ (IGUAL A LA ANTERIOR) ---
CATEGORIAS = ["🛒 Súper / Despensa", "🏠 Renta / Hipoteca", "⚡ Servicios", "🚗 Transporte", "🍕 Comida fuera", "💊 Salud", "🎓 Educación", "🛡️ Seguros", "🎈 Ocio", "🎁 Otros"]
METODOS_PAGO = ["💳 Tarjeta de Crédito", "🏦 Tarjeta de Débito", "💵 Efectivo", "📱 Transferencia / App"]

st.title("🏡 Finanzas Familiares")

with st.form("nuevo_gasto_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("¿Cuándo?", datetime.now())
        monto = st.number_input("Monto ($)", min_value=0.0, step=1.0, format="%.2f")
        pago = st.selectbox("Método de Pago", METODOS_PAGO)
    with col2:
        usuario = st.radio("¿Quién pagó?", ["Gustavo", "Fabiola"], horizontal=True)
        categoria = st.selectbox("Categoría", CATEGORIAS)
    
    descripcion = st.text_input("Nota")
    
    if st.form_submit_button("Registrar Gasto"):
        if monto > 0:
            exito = guardar_gasto(fecha, categoria, descripcion, monto, usuario, pago)
            if exito:
                st.balloons()
                st.success("¡Guardado!")
        else:
            st.warning("Escribe un monto válido.")

df = cargar_datos()
if not df.empty:
    st.divider()
    st.metric("Total", f"${df['Monto'].sum():,.2f}")
    st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
