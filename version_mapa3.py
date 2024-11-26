import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import branca

# Cargar el shapefile de los departamentos de Perú
shapefile_path = '/workspaces/proyecto_grupo2/Departamental.shp'
gdf_departamentos = gpd.read_file(shapefile_path)

# Verificar si el CRS está definido, si no, asignarlo
if gdf_departamentos.crs is None:
    gdf_departamentos.set_crs('EPSG:4326', allow_override=True, inplace=True)
else:
    gdf_departamentos = gdf_departamentos.to_crs('EPSG:4326')

# Cargar los datos de residuos
data_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'
data = pd.read_csv(data_path, encoding='ISO-8859-1', delimiter=';')

# Preprocesamiento: convertir a numérico, reemplazando errores por NaN
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Agrupar por departamento sumando los residuos domésticos, de alimentos y de maleza
data['TOTAL_RESIDUOS'] = data['QRESIDUOS_DOM'] + data['QRESIDUOS_ALIMENTOS'] + data['QRESIDUOS_MALEZA']
data_grouped = data.groupby('DEPARTAMENTO').sum().reset_index()

# Renombrar columna en el GeoDataFrame
gdf_departamentos.rename(columns={'DEPARTAMEN': 'DEPARTAMENTO'}, inplace=True)

# Fusionar los datos con la geometría de los departamentos
gdf_merged = gdf_departamentos.merge(data_grouped, on='DEPARTAMENTO')

# Verificar que 'TOTAL_RESIDUOS' son valores numéricos y descartar NaN
gdf_merged['TOTAL_RESIDUOS'] = pd.to_numeric(gdf_merged['TOTAL_RESIDUOS'], errors='coerce')
gdf_merged = gdf_merged.dropna(subset=['TOTAL_RESIDUOS'])

# Verificación de que los valores numéricos no contienen cadenas de texto
if gdf_merged['TOTAL_RESIDUOS'].dtype != 'float64':
    st.error('Error: La columna "TOTAL_RESIDUOS" contiene valores no numéricos.')
    st.stop()

# Crear mapa base
m = folium.Map(location=[-9.19, -75.015], zoom_start=5)

# Definir los 12 colores manualmente
colors = [
    "#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026", 
    "#d9f0a3", "#addd8e", "#78c679", "#31a354", "#006837"
]

# Establecer valores min y max de residuos
vmin = gdf_merged['TOTAL_RESIDUOS'].min()
vmax = gdf_merged['TOTAL_RESIDUOS'].max()

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
).add_to(m)

# Añadir los departamentos al mapa con un popup (opcional)
for idx, row in gdf_merged.iterrows():
    lat, lon = row['geometry'].centroid.y, row['geometry'].centroid.x
    residuos_total = round(row['TOTAL_RESIDUOS'], 2)
    residuos_dom = round(row['QRESIDUOS_DOM'], 2)
    residuos_alimentos = round(row['QRESIDUOS_ALIMENTOS'], 2)
    residuos_maleza = round(row['QRESIDUOS_MALEZA'], 2)

    popup_text = f"""
    <strong>{row['DEPARTAMENTO']}</strong><br>
    Residuos Totales: {residuos_total} Tn<br>
    Residuos Domésticos: {residuos_dom} Tn<br>
    Residuos de Alimentos: {residuos_alimentos} Tn<br>
    Residuos de Maleza: {residuos_maleza} Tn
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Mostrar mapa
folium_static(m)

# Selección del departamento
selected_departamento = st.selectbox('Selecciona un Departamento:', gdf_merged['DEPARTAMENTO'])

# Mostrar detalles
selected_data = gdf_merged[gdf_merged['DEPARTAMENTO'] == selected_departamento]
selected_residuos_total = round(selected_data['TOTAL_RESIDUOS'].values[0], 2)
selected_residuos_dom = round(selected_data['QRESIDUOS_DOM'].values[0], 2)
selected_residuos_alimentos = round(selected_data['QRESIDUOS_ALIMENTOS'].values[0], 2)
selected_residuos_maleza = round(selected_data['QRESIDUOS_MALEZA'].values[0], 2)

# Mostrar en tabla interactiva
residuos_data = {
    "Tipo de Residuo": ["Residuos Totales", "Residuos Domésticos", "Residuos de Alimentos", "Residuos de Maleza"],
    "Cantidad (toneladas)": [selected_residuos_total, selected_residuos_dom, selected_residuos_alimentos, selected_residuos_maleza]
}

residuos_df = pd.DataFrame(residuos_data)
st.subheader(f'Detalles de residuos para {selected_departamento}')
st.dataframe(residuos_df)