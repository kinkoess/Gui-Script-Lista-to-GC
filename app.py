import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="OdontoCalendar Tool", page_icon="🦷")
st.title("🦷 OdontoCalendar: OneNote a Google Calendar")

# 1. Entrada de datos
st.subheader("1. Pega tu tabla de OneNote")
datos_input = st.text_area("Copia la tabla completa de OneNote y pégala aquí:", height=200, placeholder="EVALUACION\tASIGNATURA\tFECHA...")

# 2. Diccionario con el ORDEN y ABREVIACIONES exactas
# Esto controla tanto el orden en la GUI como el texto final
abreviaciones = {
    "1° Teórica": "1° T.",
    "2° Teórica": "2° T.",
    "3° Teórica": "3° T.",
    "4° Teórica": "4° T.",
    "1° Evaluación Clínica": "1° E.C.",
    "2° Evaluación Clínica": "2° E.C.",
    "Caso Clínico": "C.C.",
    "Presentación CC": "P.CC",
    "1° Examen": "1° E.",
    "2° Examen": "2° E."
}

if datos_input:
    try:
        # Procesamiento inicial
        df = pd.read_csv(io.StringIO(datos_input.strip()), sep='\t')
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Filtramos las opciones para que solo aparezcan las que existen en la tabla 
        # pero respetando el orden de tu lista de abreviaciones
        opciones_disponibles = [opt for opt in abreviaciones.keys() if opt in df['EVALUACION'].unique()]
        
        # Si hay algo que no está en el diccionario, lo añadimos al final por si acaso
        otros = [opt for opt in df['EVALUACION'].unique() if opt not in abreviaciones.keys()]
        opciones_finales = opciones_disponibles + otros

        st.subheader("2. Filtra tu Calendario")
        categoria = st.selectbox("¿Qué calendario vas a actualizar ahora?", opciones_finales)
        
        if st.button("Generar Archivo para Google"):
            # Filtro estricto por la categoría seleccionada
            df_filtrado = df[df['EVALUACION'] == categoria].copy()
            
            def formatear_titulo(fila):
                eval_orig = fila['EVALUACION']
                asignatura = fila['ASIGNATURA']
                # Sacamos la abreviación del diccionario (si no existe, usa la original)
                abrev = abreviaciones.get(eval_orig, eval_orig)
                # Formato final solicitado: "1° T. Asignatura"
                return f"{abrev} {asignatura}"

            calendar_df = pd.DataFrame()
            calendar_df['Subject'] = df_filtrado.apply(formatear_titulo, axis=1)
            # Año 2026 configurado
            calendar_df['Start Date'] = pd.to_datetime(df_filtrado['FECHA'] + "-2026", format='%d-%m-%Y').dt.strftime('%m/%d/%Y')
            calendar_df['End Date'] = calendar_df['Start Date']
            calendar_df['All Day Event'] = 'TRUE'
            calendar_df['Location'] = 'Universidad Mayor, Temuco'
            calendar_df['Private'] = 'TRUE'

            # Botón de descarga con el nombre del archivo igual a la opción
            csv = calendar_df.to_csv(index=False).encode('utf-8')
            st.success(f"¡Listo! Se encontraron {len(calendar_df)} eventos para {categoria}")
            
            # El nombre del archivo ahora coincide con la opción seleccionada
            nombre_archivo_final = f"{categoria}.csv"
            
            st.download_button(
                label=f"Descargar archivo: {nombre_archivo_final}",
                data=csv,
                file_name=nombre_archivo_final,
                mime='text/csv',
            )
            # Vista previa para confirmar el formato del Subject
            st.dataframe(calendar_df[['Subject', 'Start Date']]) 

    except Exception as e:
        st.error(f"Error al procesar: Asegúrate de que las columnas se llamen EVALUACION, ASIGNATURA y FECHA.")
