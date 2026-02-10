import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas G&F", page_icon="🏡", layout="wide")

# --- 2. CONFIGURACIÓN DE DATOS ---
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

# --- 3. SIDEBAR (REGISTRO) ---
with st.sidebar:
    st.header("📝 Registro de Gasto")
    # Quitamos el 'clear_on_submit' para evitar saltos visuales extraños
    with st.form("nuevo_gasto"):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Pago", ["💳 Crédito", "🏦 Débito", "💵 Efectivo", "📱 Transf."])
        d = st.text_input("Nota")
        
        # Botón nativo (sin CSS forzado)
        submit = st.form_submit_button("GUARDAR EN GOOGLE SHEETS")
        
        if submit:
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.success("✅ ¡Guardado!")
                    st.balloons()
                    st.cache_data.clear()
                else:
                    st.error("❌ Error de envío")
            else:
                st.warning("Escribe un monto")

# --- 4. DASHBOARD PRINCIPAL ---
st.title("🏡 Finanzas Familiares")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    gastado = df_mes["Monto"].sum()
    presupuesto = sum(LIMITES.values())
    disponible = presupuesto - gastado

    # MÉTRICAS ESTÁNDAR (Son legibles en cualquier modo)
    col1, col2, col3 = st.columns(3)
    col1.metric("GASTADO", f"${gastado:,.2f}")
    col2.metric("PRESUPUESTO", f"${presupuesto:,.2f}")
    col3.metric("DISPONIBLE", f"${disponible:,.2f}", delta=f"${disponible}")

    st.divider()

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.subheader("📊 Por Categoría")
        gastos_cat = df_mes.groupby("Categoría")["Monto"].sum()
        for cat, lim in LIMITES.items():
            valor = gastos_cat.get(cat, 0)
            pct = min(valor / lim, 1.0)
            st.write(f"**{cat}**")
            st.progress(pct)
            st.caption(f"${valor:,.2f} de ${lim:,.2f}")

    with col_der:
        st.subheader("🍕 Distribución")
        if gastado > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay gastos registrados este mes.")

    st.divider()
    st.subheader("📑 Historial")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)

except:
    st.info("👋 ¡Hola! Registra un gasto para comenzar.")
