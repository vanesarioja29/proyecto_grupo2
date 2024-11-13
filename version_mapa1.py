import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from shapely.geometry import Polygon
from streamlit_folium import folium_static

# Cargar el shapefile de los departamentos de Perú
shapefile_path = '/workspaces/proyecto_grupo2/Departamental.shp'  # Asegúrate de usar la ruta correcta
gdf_departamentos = gpd.read_file(shapefile_path)

# Cargar los datos de residuos (asegúrate de tener el archivo CSV)
data_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  # Ruta al archivo CSV de residuos
data = pd.read_csv(data_path, encoding='ISO-8859-1', delimiter=';')

# Preprocesamiento: Convertir las columnas relevantes a tipos numéricos
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Agrupar por departamento
data_grouped = data.groupby('DEPARTAMENTO').sum().reset_index()

# Renombrar columna en el GeoDataFrame
gdf_departamentos.rename(columns={'DEPARTAMEN': 'DEPARTAMENTO'}, inplace=True)

# Fusionar los datos con la geometría de los departamentos
gdf_merged = gdf_departamentos.merge(data_grouped, on='DEPARTAMENTO')

# Crear un mapa base de Perú
m = folium.Map(location=[-9.19, -75.015], zoom_start=5)

# Añadir los departamentos al mapa con un popup con la información
for idx, row in gdf_merged.iterrows():
    # Usamos el centroide de cada geometría para marcar el departamento
    lat, lon = row['geometry'].centroid.y, row['geometry'].centroid.x
    
    # Redondear los valores a 2 decimales y agregar "toneladas"
    residuos_dom = round(row['QRESIDUOS_DOM'], 2)
    residuos_alimentos = round(row['QRESIDUOS_ALIMENTOS'], 2)
    residuos_maleza = round(row['QRESIDUOS_MALEZA'], 2)

    # Crear un popup con los datos de residuos
    popup_text = f"""
    <strong>{row['DEPARTAMENTO']}</strong><br>
    Residuos Domésticos: {residuos_dom} Tn<br>
    Residuos de Alimentos: {residuos_alimentos} Tn<br>
    Residuos de Maleza: {residuos_maleza} Tn
    """
    
    # Añadir el marcador al mapa
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Crear una figura de Folium y mostrarla en Streamlit
map_fig = folium.Figure(width=700, height=500).add_child(m)
st.title('Mapa Interactivo de Residuos por Departamento')
st.subheader('Haz clic en los departamentos para ver la información')

# Mostrar el mapa interactivo en Streamlit
folium_static(m)

# Selección del departamento para ver más detalles
selected_departamento = st.selectbox('Selecciona un Departamento:', gdf_merged['DEPARTAMENTO'])

# Mostrar información de residuos para el departamento seleccionado
selected_data = gdf_merged[gdf_merged['DEPARTAMENTO'] == selected_departamento]

# Redondear los valores a 2 decimales y agregar "toneladas"
selected_residuos_dom = round(selected_data['QRESIDUOS_DOM'].values[0], 2)
selected_residuos_alimentos = round(selected_data['QRESIDUOS_ALIMENTOS'].values[0], 2)
selected_residuos_maleza = round(selected_data['QRESIDUOS_MALEZA'].values[0], 2)

# Mostrar datos detallados
residuos_data = {
    "Tipo de Residuo": ["Residuos Domésticos", "Residuos de Alimentos", "Residuos de Maleza"],
    "Cantidad (toneladas)": [selected_residuos_dom, selected_residuos_alimentos, selected_residuos_maleza]
}

# Convertir a DataFrame y mostrar como tabla
residuos_df = pd.DataFrame(residuos_data)
st.subheader(f'Detalles de residuos para {selected_departamento}')
st.table(residuos_df)

