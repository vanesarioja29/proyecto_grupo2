import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuración inicial de la app
st.set_page_config(page_title="Dashboard de Residuos", layout="wide")

# Rutas de los archivos
shapefile_path = '/workspaces/proyecto_grupo2/Departamental.shp'
data_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'

# Archivos hapefile y CSV
gdf_departamentos = gpd.read_file(shapefile_path)
data = pd.read_csv(data_path, encoding='ISO-8859-1', delimiter=';')

# Renombrar columna en el GeoDataFrame
gdf_departamentos.rename(columns={'DEPARTAMEN': 'DEPARTAMENTO'}, inplace=True)

# Verificar y establecer CRS en el shapefile
if gdf_departamentos.crs is None:
    gdf_departamentos.set_crs(epsg=4326, inplace=True)
else:
    gdf_departamentos = gdf_departamentos.to_crs(epsg=4326)

# Preprocesar datos
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Crear columna de residuos totales y agrupar por departamento
data['TOTAL_RESIDUOS'] = data['QRESIDUOS_DOM'] + data['QRESIDUOS_ALIMENTOS'] + data['QRESIDUOS_MALEZA']
data_grouped = data.groupby('DEPARTAMENTO').sum().reset_index()

# Fusionar datos geográficos con residuos
gdf_merged = gdf_departamentos.merge(data_grouped, on='DEPARTAMENTO')

# Mapa interactivo (izquierda)
map_left = folium.Map(location=[-9.19, -75.015], zoom_start=5)
for _, row in gdf_merged.iterrows():
    lat, lon = row['geometry'].centroid.y, row['geometry'].centroid.x
    popup_text = f"""
    <strong>{row['DEPARTAMENTO']}</strong><br>
    Residuos Domésticos: {format(round(row['QRESIDUOS_DOM'], 2), ',')} Tn<br>
    Residuos de Alimentos: {format(round(row['QRESIDUOS_ALIMENTOS'], 2), ',')} Tn<br>
    Residuos de Maleza: {format(round(row['QRESIDUOS_MALEZA'], 2), ',')} Tn
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(map_left)

# Mapa de colorimetría (derecha)
map_right = folium.Map(location=[-9.19, -75.015], zoom_start=5)

# Crear la capa Choropleth para colorear los departamentos según los residuos
choropleth = folium.Choropleth(
    geo_data=gdf_merged,
    name="Residuos Totales",
    data=gdf_merged,
    columns=["DEPARTAMENTO", "TOTAL_RESIDUOS"],  # Usamos el total de residuos
    key_on="feature.properties.DEPARTAMENTO",  # Coincidir con la propiedad del shapefile
    fill_color="YlOrRd",  # Escala de colores (amarillo a rojo)
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Toneladas de Residuos Totales",
    bins=12,  # Aseguramos que haya 12 intervalos
    highlight=True,  # Resaltar los departamentos cuando pasas el ratón por encima
    nan_fill_opacity=0,  # Opcional: para dejar los valores faltantes sin color
    overlay=True,
).add_to(map_right)

# Añadir los departamentos al mapa con un popup que solo muestre el dato total de residuos
for idx, row in gdf_merged.iterrows():
    lat, lon = row['geometry'].centroid.y, row['geometry'].centroid.x
    residuos_total = format(round(row['TOTAL_RESIDUOS'], 2), ',')

    popup_text = f"""
    <strong>{row['DEPARTAMENTO']}</strong><br>
    Residuos Totales: {residuos_total} Tn
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(map_right)

# Dividir en columnas para mostrar los mapas
col1, col2, col3 = st.columns([1, 0.1, 1])  # Espacio en el medio para separar mapas

with col1:
    st.subheader("Mapa Interactivo por Departamento")
    folium_static(map_left)

with col3:
    st.subheader("Mapa con Colorimetría y Total de Residuos")
    folium_static(map_right)
