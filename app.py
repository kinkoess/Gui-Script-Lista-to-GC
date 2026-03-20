import streamlit as st
import pandas as pd
import io
from st_keyup import st_keyup # Importamos la librería para tiempo real

# Configuración
st.set_page_config(page_title="OdontoCalendar Tool", page_icon="🦷")

# CSS para ocultar el botón de la tabla y poner borde verde
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] { display: none; }
    textarea:focus { border-color: #28a745 !important; box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important; }
    .stTextArea label { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("# 🦷 OdontoCalendar:  \n# Tabla OneNote a Google Calendar")
st.subheader("1. Carga de Datos")

# Inicializar estados
if "procesar" not in st.session_state:
    st.session_state['procesar'] = False

# CONTENEDOR DINÁMICO
contenedor_mensaje = st.empty()

# USAMOS ST_KEYUP EN LUGAR DE ST.TEXT_AREA
# Esto detecta cada letra o el pegado SIN esperar al Ctrl+Enter
datos_input = st_keyup(
    label="Input_Invisible", 
    height=150, 
    placeholder="Pega aquí tu tabla de OneNote...",
    key="input_tabla"
)

# LÓGICA DE RESPUESTA INSTANTÁNEA
if not datos_input:
    contenedor_mensaje.info("💡 Por favor, pega la tabla de OneNote arriba para comenzar.")
    st.session_state['procesar'] = False
else:
    # EL MENSAJE DESAPARECE APENAS PEGAS (SIN CLICK AFUERA)
    contenedor_mensaje.empty()
    
    if st.button("🚀 Procesar Tabla Pegada", use_container_width=True):
        st.session_state['procesar'] = True

# --- PROCESAMIENTO ---
if st.session_state.get('procesar') and datos_input:
    try:
        abreviaciones = {
            "1° Teórica": "1° T.", "2° Teórica": "2° T.", "3° Teórica": "3° T.", "4° Teórica": "4° T.",
            "1° Evaluación Clínica": "1° E.C.", "2° Evaluación Clínica": "2° E.C.", "Caso Clínico": "C.C.",
            "Presentación CC": "P.CC", "1° Examen": "1° E.", "2° Examen": "2° E."
        }

        df = pd.read_csv(io.StringIO(datos_input.strip()), sep='\t')
        df.columns = df.columns.str.strip()
        
        opciones_disponibles = [opt for opt in abreviaciones.keys() if opt in df['EVALUACION'].unique()]
        otros = [opt for opt in df['EVALUACION'].unique() if opt not in abreviaciones.keys()]
        opciones_finales = opciones_disponibles + otros

        st.divider()
        st.subheader("2. Filtra tu Calendario")
        categoria = st.selectbox("¿Qué calendario vas a actualizar?", opciones_finales)
        
        df_filtrado = df[df['EVALUACION'] == categoria].copy()
        
        def formatear_titulo(fila):
            abrev = abreviaciones.get(fila['EVALUACION'], fila['EVALUACION'])
            return f"{abrev} {fila['ASIGNATURA']}"

        calendar_df = pd.DataFrame()
        calendar_df['Subject'] = df_filtrado.apply(formatear_titulo, axis=1)
        calendar_df['Start Date'] = pd.to_datetime(df_filtrado['FECHA'] + "-2026", format='%d-%m-%Y').dt.strftime('%m/%d/%Y')
        calendar_df['End Date'] = calendar_df['Start Date']
        calendar_df['All Day Event'] = 'TRUE'
        calendar_df['Location'] = 'Universidad Mayor, Temuco'
        calendar_df['Private'] = 'TRUE'

        csv = calendar_df.to_csv(index=False).encode('utf-8')
        st.success(f"✅ ¡Tabla detectada!")
        
        st.download_button(
            label=f"📥 Descargar {categoria}.csv",
            data=csv,
            file_name=f"{categoria}.csv",
            mime='text/csv',
            use_container_width=True
        )
        st.dataframe(calendar_df[['Subject', 'Start Date']], use_container_width=True)

    except Exception as e:
        st.error("❌ Error: Asegúrate de copiar los encabezados de la tabla.")
