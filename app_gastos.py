import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Familiares", page_icon="🏡", layout="wide")

# --- 2. ESTILO VISUAL "GOOGLE STITCH" (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        border: none;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IDs Y LÍMITES ACTUALIZADOS ---
SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

# Nuevas categorías y límites solicitados
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

READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx:out:csv"
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

# --- 4. BARRA LATERAL (REGISTRO) ---
with st.sidebar:
    st.title("📝 Nuevo Movimiento")
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
                    st.error("Error de conexión.")

# --- 5. DASHBOARD PRINCIPAL ---
st.title("🏡 Resumen Financiero Familiar")
st.markdown(f"**Estado de cuenta:** {datetime.now().strftime('%B %Y')}")

try:
    df = pd.read_csv(READ_URL)
    df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Filtro de mes actual
    hoy = datetime.now()
    df_mes = df[(df['Fecha'].dt.month == hoy.month) & (df['Fecha'].dt.year == hoy.year)]
    
    # --- MÉTRICAS DE BALANCE ---
    total_gastado = df_mes["Monto"].sum()
    presupuesto_total = sum(LIMITES.values())
    balance_restante = presupuesto_total - total_gastado
    porcentaje_consumido = (total_gastado / presupuesto_total) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total", f"${total_gastado:,.2f}")
    col2.metric("Límite Mensual", f"${presupuesto_total:,.2f}")
    col3.metric("Balance Disponible", f"${balance_restante:,.2f}", 
                delta=f"{100 - porcentaje_consumido:.1f}% libre",
                delta_color="normal" if balance_restante > 0 else "inverse")

    st.divider()

    # --- GRÁFICOS ---
    c_izq, c_der = st.columns([1.2, 1])

    with c_izq:
        st.subheader("📊 Análisis por Categoría")
        gastos_cat = df_mes.groupby("Categoría")["Monto"].sum()
        
        for cat, limite in LIMITES.items():
            gastado = gastos_cat.get(cat, 0)
            progreso = min(gastado / limite, 1.0)
            
            # Color dinámico
            if progreso < 0.7: color_bar = "blue"
            elif progreso < 1.0: color_bar = "orange"
            else: color_bar = "red"
            
            st.write(f"**{cat}** — ${gastado:,.2f} de ${limite:,.2f}")
            st.progress(progreso)

    with c_der:
        st.subheader("🍕 Distribución del Gasto")
        if total_gastado > 0:
            fig = px.pie(df_mes, values='Monto', names='Categoría', 
                         hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Registra gastos para ver el gráfico circular.")

    st.divider()
    st.subheader("📑 Últimos Movimientos")
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

except Exception as e:
    st.info("Inicia el registro para visualizar el balance mensual.")

