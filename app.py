import os
import geopandas as gpd
import pandas as pd
import streamlit as st

# Función para cargar un archivo CSV
def cargar_csv(nombre_archivo):
    file_path = os.path.join(os.path.dirname(__file__), 'data', nombre_archivo)
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')
            return data
        except Exception as e:
            st.error(f"Error al cargar el archivo CSV: {e}")
            return None
    else:
        st.error(f"No se encontró el archivo CSV: {file_path}")
        return None

# Función para cargar un shapefile (.shp, .dbf, .shx)
def cargar_shapefile(nombre_shapefile):
    file_path = os.path.join(os.path.dirname(__file__), 'data', nombre_shapefile)
    if os.path.exists(file_path):
        try:
            data = gpd.read_file(file_path)
            return data
        except Exception as e:
            st.error(f"Error al cargar el archivo shapefile: {e}")
            return None
    else:
        st.error(f"No se encontró el archivo shapefile: {file_path}")
        return None

# Interfaz de Streamlit
st.title("Aplicación para Archivos CSV y Geoespaciales")
st.sidebar.title("Opciones")

# Cargar y mostrar un CSV
if st.sidebar.checkbox("Mostrar archivo CSV"):
    st.header("Datos CSV")
    # Nombre exacto del archivo CSV
    csv_file = "D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv"
    data_csv = cargar_csv(csv_file)
    if data_csv is not None:
        st.write(data_csv)

# Cargar y mostrar un shapefile
if st.sidebar.checkbox("Mostrar archivo Shapefile"):
    st.header("Datos Geoespaciales (Shapefile)")
    # Nombre exacto del archivo Shapefile
    shapefile = "Departamental.shp"
    shapefile_data = cargar_shapefile(shapefile)
    if shapefile_data is not None:
        st.write(shapefile_data)

        # Mostrar un mapa si el shapefile contiene geometría válida
        if not shapefile_data.empty and shapefile_data.geometry.is_valid.all():
            st.map(shapefile_data)
        else:
            st.warning("El shapefile no contiene geometría válida para mostrar en el mapa.")

# Nota sobre la estructura del proyecto
st.sidebar.info("Asegúrate de que los archivos estén en la carpeta 'data'.")
