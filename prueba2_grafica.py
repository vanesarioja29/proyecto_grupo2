import streamlit as st
import pandas as pd
import altair as alt
st.title("Bienvenidos a este repositorio sin imaginacion")
st.write("Hola **como** estas")

grafica = pd.DataFrame({"category": [1, 2, 3, 4, 5, 6], "value": [4, 5, 10, 3, 7, 8]})

c = alt.Chart(grafica).mark_arc().encode(theta="value", color="category")

st.altair_chart(c)
