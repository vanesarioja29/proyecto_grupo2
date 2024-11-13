import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import json

# Cargar los datos
file_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  
data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Cargar el archivo GeoJSON de los departamentos de Perú
geojson_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  # Cambia la ruta a tu archivo GeoJSON
with open(geojson_path, 'r', encoding='ISO-8859-1') as file:
    peru_geojson = json.load(file)

# Preprocesamiento: Convertir columnas relevantes a tipos numéricos
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Título de la aplicación
st.title('Dashboard de Residuos con Mapa Interactivo')

# Filtro de Región y Departamento
region = st.selectbox('Selecciona la Región', data['REG_NAT'].unique())
departamento = st.selectbox('Selecciona el Departamento', data[data['REG_NAT'] == region]['DEPARTAMENTO'].unique())

# Filtrar datos por el departamento seleccionado
filtered_data = data[data['DEPARTAMENTO'] == departamento]

# Resumen de estadísticas generales para el departamento seleccionado
st.subheader(f'Estadísticas Generales de Residuos en {departamento}')
stats = filtered_data.groupby('DEPARTAMENTO').sum(numeric_only=True).iloc[0]
st.write(stats)

# Crear el mapa de Perú centrado
m = folium.Map(location=[-9.19, -75.0152], zoom_start=5, tiles='cartodb positron')

# Agregar capa de departamentos al mapa
folium.Choropleth(
    geo_data=peru_geojson,
    name="choropleth",
    data=filtered_data,
    columns=["DEPARTAMENTO", "QRESIDUOS_DOM"],  # Cambia la columna para mostrar otra métrica
    key_on="feature.properties.NOMBDEP",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Residuos Domiciliarios"
).add_to(m)

# Mostrar el mapa en Streamlit
st.subheader(f"Mapa Interactivo de {departamento}")
st_folium(m, width=700, height=450)

# Seleccionar y graficar una estadística de residuos específica
tipo_residuo = st.selectbox(
    'Selecciona el Tipo de Residuo para Visualización Detallada',
    ['QRESIDUOS_DOM', 'QRESIDUOS_ALIMENTOS', 'QRESIDUOS_MALEZA', 'QRESIDUOS_OTROS_ORGANICOS', 
     'QRESIDUOS_PAPEL_BLANCO', 'QRESIDUOS_PAPEL_PERIODICO', 'QRESIDUOS_PAPEL_MIXTO', 
     'QRESIDUOS_CARTON_BLANCO', 'QRESIDUOS_CARTON_MARRON', 'QRESIDUOS_CARTON_MIXTO']
)

# Visualización de residuos seleccionados por distrito
st.subheader(f'Gráfica de {tipo_residuo} por Distrito en {departamento}')
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(filtered_data['DISTRITO'], filtered_data[tipo_residuo])
ax.set_xlabel('Distrito')
ax.set_ylabel('Cantidad de Residuos')
ax.set_title(f'{tipo_residuo} en {departamento}')
st.pyplot(fig)

# Mostrar tabla de datos filtrados
st.subheader('Datos Filtrados')
st.write(filtered_data[['DISTRITO', tipo_residuo]])
