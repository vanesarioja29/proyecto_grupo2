import streamlit as st
import pandas as pd
import plotly.express as px

# Función para generar el gráfico circular interactivo
def generar_grafico_circular(departamento, datos):
    # Filtrar los datos del departamento seleccionado
    selected_data = datos[datos['DEPARTAMENTO'] == departamento].iloc[0, 1:]
    selected_data = selected_data[selected_data > 0]  # Excluir columnas con valor 0

    # Ordenar los datos por cantidad en toneladas, descendente
    selected_data = selected_data.sort_values(ascending=False)

    # Limitar a los 5 residuos más grandes y agrupar el resto como "Otros"
    if len(selected_data) > 5:
        top_residuos = selected_data[:5]  # Tomar los 5 residuos más grandes
        others = selected_data[5:].sum()  # Sumar el resto como "Otros"
        top_residuos["Otros"] = others
    else:
        top_residuos = selected_data

    # Crear la gráfica circular con Plotly
    fig = px.pie(
        names=top_residuos.index,
        values=top_residuos.values,
        title=f"Composición de los residuos más comunes en {departamento}",
        hole=0.3  # Opcional: Gráfico tipo dona
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=12,
        pull=[0.1]*len(top_residuos),
        hovertemplate="<b>%{label}</b><br>Valor: %{value:,.2f} Tn<extra></extra>"  # Mensaje emergente personalizado
    )
    fig.update_layout(
        legend_itemclick=False,  # Deshabilitar click para ocultar
        legend_itemdoubleclick=False,  # Deshabilitar doble click
        height=700,  # Ajustar altura del gráfico
        width=900,   # Ajustar ancho del gráfico
        title_font_size=24,
        title_x=0.5,  # Centrar el título
        legend=dict(
            orientation="v",  # Cambiar la orientación a vertical
            yanchor="middle",  # Alinear verticalmente con el gráfico
            y=0.5,             # Posicionar en el centro vertical
            xanchor="right",   # Alinear horizontalmente al borde del gráfico
            x=1.2              # Ajustar la distancia al gráfico
        )
    )
    return fig

# Configuración inicial de la app
st.set_page_config(page_title="Dashboard de Residuos - Gráficas Interactivas", layout="wide")
st.title("Residuos mas comunes por departamento en el Perú 🌎")

# Introducción breve
st.write("""
Selecciona un departamento de la lista desplegable para descubrir los **5 tipos de residuos más destacados** y su proporción en toneladas.
""")

# Cargar los datos procesados
file_path = '/workspaces/proyecto_grupo2/D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'
data = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Filtrar las columnas relevantes
residuos_columns = [col for col in data.columns if col.startswith('QRESIDUOS_')]
residuos_columns.insert(0, 'DEPARTAMENTO')  # Asegurarse de incluir el departamento
filtered_data = data[residuos_columns]

# Convertir las columnas de residuos a numéricas
for col in residuos_columns[1:]:
    filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

# Mapear nombres de columnas a etiquetas amigables
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
}

filtered_data.rename(columns=residuos_mapping, inplace=True)

# Agrupar los datos por departamento
grouped_data = filtered_data.groupby('DEPARTAMENTO').sum().reset_index()

# Selección del departamento
departamentos = grouped_data['DEPARTAMENTO'].unique()
selected_departamento = st.selectbox("Seleccione un Departamento:", sorted(departamentos))

# Generar y mostrar el gráfico circular interactivo
fig = generar_grafico_circular(selected_departamento, grouped_data)
st.plotly_chart(fig)
