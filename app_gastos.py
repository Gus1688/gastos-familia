import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="wide")

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

# --- 2. LÍMITES MENSUALES (Ajusta los montos aquí) ---
LIMITES = {
    "🛒 Súper": 1000.0,
    "🏠 Hipoteca": 5600.0,
    "⚡ Servicios": 200.0,
    "🚗 Transporte": 150.0,
    "🍕 Salidas / Comida fuera": 1000.0,
    "💊 Salud / Farmacia": 300.0,
    "🎓 Educación / Nido": 1000,
    " 🛡️ Seguros": 500.0,
    "🎈 Ocio / Entretenimiento": 500.0.
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

# --- SIDEBAR: REGISTRO DE GASTOS ---
with st.sidebar:
    st.title("📝 Registro")
    with st.form("nuevo_gasto", clear_on_submit=True):
        f = st.date_input("Fecha", datetime.now())
        m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        c = st.selectbox("Categoría", list(LIMITES.keys()))
        u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
        p = st.selectbox("Método de Pago", ["💳 Tarjeta Crédito", "🏦 Tarjeta Débito", "💵 Efectivo", "📱 Transferencia"])
        d = st.text_input("Nota")
        
        if st.form_submit_button("Registrar Gasto"):
            if m > 0:
                if enviar_a_google(f, c, d, m, u, p):
                    st.balloons()
                    st.success("¡Guardado!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Error al conectar con Google.")

# --- CUERPO PRINCIPAL: DASHBOARD ---
st.title("🏡 Dashboard Finanzas Familiares")
st.markdown(f"**Análisis del mes:** {datetime.now().strftime('%B %Y')}")

try:
    # Lectura de datos
    df = pd.read_csv(READ_URL)
    
    # Ajustar nombres (Google Forms añade Timestamp al inicio)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Filtrar mes actual
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    # --- MÉTRICAS ---
    total_mes = df_mes["Monto"].sum()
    presupuesto_total = sum(LIMITES.values())
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Gasto Total Mes", f"${total_mes:,.2f}")
    m2.metric("Presupuesto", f"${presupuesto_total:,.2f}")
    m3.metric("Balance", f"${presupuesto_total - total_mes:,.2f}", 
              delta_color="normal" if total_mes < presupuesto_total else "inverse")

    st.divider()

    # --- GRÁFICOS ---
    col_prog, col_pie = st.columns([1.2, 1])

    with col_prog:
        st.subheader("📊 Presupuesto por Categoría")
        gastos_por_cat = df_mes.groupby("Categoría")["Monto"].sum()
        
        for cat, limite in LIMITES.items():
            gastado = gastos_por_cat.get(cat, 0)
            porcentaje = min(gastado / limite, 1.0)
            
            # Color de barra según gasto
            color = "green" if porcentaje < 0.8 else "orange" if porcentaje < 1.0 else "red"
            
            st.write(f"**{cat}** (${gastado:,.2f} de ${limite:,.2f})")
            st.progress(porcentaje)
            if gastado > limite:
                st.caption(f"⚠️ Exceso de ${gastado-limite:,.2f}")

    with col_pie:
        st.subheader("🍕 Distribución de Gastos")
        if total_mes > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos suficientes este mes.")

    st.divider()
    st.subheader("📑 Historial Completo")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)

except Exception as e:
    st.info("👋 ¡Hola Gustavo y Fabiola! Registren su primer gasto para activar las gráficas.")


