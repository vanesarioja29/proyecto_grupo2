import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el shapefile de los departamentos de Perú
shapefile_path = '/workspaces/proyecto_grupo2/Departamental.shp'  # Asegúrate de usar la ruta correcta
gdf_departamentos = gpd.read_file(shapefile_path)
gdf_departamentos.rename(columns={'DEPARTAMEN': 'DEPARTAMENTO'}, inplace=True)

# Cargar los datos de residuos (debes asegurarte de tener el archivo CSV)
data_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  # Ruta al archivo CSV de residuos
data = pd.read_csv(data_path, encoding='ISO-8859-1', delimiter=';')

# Preprocesamiento: Convertir las columnas relevantes a tipos numéricos
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Agrupar por departamento
data_grouped = data.groupby('DEPARTAMENTO').sum().reset_index()

# Fusionar los datos con la geometría de los departamentos
#gdf_merged = gdf_departamentos.merge(data_grouped, left_on='DEPARTAMENTO', right_on='DEPARTAMENTO')
gdf_merged = gdf_departamentos.merge(data_grouped, on='DEPARTAMENTO')

# Título de la aplicación
st.title('Mapa Interactivo de Residuos por Departamento')

# Visualización del mapa con GeoPandas
st.subheader('Mapa de Residuos por Departamento')

# Crear un gráfico con GeoPandas
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
gdf_merged.plot(column='QRESIDUOS_DOM', ax=ax, legend=True,
                legend_kwds={'label': "Cantidad de Residuos Domésticos por Departamento",
                             'orientation': "horizontal"})
ax.set_title('Mapa de Residuos por Departamento')

# Mostrar el mapa
st.pyplot(fig)

# Mostrar algunos datos filtrados como tabla
st.subheader('Datos Filtrados')
st.write(gdf_merged[['DEPARTAMENTO', 'QRESIDUOS_DOM', 'QRESIDUOS_ALIMENTOS', 'QRESIDUOS_MALEZA']])
