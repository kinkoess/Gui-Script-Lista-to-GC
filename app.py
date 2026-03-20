import streamlit as st
import pandas as pd
import io

# Configuración básica
st.set_page_config(page_title="OdontoCalendar Tool", page_icon="🦷")

# CSS para el borde verde y limpiar la tabla
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] { display: none; }
    textarea:focus { border-color: #28a745 !important; }
    .stTextArea label { font-size: 1.1rem; font-weight: bold; color: #28a745; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("# 🦷 OdontoCalendar:  \n# Tabla OneNote a Google Calendar")

# --- PASO 1: LA CARGA ---
st.subheader("1. Carga de Datos")
datos_input = st.text_area("📋 Pega aquí tu tabla de OneNote:", height=150, placeholder="EVALUACION\tASIGNATURA\tFECHA...")

# EL TRUCO: Si no hay texto, mostramos el aviso. Si hay texto, el aviso desaparece 
# y aparece el botón de procesar inmediatamente debajo.
if not datos_input:
    st.info("💡 Esperando que pegues la tabla... (Recuerda que al pegar, Streamlit necesita un segundo para detectar el cambio)")
else:
    # Este botón "desbloquea" el resto de la app
    if st.button("🚀 PROCESAR TABLA AHORA", use_container_width=True):
        st.session_state['listo'] = True

# --- PASO 2: EL PROCESAMIENTO ---
if st.session_state.get('listo') and datos_input:
    try:
        abreviaciones = {
            "1° Teórica": "1° T.", "2° Teórica": "2° T.", "3° Teórica": "3° T.", "4° Teórica": "4° T.",
            "1° Evaluación Clínica": "1° E.C.", "2° Evaluación Clínica": "2° E.C.", "Caso Clínico": "C.C.",
            "Presentación CC": "P.CC", "1° Examen": "1° E.", "2° Examen": "2° E."
        }

        df = pd.read_csv(io.StringIO(datos_input.strip()), sep='\t')
        df.columns = df.columns.str.strip()
        
        opciones_finales = [opt for opt in abreviaciones.keys() if opt in df['EVALUACION'].unique()]

        st.divider()
        st.subheader("2. Filtra tu Calendario")
        categoria = st.selectbox("¿Qué calendario vas a actualizar?", opciones_finales)
        
        # Filtro y Formato
        df_filtrado = df[df['EVALUACION'] == categoria].copy()
        def f_tit(f): return f"{abreviaciones.get(f['EVALUACION'], f['EVALUACION'])} {f['ASIGNATURA']}"

        cal_df = pd.DataFrame()
        cal_df['Subject'] = df_filtrado.apply(f_tit, axis=1)
        cal_df['Start Date'] = pd.to_datetime(df_filtrado['FECHA'] + "-2026", format='%d-%m-%Y').dt.strftime('%m/%d/%Y')
        cal_df['End Date'] = cal_df['Start Date']
        cal_df['All Day Event'] = 'TRUE'
        cal_df['Location'] = 'Universidad Mayor, Temuco'

        st.success(f"✅ ¡{len(cal_df)} eventos listos!")
        st.download_button(f"📥 Descargar {categoria}.csv", cal_df.to_csv(index=False).encode('utf-8'), f"{categoria}.csv", "text/csv", use_container_width=True)
        st.dataframe(cal_df[['Subject', 'Start Date']], use_container_width=True)

    except Exception as e:
        st.error("❌ Error en el formato. Asegúrate de copiar la tabla completa con títulos.")
