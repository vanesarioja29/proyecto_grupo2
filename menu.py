import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static

def generar_grafico_circular(departamento, datos):
    selected_data = datos[datos['DEPARTAMENTO'] == departamento].iloc[0, 1:]
    selected_data = selected_data[selected_data > 0]
    selected_data = selected_data.sort_values(ascending=False)
    
    if len(selected_data) > 5:
        top_residuos = selected_data[:5]
        others = selected_data[5:].sum()
        top_residuos["Otros"] = others
    else:
        top_residuos = selected_data

    fig = px.pie(
        names=top_residuos.index,
        values=top_residuos.values,
        title=f"Composición de los residuos más comunes por Departamento",
        hole=0.3
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=12,
        pull=[0.1]*len(top_residuos),
        hovertemplate="<b>%{label}</b><br>Valor: %{value:,.2f} Tn<extra></extra>"
    )
    fig.update_layout(
        height=700,
        width=900,
        title_font_size=24,
        title_x=0.5,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.2
        )
    )
    return fig

# Configuración inicial de la app
st.set_page_config(page_title="Dashboard de Residuos en el Perú", layout="wide")
st.title("Dashboard Interactivo de Residuos en el Perú 🌎")

# Definir rutas constantes
data_path = 'D. Composición Anual de residuos domiciliarios_Distrital_2019_2022 (1).csv'
shapefile_path = 'Departamental.shp'
data = pd.read_csv(data_path, encoding='ISO-8859-1', delimiter=';')
gdf_departamentos = gpd.read_file(shapefile_path)

# Crear el menú de navegación
selected_option = option_menu(
    menu_title=None,
    options=["Introducción", "Data", "Mapas", "Gráfico Circular", "Gráfico de barras", "Sobre Nosotros"],  # Opciones del menú
    icons=["house", "table", "map", "pie-chart", "bar-chart", "people"],  # Iconos de las opciones
    default_index=0,
    orientation="horizontal" 
)

# Lógica del menú
if selected_option == "Introducción":
    st.subheader("Análisis y Visualización de la Composición de Residuos Sólidos Domiciliarios - Perú")
    st.write("""
    Este proyecto tiene como objetivo ofrecer una **visualización interactiva** de la composición de residuos sólidos 
    domiciliarios en Perú, utilizando datos provenientes del Sistema de Información para la Gestión de los Residuos 
    Sólidos – **SIGERSOL** y los **Estudios de Caracterización de Residuos Sólidos Municipales (EC-RSM)**, que han sido 
    estandarizados desde 2019.
    """)

    st.markdown("### ¿Qué son los Residuos Sólidos Domiciliarios?")
    st.write("""
    Los **residuos sólidos domiciliarios** son aquellos generados en los hogares como resultado del consumo o uso de 
    bienes y servicios. Este proyecto visualiza la **distribución de estos residuos**, que incluyen plásticos, metales, 
    papeles, materia orgánica, entre otros, desglosados por tipo de residuo y cantidad en **toneladas**.

    La base de datos es crucial para los gobiernos locales, quienes utilizan esta información para gestionar 
    adecuadamente los residuos y formular políticas públicas en pro de la **gestión sostenible** y la **reducción de residuos**.
    """)

    st.markdown("### Fuentes de Información")
    st.write("""
    1. **SIGERSOL**: Sistema administrado por el Ministerio del Ambiente, que recolecta anualmente los reportes de 
       gestión de residuos de las municipalidades.
    2. **Estudios de Caracterización**: Realizados desde el año 2019, siguiendo los lineamientos establecidos por el 
       Ministerio del Ambiente para caracterizar los residuos sólidos municipales.
    """)

    st.markdown("### Visualización Interactiva")
    st.write("""
    A través de este **Dashboard Interactivo**, hemos creado herramientas visuales que te permitirán explorar y analizar 
    datos sobre los residuos sólidos generados en cada rincón del Perú. Podrás:
    - Consultar gráficos interactivos que destacan los tipos de residuos más comunes en cada departamento.
    - Explorar mapas visuales que muestran la distribución geográfica de los residuos.
    - Descubrir datos organizados en tablas interactivas que facilitan la exploración de la base de datos.

    ¡Navega por las diferentes secciones del menú para obtener una perspectiva clara y dinámica sobre cómo se gestionan 
    los residuos en el Perú! 🌟
    """)

