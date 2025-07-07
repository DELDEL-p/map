

import streamlit as st
import pandas as pd
import numpy as np
import folium
from pykrige.ok import OrdinaryKriging
from folium import plugins
from streamlit_folium import folium_static

st.title("🌏 PGA Map with Kriging Interpolation")

# [1] Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file with PGA data", type=['xlsx'])
if uploaded_file is not None:

    # [2] Read data
    df = pd.read_excel(uploaded_file)
    st.write("### Raw Data", df.head())

    lon = df['Lon'].values
    lat = df['Lat'].values
    pga = df.iloc[:,2].values

    # [3] Create grid
    grid_lon = np.linspace(lon.min(), lon.max(), 100)
    grid_lat = np.linspace(lat.min(), lat.max(), 100)
    grid_lon_mesh, grid_lat_mesh = np.meshgrid(grid_lon, grid_lat)

    # [4] Perform Kriging
    OK = OrdinaryKriging(lon, lat, pga, variogram_model='spherical', verbose=False, enable_plotting=False)
    z, ss = OK.execute('grid', grid_lon, grid_lat)

    # [5] Identify peak PGA
    peak_idx = np.argmax(pga)
    peak_lon = lon[peak_idx]
    peak_lat = lat[peak_idx]
    peak_pga = pga[peak_idx]

    # [6] Create Folium map
    m = folium.Map(location=[peak_lat, peak_lon], zoom_start=8)

    # [7] Add peak marker
    folium.Marker(
        [peak_lat, peak_lon],
        popup=f"Peak PGA: {peak_pga:.3f}%g",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    # [8] Add Kriging heatmap (approximate aura)
    heat_data = []
    for i in range(len(grid_lat)):
        for j in range(len(grid_lon)):
            heat_data.append([grid_lat[i], grid_lon[j], z[i,j]])

    plugins.HeatMap(heat_data, radius=25, blur=15, max_zoom=1).add_to(m)

    # [9] Display map
    folium_static(m)

else:
    st.info("Please upload an Excel file to continue.")
