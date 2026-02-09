import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="centered")

DATA_FILE = "gastos_familia.csv"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Añadimos la columna "Pago" al DataFrame inicial
        return pd.DataFrame(columns=["Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"])

def guardar_gasto(fecha, cat, desc, monto, usuario, pago):
    df = cargar_datos()
    nuevo_gasto = pd.DataFrame([[str(fecha), cat, desc, monto, usuario, pago]], 
                                columns=["Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"])
    df = pd.concat([df, nuevo_gasto], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- CONFIGURACIÓN ---
CATEGORIAS = [
    "🛒 Súper / Despensa", "🏠 Renta / Hipoteca", "⚡ Servicios", 
    "🚗 Transporte", "🍕 Comida fuera", "💊 Salud", 
    "🎓 Educación", "🛡️ Seguros", "🎈 Ocio", "🎁 Otros"
]

METODOS_PAGO = [
    "💳 Tarjeta de Crédito",
    "🏦 Tarjeta de Débito",
    "💵 Efectivo",
    "📱 Transferencia / App"
]

st.title("🏡 Control de Gastos Familiar")
st.markdown("---")

# Formulario mejorado
with st.container():
    with st.form("nuevo_gasto_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("¿Cuándo?", datetime.now())
            monto = st.number_input("Monto ($)", min_value=0.0, step=1.0, format="%.2f")
            pago = st.selectbox("Método de Pago", METODOS_PAGO) # Nueva opción
        with col2:
            usuario = st.radio("¿Quién pagó?", ["Esposo", "Esposa"], horizontal=True)
            categoria = st.selectbox("Categoría", CATEGORIAS)
        
        descripcion = st.text_input("Nota (Ej: Pago de luz vencido)")
        
        if st.form_submit_button("Registrar Gasto"):
            if monto > 0:
                guardar_gasto(fecha, categoria, descripcion, monto, usuario, pago)
                st.balloons()
                st.success(f"¡Gasto registrado con {pago}!")
            else:
                st.warning("Escribe un monto válido.")

# Análisis de datos
df = cargar_datos()

if not df.empty:
    st.divider()
    
    # Métricas en columnas
    c1, c2 = st.columns(2)
    with c1:
        total = df["Monto"].sum()
        st.metric("Gasto Total", f"${total:,.2f}")
    with c2:
        # Muestra el método de