elif selected_option == "Data":
    st.subheader("Data - Exploración de la Base de Datos")
    
    # Filtrar las columnas relevantes (hasta "PERIODO")
    data = data.loc[:, :'PERIODO']
    
    # Eliminar las filas no deseadas (7528 y 7529)
    data = data.drop(index=[7528, 7529], errors='ignore')
    
    st.write("A continuación, puedes explorar la base de datos de residuos de forma interactiva:")
    # Crear filtros interactivos
    periodos = sorted(data['PERIODO'].dropna().unique())
    periodos = [int(p) for p in periodos]
    selected_periodo = st.selectbox("Selecciona el Periodo", periodos, index=0)

    departamentos = sorted(data['DEPARTAMENTO'].dropna().unique())
    selected_departamento = st.selectbox("Selecciona el Departamento", departamentos, index=0)

    # Filtrar provincias dinámicamente según el departamento
    provincias = sorted(data[data['DEPARTAMENTO'] == selected_departamento]['PROVINCIA'].dropna().unique())
    selected_provincia = st.selectbox("Selecciona la Provincia", provincias, index=0)

    # Filtrar los datos según los criterios seleccionados
    filtered_data = data[
        (data['PERIODO'] == selected_periodo) &
        (data['DEPARTAMENTO'] == selected_departamento) &
        (data['PROVINCIA'] == selected_provincia)
    ]

    st.write("Filtrando datos según el periodo, departamento y provincia seleccionados:")
    st.dataframe(filtered_data)

elif selected_option == "Mapas":
    st.subheader("Mapas Interactivos de Residuos en el Perú")
    st.write("""
    En esta sección, puedes explorar dos tipos de mapas:
    - **Mapa Interactivo por Departamento:** Muestra un marcador con información detallada sobre los residuos domésticos, de alimentos y maleza generados en cada departamento.
    - **Mapa Coroplético:** Representa los residuos totales generados en cada departamento con un esquema de colores que varía según la cantidad de toneladas.

    ¡Interactúa con los mapas para conocer más detalles! 🌍
    """)

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
        columns=["DEPARTAMENTO", "TOTAL_RESIDUOS"],
        key_on="feature.properties.DEPARTAMENTO",
        fill_color="YlOrRd",  # Escala de colores (amarillo a rojo)
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Toneladas de Residuos Totales",
        bins=12,  # 12 intervalos
        highlight=True,
        nan_fill_opacity=0,
        overlay=True,
    ).add_to(map_right)

    # Popup que solo muestre el dato total de residuos
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
    col1, col2, col3 = st.columns([1, 0.1, 1])

    with col1:
        st.subheader("Mapa Interactivo por Departamento")
        folium_static(map_left)

    with col3:
        st.subheader("Mapa Corplético y total de residuos")
        folium_static(map_right)


elif selected_option == "Gráfico Circular":
    st.subheader("Gráfico Circular - Composición de Residuos")

    st.markdown("""
    En esta sección, podrás explorar la **composición de residuos sólidos** generados en los diferentes departamentos del Perú, 
    visualizados a través de un gráfico circular. Este gráfico muestra los **5 tipos de residuos más comunes** en un departamento 
    específico, permitiéndote analizar la distribución de residuos domiciliarios, plásticos, alimentos, maleza, entre otros, 
    en términos de **toneladas** generadas.
    
    Selecciona un departamento del Perú para ver los detalles sobre los residuos que se generan allí. 🌱

    """)
    
    residuos_columns = [col for col in data.columns if col.startswith('QRESIDUOS_')]
    residuos_columns.insert(0, 'DEPARTAMENTO')
    filtered_data = data[residuos_columns]

    for col in residuos_columns[1:]:
        filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

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
    grouped_data = filtered_data.groupby('DEPARTAMENTO').sum().reset_index()

    departamentos = grouped_data['DEPARTAMENTO'].unique()
    selected_departamento = st.selectbox("Seleccione un Departamento:", sorted(departamentos))
    fig = generar_grafico_circular(selected_departamento, grouped_data)
    st.plotly_chart(fig)

