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
    url = 'https://github.com/dhruv-pandit/Projects/raw/main/spatial_elections_eda/Dataset/V11.shp'
    new_gdf = gpd.read_file(url)
    return new_gdf.copy()  # Return a copy to ensure the original is not mutated

# Scale the data
@st.cache_data
def scale_data(_new_gdf):
    from sklearn.preprocessing import StandardScaler
    gdf_demo_scal = _new_gdf.copy()
    numeric_cols = gdf_demo_scal.select_dtypes(include=['float64', 'int64']).columns
    

    return gdf_demo_scal

def weight_df(weight, gdf_demo_scal):
    knn_df = gdf_demo_scal.copy()
    for each in knn_df.columns:
        if each == 'geometry':
            continue
        knn_df[each] = weights.spatial_lag.lag_spatial(
            weight, gdf_demo_scal[each]
        )
    return knn_df
def show_choropleth(df_scatter,gdf_demo_scal, knn_df, selection):
    option = st.selectbox('Select a Variable for Visualization:',('PPindex202', 'Mhousesqm', 'Votepct', 'OBN',
       'DVotepct', 'DOBN', 'Left', 'Centre', 'Right', 'C - left', 'C - right',
       'Tot 0_14', 'Tot 15_24', 'Tot 25_64', 'Tot 65', 'T0_14(%)', 'T15_24(%)',
       'T25_64(%)', ' T65(%)', 'Votepct_we', 'Crime Rate', 'Non fin en',
       'TotStudEnr'))
    # Create two choropleth maps
    m1 = folium.Map(location=[39.4, -8.2], zoom_start=6, width=200)
    m2 = folium.Map(location=[39.4, -8.2], zoom_start=6, width=200)
    knn_df['concelhos_'] = gdf_demo_scal['concelhos_']
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
    col1, col2 = st.columns(2)

    # Display the maps in the columns
    with col1:
        st.write("""
    ### Original Values Distribution
    """)
        folium_static(m1, width = 250)

    with col2:
        st.write(f"""
    ### Spatially Lagged Values Distribution Using {selection}
    """)
        folium_static(m2, width = 250)

