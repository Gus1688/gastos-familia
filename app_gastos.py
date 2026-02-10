import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Finanzas Casita", page_icon="🏡", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* Hacer que el botón de guardar sea verde y destaque */
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERIFICACIÓN DE CONTRASEÑA ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔒 Acceso Privado")
        clave_usuario = st.text_input("Introduce la contraseña familiar:", type="password")
        if st.button("Entrar"):
            if clave_usuario == st.secrets["password"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        return False
    return True

if login():
    # --- CONFIGURACIÓN DE DATOS ---
    SHEET_ID = "1C923YPTM65pFZYS8qHtFkcVZYVNkAoZ455JkjZwpwU4" 
    FORM_ID = "1FAIpQLSfowcz9hT3dckaDw_hJ2MRJ9eshXlM9QHXc9dbr_1hQk2yx5Q"

    LIMITES = {
        "🎓 Educacion": 1500.0, "⚡ Servicios": 321.0, "🛠️ Mantenimiento": 500.0,
        "🛡️ Seguros": 630.0, "📺 Suscripciones": 123.0, "🚗 Transporte": 350.0,
        "🏦 Prestamo": 5600.0, "⚖️ Impuestos": 150.0, "🛒 Comida+Super": 2500.0,
        "🍕 Salidas": 600.0, "🎁 Otros": 200.0
    }

    READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
    SUBMIT_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

    def enviar_a_google(fecha, cat, desc, monto, usuario, pago):
        payload = {
            "entry.1460713451": str(fecha), "entry.1410133594": cat,
            "entry.344685481": desc, "entry.324330457": str(monto),
            "entry.745504096": usuario, "entry.437144806": pago
        }
        try:
            response = requests.post(SUBMIT_URL, data=payload)
            return response.status_code < 400
        except: return False

    # --- 3. ENCABEZADO Y LOGOUT ---
    col_t, col_l = st.columns([4, 1])
    with col_t:
        st.title("🏡 Finanzas G&F")
    with col_l:
        if st.button("Salir"):
            st.session_state["autenticado"] = False
            st.rerun()

    # --- 4. FORMULARIO DE REGISTRO (AHORA EN EL CUERPO PRINCIPAL) ---
    with st.expander("➕ REGISTRAR NUEVO GASTO", expanded=False):
        with st.form("nuevo_gasto", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f = st.date_input("Fecha", datetime.now())
                m = st.number_input("Monto ($)", min_value=0.0, step=1.0)
                u = st.radio("¿Quién?", ["Gustavo", "Fabiola"], horizontal=True)
            with col2:
                c = st.selectbox("Categoría", list(LIMITES.keys()))
                p = st.selectbox("Pago", ["💳 Crédito", "🏦 Débito", "💵 Efectivo", "📱 Transf."])
                d = st.text_input("Nota")
            
            if st.form_submit_button("GUARDAR GASTO"):
                if m > 0:
                    if enviar_a_google(f, c, d, m, u, p):
                        st.success("✅ ¡Guardado!")
                        st.cache_data.clear()
                        st.rerun()
                    else: st.error("❌ Error")

    # --- 5. DASHBOARD ---
    try:
        df = pd.read_csv(READ_URL)
        df.columns = ["Timestamp", "Fecha", "Categoría", "Descripción", "Monto", "Usuario", "Pago"]
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        hoy = datetime.now()
        st.subheader("🗓️ Filtro de Mes")
        c_mes, c_anio = st.columns(2)
        with c_mes:
            mes_sel = st.selectbox("Selecciona Mes", options=list(meses_nombres.keys()), 
                                   format_func=lambda x: meses_nombres[x], index=hoy.month-1)
        with c_anio:
            anios_disponibles = sorted(pd.to_datetime(df['Fecha']).dt.year.unique())
            if hoy.year not in anios_disponibles: anios_disponibles.append(hoy.year)
            anio_sel = st.selectbox("Selecciona Año", options=anios_disponibles, index=anios_disponibles.index(hoy.year))

        df_filtrado = df[(pd.to_datetime(df['Fecha']).dt.month == mes_sel) & 
                         (pd.to_datetime(df['Fecha']).dt.year == anio_sel)].copy()
        df_filtrado['Fecha'] = pd.to_datetime(df_filtrado['Fecha']).dt.strftime('%d-%m-%Y')

        gastado = df_filtrado["Monto"].sum()
        presupuesto = sum(LIMITES.values())
        disponible = presupuesto - gastado

        m1, m2, m3 = st.columns(3)
        m1.metric("GASTADO", f"${gastado:,.2f}")
        m2.metric("LÍMITE", f"${presupuesto:,.2f}")
        m3.metric("RESTANTE", f"${disponible:,.2f}", delta=f"${disponible:,.2f}")

        st.divider()
        col_izq, col_der = st.columns([1, 1])
        with col_izq:
            st.subheader("📊 Por Categoría")
            gastos_cat = df_filtrado.groupby("Categoría")["Monto"].sum()
            for cat, lim in LIMITES.items():
                v = gastos_cat.get(cat, 0)
                st.write(f"**{cat}** (${v:,.2f} / ${lim:,.2f})")
                st.progress(min(v / lim, 1.0))

        with col_der:
            st.subheader("🍕 Distribución")
            if gastado > 0:
                fig = px.pie(df_filtrado, values='Monto', names='Categoría', hole=0.5)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin registros.")

        st.divider()
        st.subheader("📑 Historial")
        st.dataframe(df_filtrado.sort_values("Fecha", ascending=False).drop(columns=["Timestamp"]), 
                     use_container_width=True, hide_index=True)

    except Exception as e:
        st.info("👋 Registra tu primer gasto para ver el dashboard.")