elif selected_option == "Gráfico de barras":
    st.subheader("Distribución de Residuos por Distrito")
    st.markdown("""
    En esta sección, se muestra la **distribución de residuos** en los distritos seleccionados,
    en función del departamento y provincia de interés. 🌎
    """)

    # Filtrar datos relevantes
    periodos = sorted(data['PERIODO'].dropna().unique())
    periodos = [int(p) for p in periodos]
    selected_periodo = st.selectbox("Selecciona el Periodo", periodos, index=0)

    departamentos = sorted(data['DEPARTAMENTO'].dropna().unique())
    selected_departamento = st.selectbox("Selecciona el Departamento", departamentos, index=0)

    provincias = sorted(data[data['DEPARTAMENTO'] == selected_departamento]['PROVINCIA'].dropna().unique())
    selected_provincia = st.selectbox("Selecciona la Provincia", provincias, index=0)

    # Filtrar datos según las selecciones
    distritos_data = data[
        (data['PERIODO'] == selected_periodo) &
        (data['DEPARTAMENTO'] == selected_departamento) &
        (data['PROVINCIA'] == selected_provincia)
    ]

    # Seleccionar residuos para la gráfica
    residuos_columns = [col for col in data.columns if col.startswith('QRESIDUOS_')]
    distritos_data['TOTAL_RESIDUOS'] = distritos_data[residuos_columns].sum(axis=1)

    # Crear gráfica de barras
    if not distritos_data.empty:
        fig_distritos = px.bar(
            distritos_data,
            x="DISTRITO",
            y="TOTAL_RESIDUOS",
            text="TOTAL_RESIDUOS",
            color="DISTRITO",
            labels={"DISTRITO": "Distrito", "TOTAL_RESIDUOS": "Toneladas de Residuos (Tn)"},
            title=f"Residuos generados por distrito en {selected_departamento} - {selected_provincia}",
        )
        fig_distritos.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_distritos.update_layout(
            showlegend=False,
            height=600,
            width=900,
            xaxis_tickangle=-45,
            title_x=0.5,
            margin=dict(l=20, r=20, t=50, b=100),
        )
        st.plotly_chart(fig_distritos)
    else:
        st.warning("No se encontraron datos para los filtros seleccionados.")

elif selected_option == "Sobre Nosotros":
    st.markdown("### ¿QUIÉNES SOMOS?")
    st.write("""
    Somos un grupo de estudiantes de la universidad peruana Cayetano Heredia, a continuación, una breve descripción de cada uno de nosotros:
    """)

    st.markdown("### Vanesa Rioja Cruz")
    st.write("""   
        - Facultad de Ciencias e Ingeniería
        - CARRERA: Ing. informática
        - Me gusta leer libros y viajar 📚 ✈️
        - Estoy interesada en tecnologías de inteligencia artificial 🖥️
        - Correo de contacto: vanesa.rioja@upch.pe
             
    """)
    st.markdown("### Jander Huamani Salazar")
    st.write("""
        - Facultad de Ciencias e Ingeniería
        - CARRERA: Ing. informática
        - Me interesa la inteligencia artificial y programación de videojuegos 🖥️ 🕹️
        - Correo de contacto: jander.huamani@upch.pe
             
    """)

    st.markdown("### Said Andre Quispe Diaz ")
    st.write("""
        - Facultad de Ciencias e Ingeniería
        - CARRERA: Ing. Ambiental
        - Amante de los animales, musica, animación y videojuegos 🐕‍🦺 🎼 
        - Me interesa la protección y preservación de áreas naturales 🌳
        - Correo de contacto: said.quispe@upch.pe
             
    """)

    st.markdown("### Victor Daniel Rivera Torres ")
    st.write("""
        - Facultad de Ciencias e Ingeniería
        - CARRERA: Ingeniería Informática 
        - Quiero pasar Ecuaciones Diferenciales / Comer chifita / Estudios Bioinformáticos 🥴 🍜
        - Correo de contacto: victor.rivera@upch.pe
             
    """)
