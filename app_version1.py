import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
file_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'  # Cambia la ruta según donde tengas el archivo
data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Preprocesamiento: Convertir las columnas que son de interés a tipos numéricos cuando sea necesario
data['QRESIDUOS_DOM'] = pd.to_numeric(data['QRESIDUOS_DOM'], errors='coerce')
data['QRESIDUOS_ALIMENTOS'] = pd.to_numeric(data['QRESIDUOS_ALIMENTOS'], errors='coerce')
data['QRESIDUOS_MALEZA'] = pd.to_numeric(data['QRESIDUOS_MALEZA'], errors='coerce')

# Título de la aplicación
st.title('Dashboard de Residuos')

# Filtro de Región
region = st.selectbox('Selecciona la Región', data['REG_NAT'].unique())

# Filtro de Departamento
departamento = st.selectbox('Selecciona el Departamento', data[data['REG_NAT'] == region]['DEPARTAMENTO'].unique())

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

# Filtrar los datos según los filtros seleccionados
filtered_data = data[(data['REG_NAT'] == region) & (data['DEPARTAMENTO'] == departamento)]

# Visualización de los residuos
st.subheader(f'Gráfica de {tipo_residuo} por Distrito')

# Graficar la cantidad de residuos por distrito
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(filtered_data['DISTRITO'], filtered_data[tipo_residuo])
ax.set_xlabel('Distrito')
ax.set_ylabel('Cantidad de Residuos')
ax.set_title(f'{tipo_residuo} en la Región {region}, Departamento {departamento}')

# Mostrar la gráfica
st.pyplot(fig)

# Mostrar algunos datos filtrados como tabla
st.subheader('Datos Filtrados')
st.write(filtered_data[['DISTRITO', tipo_residuo]])

