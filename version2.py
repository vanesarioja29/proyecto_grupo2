import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium

# Cargar los datos
file_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  # Cambia la ruta según donde tengas el archivo
data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Preprocesamiento: Convertir las columnas que son de interés a tipos numéricos cuando sea necesario
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Título de la aplicación
st.title('Dashboard de Residuos en el Perú')

# Crear un mapa interactivo
st.subheader('Mapa Interactivo del Perú para Selección de Departamentos')
m = folium.Map(location=[-9.19, -75.015], zoom_start=6)

# Diccionario con las coordenadas de los departamentos y la provincia constitucional
ubicaciones = {
    'Amazonas': [-5.0713, -78.0465],
    'Áncash': [-9.5295, -77.5285],
    'Apurímac': [-13.6350, -72.8816],
    'Arequipa': [-16.4090, -71.5375],
    'Ayacucho': [-13.1588, -74.2236],
    'Cajamarca': [-7.1617, -78.5003],
    'Callao': [-12.0547, -77.1181],
    'Cusco': [-13.5320, -71.9675],
    'Huancavelica': [-13.0238, -75.0350],
    'Huánuco': [-9.9306, -76.2422],
    'Ica': [-14.0675, -75.7286],
    'Junín': [-11.5417, -74.8679],
    'La Libertad': [-8.1154, -78.9903],
    'Lambayeque': [-6.7011, -79.9061],
    'Lima': [-12.0464, -77.0428],
    'Loreto': [-3.7491, -73.2538],
    'Madre de Dios': [-12.5933, -69.1856],
    'Moquegua': [-17.1944, -70.9350],
    'Pasco': [-10.6832, -76.2566],
    'Piura': [-5.1945, -80.6328],
    'Puno': [-15.8402, -70.0219],
    'San Martín': [-6.4854, -76.3569],
    'Tacna': [-18.0056, -70.2486],
    'Tumbes': [-3.5669, -80.4515],
    'Ucayali': [-8.3791, -74.5539]
}


for depto, coord in ubicaciones.items():
    if depto in departamentos:
        folium.Marker(
            location=coord,
            popup=f'Departamento: {depto}',
            tooltip=f'Selecciona {depto}',
            on_click=lambda: st.session_state.update(departamento_seleccionado=depto)
        ).add_to(m)

# Mostrar el mapa y capturar la selección
mapa_interactivo = st_folium(m, width=700, height=500)

# Revisar si se ha seleccionado un departamento
departamento_seleccionado = st.session_state.get('departamento_seleccionado', '')

if departamento_seleccionado:
    st.write(f'Departamento seleccionado: {departamento_seleccionado}')
    if departamento_seleccionado in departamentos:
        # Filtro de Región
        region = data[data['DEPARTAMENTO'] == departamento_seleccionado]['REG_NAT'].iloc[0]
        
        # Filtro de Tipo de Residuo
        tipo_residuo = st.selectbox('Selecciona el Tipo de Residuo', [
            'QRESIDUOS_DOM', 
            'QRESIDUOS_ALIMENTOS', 
            'QRESIDUOS_MALEZA', 
            'QRESIDUOS_OTROS_ORGANICOS', 
            'QRESIDUOS_PAPEL_BLANCO', 
            'QRESIDUOS_PAPEL_PERIODICO',
            'QRESIDUOS_PAPEL_MIXTO',
            'QRESIDUOS_CARTON_BLANCO',
            'QRESIDUOS_CARTON_MARRON',
            'QRESIDUOS_CARTON_MIXTO'
        ])

        # Filtrar los datos según el departamento seleccionado
        filtered_data = data[data['DEPARTAMENTO'] == departamento_seleccionado]

        # Visualización de los residuos
        st.subheader(f'Gráfica de {tipo_residuo} en el Departamento de {departamento_seleccionado}')

        # Graficar la cantidad de residuos por distrito
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(filtered_data['DISTRITO'], filtered_data[tipo_residuo])
        ax.set_xlabel('Distrito')
        ax.set_ylabel('Cantidad de Residuos')
        ax.set_title(f'{tipo_residuo} en el Departamento de {departamento_seleccionado}')

        # Mostrar la gráfica
        st.pyplot(fig)

        # Mostrar algunos datos filtrados como tabla
        st.subheader('Datos Filtrados')
        st.write(filtered_data[['DISTRITO', tipo_residuo]])
    else:
        st.warning('El departamento seleccionado no tiene datos disponibles.')
else:
    st.info('Selecciona un departamento en el mapa.')





