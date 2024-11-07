import streamlit as st
import numpy as np
import pandas as pd

n = st.slider('number of points', 0, 1000)

map_data = pd.DataFrame(
    np.random.randn(n, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)