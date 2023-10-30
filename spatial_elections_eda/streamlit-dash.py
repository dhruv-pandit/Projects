# Import necessary libraries
import streamlit as st
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import pandas as pd
from sklearn.decomposition import PCA

# Load the data
@st.cache_data
def load_data():
    new_gdf = gpd.read_file(r'/Users/dhruvpandit/Documents/GitHub/Projects/spatial_elections_eda/Dataset/V11.shp')
    return new_gdf.copy()  # Return a copy to ensure the original is not mutated

# Scale the data
@st.cache_data
def scale_data(_new_gdf):
    from sklearn.preprocessing import StandardScaler
    gdf_demo_scal = _new_gdf.copy()

    #gdf_demo_scal = new_gdf.copy()
    # ... [rest of your scaling code here]
    return gdf_demo_scal


# Main function to run the app
def main():
    st.title("Spatial Exploration of 2019 Portuguese Elections")
    st.write("""
    * Contact at dhruvpandit@aln.iseg.ulisboa.pt
    """)
    # Load and scale data
    new_gdf = load_data()
    new_gdf = new_gdf.to_crs("EPSG:4326")
    gdf_demo_scal = scale_data(new_gdf)

    # Dropdown to select variable for choropleth
    option = st.selectbox(
        'Select a Variable for Visualization:',
        ('PPindex202', 'Mhousesqm', 'M0_14', 'M15_24', 'M25_64', 'M65', 'F0_14', 'F15_24', 'F25_64', 'F65',
         'TOTALPOP', 'Voters', 'Votepct', 'DVotepct', 'DOBN',
         'Centre_l_tvote', 'Centre_r_tvote', 'Left_tvote', 'Right_tvote')
    )

    # Display choropleth map using folium
    m = folium.Map(location=[39.4, -8.2], zoom_start=6)  # Location is roughly the center of Portugal

    choropleth = folium.Choropleth(
        geo_data=gdf_demo_scal,
        name="choropleth",
        data=gdf_demo_scal,
        columns=["concelhos_", option],
        key_on="feature.properties.concelhos_",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=option
    ).add_to(m)

    #folium.LayerControl().add_to(m)
    st_folium(m)
    #folium_static(m)
    # Dropdown for selecting X and Y variables
    st.write("""
    ## Scatter Plot Visualization for Numeric Variables
    """)
    numeric_cols = gdf_demo_scal.select_dtypes(exclude=['object'])
    df_scatter = gdf_demo_scal[numeric_cols.columns]
    # Drop non-numeric columns
    df_scatter = df_scatter.select_dtypes(include=['float64', 'int64'])
    df_scatter.dropna(inplace = True)
    df_scatter.drop(columns = ['TOTALPOP', 'Voters', 'DOBN', 'To I p Ca', 'Non fin en', 'Votepct_we',
       'Left_w', 'Centre_w', 'Right_w', 'Centre_l_w', 'Centre_r_w',
       'DVotepct_w', 'Personel E', 'Inhb per F', 'For Pop (%', 'Env Pr Cap'], axis = 1, inplace = True)
    x_var = st.selectbox('Select X variable:', df_scatter.columns)
    y_var = st.selectbox('Select Y variable:', df_scatter.columns)

    # Scatter plot using Plotly
    fig_scatter = px.scatter(df_scatter, x=x_var, y=y_var)
    st.plotly_chart(fig_scatter)
    st.write("""
    ## Correlation Matrix for Numeric Variables
    """)
    # Correlation matrix using Plotly
    corr_matrix = df_scatter.corr()
    fig_corr = px.imshow(corr_matrix, color_continuous_scale='RdBu')
    st.plotly_chart(fig_corr)

    num_components = st.slider('Select number of principal components:', 1, 20)
    st.write("""
    # Principal Component Analysis for Numeric Variables
    * Select the number of components you are interested in analyzing. 
    """)
    # Applying PCA

    pca = PCA(n_components=num_components)
    components = pca.fit_transform(df_scatter)
    st.write("""
    ## Bar Plot for Explained Variance
    """)
    # Bar plot for explained variance
    explained_var = pca.explained_variance_ratio_
    fig_variance = px.bar(x=[f'PC{i+1}' for i in range(num_components)], y=explained_var, labels={'x':'Principal Component', 'y':'Explained Variance'})
    st.plotly_chart(fig_variance)
    st.write("""
    ## Select Principal Component to Visualise Loadings
    """)
    # Dropdown to select a specific principal component for loadings plot
    selected_pc = st.selectbox('Select principal component for loadings plot:', [f'PC{i+1}' for i in range(num_components)])
    selected_index = int(selected_pc[2:]) - 1  # Convert PC label to index

    # Bar plot for loadings of the chosen principal component
    loadings = pca.components_[selected_index]
    fig_loadings = px.bar(x=df_scatter.columns, y=loadings, labels={'x':'Feature', 'y':'Loading'})
    st.plotly_chart(fig_loadings)

if __name__ == "__main__":
    main()
