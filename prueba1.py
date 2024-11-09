import pandas as pd
import numpy as np
import streamlit as st

st.title("Proyecto Programación")
n = st.slider("n", 5, 100, step=1)
chart_data = pd.DataFrame(np.random.randn(n), columns=['data'])
st.line_chart(chart_data)

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])
st.map(df)

#hola
