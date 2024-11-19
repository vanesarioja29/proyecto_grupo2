import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math  # Para usar funciones trigonométricas

# Cargar el archivo CSV
file_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'
data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Filtrar las columnas relevantes (aquellas que comienzan con 'QRESIDUOS_')
residuos_columns = [col for col in data.columns if col.startswith('QRESIDUOS_')]
residuos_columns.insert(0, 'DEPARTAMENTO')  # Asegurarse de incluir el departamento
filtered_data = data[residuos_columns]

# Convertir las columnas de residuos a numéricas y excluir NaN
for col in residuos_columns[1:]:  # Excluyendo 'DEPARTAMENTO'
    filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

# Mapear los nombres de residuos a etiquetas más amigables
residuos_mapping = {
    "QRESIDUOS_DOM": "Domiciliarios",
    "QRESIDUOS_BOLSAS_PLASTICAS": "Bolsas Plásticas",
    "QRESIDUOS_ALIMENTOS": "Alimentos",
    "QRESIDUOS_MALEZA": "Maleza",
    "QRESIDUOS_TECNOPOR": "Tecnopor",
    "QRESIDUOS_SANITARIOS": "Sanitarios",
    "QRESIDUOS_OTROS_ORGANICOS": "Otros orgánicos",
    "QRESIDUOS_PAPEL_BLANCO": "Papel Blanco",
    "QRESIDUOS_PAPEL_PERIODICO": "Papel Periódico",
    "QRESIDUOS_PAPEL_MIXTO": "Papel Mixto",
    "QRESIDUOS_CARTON_BLANCO": "Cartón Blanco",
    "QRESIDUOS_CARTON_MARRON": "Cartón Marrón",
    "QRESIDUOS_CARTON_MIXTO": "Cartón Mixto",
    "QRESIDUOS_OTROS_NO_CATEGORIZADOS": "No categorizados",
    "QRESIDUOS_CAUCHO_CUERO": "Caucho cuero",
    "QRESIDUOS_PILAS": "Pilas",
    "QRESIDUOS_TEREFLATO_POLIETILENO": "Tereflato polietileno",
    "QRESIDUOS_INERTES": "Inertes",
    "QRESIDUOS_POLIETILENO_ALTA_DENSIDAD": "Polietileno alta densidad",
    "QRESIDUOS_LATA": "Lata",
    "QRESIDUOS_VIDRIO_TRANSPARENTE": "Vidrio transparente",
    "QRESIDUOS_TEXTILES": "Textiles"
    # Agrega más mapeos aquí según sea necesario...
}


# Renombrar las columnas con etiquetas amigables
filtered_data.rename(columns=residuos_mapping, inplace=True)

# Agrupar por departamento y sumar los valores de residuos
grouped_data = filtered_data.groupby('DEPARTAMENTO').sum().reset_index()

# Configuración inicial de la app
st.set_page_config(page_title="Dashboard de Residuos - Gráficas Circulares", layout="wide")

# Título del dashboard
st.title("Dashboard de Residuos - Gráficas Circulares")
st.write("Seleccione un departamento para visualizar los tipos de residuos generados.")

# Selección del departamento
departamentos = grouped_data['DEPARTAMENTO'].unique()
selected_departamento = st.selectbox("Seleccione un Departamento:", sorted(departamentos))

# Filtrar datos del departamento seleccionado y eliminar columnas con valor 0
selected_data = grouped_data[grouped_data['DEPARTAMENTO'] == selected_departamento].iloc[0, 1:]
selected_data = selected_data[selected_data > 0]  # Excluir columnas con valor 0

# Ordenar los datos por cantidad en toneladas, descendente
selected_data = selected_data.sort_values(ascending=False)

# Limitar a los 8 residuos más grandes y agrupar el resto como "Otros"
if len(selected_data) > 8:
    top_residuos = selected_data[:8]  # Tomar los 8 residuos más grandes
    others = selected_data[8:].sum()  # Sumar el resto como "Otros"
    top_residuos["Otros"] = others
else:
    top_residuos = selected_data

# Crear la gráfica circular
labels = top_residuos.index
values = top_residuos.values

fig, ax = plt.subplots(figsize=(6, 6))  # Tamaño uniforme para todas las gráficas
wedges, texts, autotexts = ax.pie(
    values,
    labels=None,  # No mostrar etiquetas aquí
    autopct=lambda p: f'{p:.1f}%\n({p * sum(values) / 100:,.2f} Tn)',
    startangle=90,
    wedgeprops={'edgecolor': 'black'},
    textprops={'fontsize': 8}  # Reducir el tamaño del autotexto
)

# Agregar líneas guía y etiquetas externas
for i, (label, wedge) in enumerate(zip(labels, wedges)):
    angle = (wedge.theta2 + wedge.theta1) / 2
    x = math.cos(math.radians(angle)) * 1.4  # Aumentar el radio para etiquetas externas
    y = math.sin(math.radians(angle)) * 1.4
    connection_style = "arc3,rad=0.2"  # Estilo de conexión para una curva más pronunciada
    ax.annotate(
        label,
        xy=(math.cos(math.radians(angle)) * wedge.r, math.sin(math.radians(angle)) * wedge.r),
        xytext=(x, y),
        arrowprops=dict(arrowstyle="-", connectionstyle=connection_style, color='gray'),
        fontsize=9,  # Tamaño de fuente de las etiquetas externas
        ha="center",
        va="center"
    )

ax.axis('equal')  # Hacer el gráfico circular

# Mostrar la gráfica en el dashboard
st.subheader(f"Gráfica Circular de Residuos en {selected_departamento}")
st.pyplot(fig)

# Mostrar los valores numéricos también en formato tabular
st.write(f"**Valores en toneladas para {selected_departamento}:**")
residuos_table = pd.DataFrame({
    'Tipo de Residuo': labels,
    'Cantidad (Toneladas)': [f"{v:,.2f}" for v in values]
})
st.table(residuos_table)

