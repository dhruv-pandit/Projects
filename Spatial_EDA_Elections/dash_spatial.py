import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

# Load your shapefile data using GeoPandas
new_gdf = gpd.read_file(r'/Users/dhruvpandit/Documents/GitHub/Projects/Spatial_EDA_Elections/Dataset/V11.shp')

# Select numeric columns for PCA
numeric_cols = new_gdf.select_dtypes(include=['float64', 'int64'])

# Standardize the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_cols)

# Impute missing values
imputer = SimpleImputer(strategy='median')  # You can choose 'mean', 'median', etc.
scaled_data = imputer.fit_transform(scaled_data)

# Perform PCA
pca = PCA(n_components=15)
principal_components = pca.fit_transform(scaled_data)

# Create a Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Principal Component Analysis of Portuguese Legislative Elections (2019)", style={'textAlign': 'center'}),
    
    # Scatter plot of explained variance ratio
    dcc.Graph(id="explained-variance-plot"),
    
    # Dropdown for selecting the number of components
    html.Label("Select the component:"),
    dcc.Dropdown(
        id="component-dropdown",
        options=[{'label': str(i), 'value': i} for i in range(1, 16)],
        value=5,  # Default number of components
    ),
    
    # Scatter plot for loading of selected component
    dcc.Graph(id="loading-plot")
])

# Custom CSS stylesheet for changing font family
app.css.append_css({
    'external_url': 'https://fonts.googleapis.com/css?family=Futura&display=swap'
})

@app.callback(
    Output("explained-variance-plot", "figure"),
    Output("loading-plot", "figure"),
    Input("component-dropdown", "value")
)
def update_plots(selected_component):
    # Explained variance ratio plot as a bar graph
    explained_variance_fig = go.Figure(go.Bar(
        x=list(range(1, len(pca.explained_variance_ratio_) + 1)),
        y=pca.explained_variance_ratio_,
        marker=dict(color=pca.explained_variance_ratio_, colorscale='Blues'),
    ))

    explained_variance_fig.update_layout(
        xaxis=dict(title="Component"),
        yaxis=dict(title="Explained Variance Ratio"),
        title="Explained Variance Ratio of 15 Components",
    )

    # Loading plot for the selected component as a bar graph
    loading_fig = go.Figure(go.Bar(
        x=numeric_cols.columns,
        y=pca.components_[selected_component - 1],
        marker=dict(color=pca.components_[selected_component - 1], colorscale='Blues'),
    ))

    loading_fig.update_layout(
        xaxis=dict(title="Variable"),
        yaxis=dict(title="Loading"),
        title=f"Loading for Component {selected_component}",
    )

    return explained_variance_fig, loading_fig

if __name__ == '__main__':
    app.run_server(debug=True)
