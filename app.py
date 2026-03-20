import streamlit as st
import pandas as pd
import io
from st_keyup import st_keyup # Esta es la pieza clave

st.set_page_config(page_title="OdontoCalendar", page_icon="🦷")

st.markdown("# 🦷 OdontoCalendar:  \n# Tabla OneNote a Google")

# Contenedor para el mensaje que debe desaparecer
placeholder = st.empty()

# El input que reacciona AL TIRO
datos_input = st_keyup("Pega tu tabla aquí", key="input_realtime", height=150)

if not datos_input:
    placeholder.info("💡 Por favor, pega la tabla de OneNote arriba para comenzar.")
else:
    placeholder.empty() # SE BORRA AL INSTANTE AL DETECTAR TEXTO
    
    if st.button("🚀 Procesar Tabla", use_container_width=True):
        try:
            # Procesamiento que ya conocemos
            df = pd.read_csv(io.StringIO(datos_input.strip()), sep='\t')
            df.columns = df.columns.str.strip()
            
            st.success("✅ Tabla cargada correctamente")
            # ... (aquí sigue el resto de tu lógica de filtros)
            st.write(df.head()) 
        except:
            st.error("Error en el formato de la tabla")
