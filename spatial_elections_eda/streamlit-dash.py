# Import necessary libraries
import streamlit as st
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import pandas as pd
from sklearn.decomposition import PCA
from pysal.explore import esda
from pysal.lib import weights
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

def weight_df(weight, gdf_demo_scal):
    knn_df = gdf_demo_scal.copy()
    for each in knn_df.columns:
        knn_df[each] = weights.spatial_lag.lag_spatial(
            weight, gdf_demo_scal["Centre_l"]
        )
    return knn_df
def show_choropleth(df_scatter,gdf_demo_scal, knn_df, selection):
    option = st.selectbox(df_scatter.columns)
    # Create two choropleth maps
    m1 = folium.Map(location=[39.4, -8.2], zoom_start=6)
    m2 = folium.Map(location=[39.4, -8.2], zoom_start=6)

    choropleth1 = folium.Choropleth(
        geo_data=gdf_demo_scal,
        name="choropleth",
        data=gdf_demo_scal,
        columns=["concelhos_", option],
        key_on="feature.properties.concelhos_",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=option
    ).add_to(m1)

    # You can customize the choropleth2 settings as needed
    choropleth2 = folium.Choropleth(
        geo_data=knn_df,
        name="choropleth",
        data=knn_df,
        columns=["concelhos_", option],  # Change 'option' to another column if needed
        key_on="feature.properties.concelhos_",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=option
    ).add_to(m2)

    # Create two columns to display the maps side by side
    col1, col2 = st.beta_columns(2)

    # Display the maps in the columns
    with col1:
        st.write("""
    ### Original Values Distribution
    """)
        st_folium(m1)

    with col2:
        st.write(f"""
    ### Spatially Lagged Values Distribution Using {selection}
    """)
        st_folium(m2)

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



    selection = st.radio("Choose a method:", ('KNN', 'Queen'))

    # If KNN is selected, display the slider
    if selection == 'KNN':
        knn_value = st.slider('Select KNN value:', min_value=3, max_value=8)
        st.write(f"You selected KNN with value: {knn_value} neighbours")
        # Generate Weights from the GeoDataFrame
        weight = weights.KNN.from_dataframe(gdf_demo_scal, k=knn_value)
        # Row-standardization
        weight.transform = "R"
        knn_df = weight_df(weight, gdf_demo_scal)
        show_choropleth(df_scatter, gdf_demo_scal, knn_df, selection)
    else:
        st.write("You selected Queen.")
        w_q = weights.contiguity.Queen.from_dataframe(gdf_demo_scal)
        w_q.transform = 'R'
        queen_df = weight_df(w_q, gdf_demo_scal)
        show_choropleth(df_scatter, gdf_demo_scal, queen_df, selection)

if __name__ == "__main__":
    main()