# Main function to run the app
def main():
    st.title("Spatial Exploration of 2019 Portuguese Elections")
    st.write("""
    Welcome to the spatial EDA of Portuguese Elections. This dashboard provides visual insights into various election-related metrics across different regions of Portugal. Dive in, explore the data, and uncover spatial patterns.
    """)
    st.write("""
    * Contact at dhruvpandit@aln.iseg.ulisboa.pt
    """)
    # Load and scale data
    new_gdf = load_data()
    new_gdf = new_gdf.to_crs("EPSG:4326")
    gdf_demo_scal = scale_data(new_gdf)
    st.write("""
    ## Choropleth Visualisation of Variables
    ### Selected Variables Used
    * PPindex2020 – Purchasing Power Index (Portugal = 100)
    * Mhousesqm – Median house prices per square meter
    * M0_14 – male population between 0 and 14 years
    * M15_24 – male population between 15 and 24 years
    * M25_64 – male population between 25 and 64 years
    * M65 – male population with 65 years or higher
    * F0_14 – female population between 0 and 14 years
    * F15_24 – female population between 15 and 24 years
    * F25_64 – female population between 25 and 64 years
    * F65 – female population with 65 years or higher
    * TOTALPOP – Total population
    * Voters – Total number of voters
    * Votepct – Voters Percentage (participation rate)
    * Party percentages for 10 political parties aggregated over political spectrum (from left to right) 
    * DVotepct – change in Voters Percentage from previous national elections (change in participation)
    * DOBN – change in OBN % from from previous national elections
    """)
    st.write("""
    ### Choropleth Visualization

    Choose a metric from the dropdown to visualize its spatial distribution across Portugal. Choropleth maps use varying shades of colors to represent data values in different regions, providing an intuitive way to understand spatial patterns.
    """)

    # Dropdown to select variable for choropleth
    option = st.selectbox(
        'Select a Variable for Visualization:',
        ('PPindex202', 'Mhousesqm', 'M0_14', 'M15_24', 'M25_64', 'M65', 'F0_14', 'F15_24', 'F25_64', 'F65',
         'TOTALPOP', 'Voters', 'Votepct', 'DVotepct', 'DOBN',
         'Centre_l_tvote', 'Centre_r_tvote', 'Left_tvote', 'Right_tvote')
    )
    with st.spinner('Plotting... This might take a while.'):
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
    st.write("""
    ### Scatter Plot Analysis

    Select two variables to plot against each other. This can help you identify relationships or correlations between different metrics. 
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
    with st.spinner('Plotting... This might take a while.'):

        # Scatter plot using Plotly
        fig_scatter = px.scatter(df_scatter, x=x_var, y=y_var)
        st.plotly_chart(fig_scatter)
    st.write("""
    ## Correlation Matrix for Numeric Variables
    """)
    st.write("""
    ### Correlation Matrix

    The heatmap below represents the correlation between different metrics. A value close to 1 indicates a strong positive correlation, while a value close to -1 indicates a strong negative correlation.
    """)

    with st.spinner('Plotting... This might take a while.'):
        # Correlation matrix using Plotly
        corr_matrix = df_scatter.corr()
        fig_corr = px.imshow(corr_matrix, color_continuous_scale='RdBu')
        st.plotly_chart(fig_corr)

    st.write("""
    ### Principal Component Analysis (PCA)

    Principal Component Analysis (PCA) is a powerful dimensionality reduction technique that transforms high-dimensional data into a lower-dimensional form. This transformation retains as much of the data's original variance as possible. By visualizing and analyzing these principal components, we can gain insights into the underlying patterns and structures of the original data.
    """)
    st.write("""
    #### Selecting Number of Components

    Use the slider below to select the number of principal components you'd like to consider. Typically, we choose components that together capture a significant portion of the total variance in the data. The bar chart below the slider will show the explained variance for each component, helping you make an informed choice.
    """)

    num_components = st.slider('Select number of principal components:', 1, 20)

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
    st.write("""
    ### Loadings Plot for Chosen Component

    Once you've selected the number of components, delve deeper into the composition of an individual component. Use the dropdown menu to select a specific principal component and visualize its loadings plot. The loadings plot reveals how much each original variable contributes to the selected component, helping to interpret the component in terms of the original data.
    """)

    # Dropdown to select a specific principal component for loadings plot
    selected_pc = st.selectbox('Select principal component for loadings plot:', [f'PC{i+1}' for i in range(num_components)])
    selected_index = int(selected_pc[2:]) - 1  # Convert PC label to index

    # Bar plot for loadings of the chosen principal component
    loadings = pca.components_[selected_index]
    fig_loadings = px.bar(x=df_scatter.columns, y=loadings, labels={'x':'Feature', 'y':'Loading'})
    st.plotly_chart(fig_loadings)


    st.write("""
    ## Spatial Weights and Lags

    Select a method for spatial weights:

    - **KNN (K-Nearest Neighbors)**: Weights based on a specified number of nearest regions. Use the slider to choose between a minimum of 3 and a maximum of 8 neighbors. 
    - **Queen**: Weights based on shared boundaries or vertices between regions.

    Depending on your selection, you'll see two choropleth maps side by side. The first represents the original values, while the second represents spatially lagged values using the chosen method.
    """)

    selection = st.radio("Choose a method:", ('KNN', 'Queen'))

    # If KNN is selected, display the slider
    if selection == 'KNN':
        knn_value = st.slider('Select KNN value:', min_value=3, max_value=8)
        st.write(f"You selected KNN with value: {knn_value} neighbours")
        # Generate Weights from the GeoDataFrame
        df_scatter['geometry'] = gdf_demo_scal['geometry']
        weight = weights.KNN.from_dataframe(df_scatter, k=knn_value)
        # Row-standardization
        weight.transform = "R"
        knn_df = weight_df(weight, df_scatter)
        with st.spinner('Plotting... This might take a while.'):
            show_choropleth(df_scatter, gdf_demo_scal, knn_df, selection)
    else:
        st.write("You selected Queen.")
        df_scatter['geometry'] = gdf_demo_scal['geometry']
        w_q = weights.contiguity.Queen.from_dataframe(df_scatter)
        w_q.transform = 'R'
        queen_df = weight_df(w_q, df_scatter)
        with st.spinner('Plotting... This might take a while.'):
            show_choropleth(df_scatter, gdf_demo_scal, queen_df, selection)

if __name__ == "__main__":
    main()
