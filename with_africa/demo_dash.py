import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
import base64
import plotly.express as px
import pandas as pd
import sqlite3
import requests
# Connect to the database (it will be created if it doesn't exist)
url = 'https://github.com/dhruv-pandit/Projects/raw/1e99b17eeeb01254051e6b73a158e64e6cef390c/with_africa/data_discovery_db.sqlite'
response = requests.get(url)
with open("data_discovery_db.sqlite", 'wb') as f:
    f.write(response.content)

conn = sqlite3.connect("data_discovery_db.sqlite")
cursor = conn.cursor()

# Retrieve data from each table and store in separate DataFrames
country_df = pd.read_sql_query("SELECT * FROM country_table", conn)
country_indicator_value_df = pd.read_sql_query("SELECT * FROM country_indicator_value_table", conn)
indicator_df = pd.read_sql_query("SELECT * FROM indicator_table", conn)

# Close the database connection
conn.close()
df_ddt_demo = country_indicator_value_df
df_ddt_demo = df_ddt_demo.merge(indicator_df[['indicator_id', 'indicator_ddt_name','indicator_source', 'indicator_ddt_cat']], left_on='indicator_id', right_on='indicator_id', how= 'left')
df_ddt_demo = df_ddt_demo.merge(country_df[['iso3_country_code', 'country_name', 'region_name']], left_on='iso3_country_code', right_on='iso3_country_code', how = 'left')
df_ddt_demo.dropna(subset=['indicator_value'], inplace=True)
df_complete = df_ddt_demo.merge(indicator_df[['indicator_id', 'units']], on='indicator_id', how='left')
# Group by the specified columns and find the index of the maximum year for each group
latest_indices = df_ddt_demo.groupby(['indicator_source', 'indicator_ddt_name', 'indicator_ddt_cat', 'country_name', 'region_name'])['indicator_year'].idxmax()

# Use the indices to filter the dataframe
df_filtered = df_ddt_demo.loc[latest_indices]
# Initialize Dash app
app = dash.Dash(__name__)
image_filename = 'https://raw.githubusercontent.com/dhruv-pandit/Projects/1e99b17eeeb01254051e6b73a158e64e6cef390c/with_africa/wa.png'  # replace with your local image path

# Download the image
response = requests.get(image_filename)
image_content = response.content

encoded_image = base64.b64encode(image_content).decode('ascii')

# Prepare your treemap
df_filtered['values'] = 2
fig = px.treemap(df_filtered, 
                 path=[px.Constant("Africa"), 'region_name', 'country_name', 'indicator_ddt_cat', 'indicator_ddt_name', 'indicator_source'], 
                 values='values',
                 color='indicator_year',
                 color_continuous_scale= 'oranges_r'
                 )
fig.data[0].hovertemplate = '%{label} <br>%{color:.0f}' 
fig.update_traces(hoverinfo='none')
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25),   font=dict(family="Futura, sans-serif", size=12, color="black"),
    coloraxis_colorbar=dict(title="Recency"))
# Define the app layout
app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image), width='1600', height='250'),
    html.H2("MVP - Demo Mode : Size, Color, Margins, Images, Etc NOT TO SCALE OR FINAL",
            style={"fontFamily": "Futura", "fontWeight": "lighter", 'color' : 'red',  'margin' : '25px'}),
    html.H1("Data Discovery Tool (2023)",
            style={"fontFamily": "Futura", "fontWeight": "lighter", 'margin' : '25px'}),
    html.Hr(style={'borderWidth': '2px', 'width': '5%', 'marginLeft': '0', 'margin' : '25px'}),  # Adjusting the size and style of the line
    html.H2("Understanding the Treemap",
            style={"fontFamily": "Futura", "fontWeight": "lighter",  'margin' : '25px'}),
    html.P("Welcome to the Data Discovery Tool! This treemap visually organizes data from various African regions, countries, and specific indicators. As you delve deeper into each section, you'll uncover more specific categories. The color represents the recency of the data: darker shades indicate more recent information. When you hover over a section, the displayed year is the average latest year available for that particular group. Dive in and explore the intricacies of the data landscape!",
            style={"fontFamily": "Futura", "fontWeight": "lighter", 'color' : 'gray',  'margin' : '25px'}),
    dcc.Graph(id='treemap', figure=fig),  # your treemap figure
    html.H2("Visualizing Trends Over Time",
            style={"fontFamily": "Futura", "fontWeight": "lighter",  'margin' : '25px'}),
    html.P("Click on any section of the treemap above to see detailed trends over the years in the graph below, which reveals trends of a chosen indicator over time. The vertical axis shows the indicator's value, and the horizontal axis represents years. Explore the line to see the data's progression. Remember to select a specific source for an indicator to view the time series visualisation.",
            style={"fontFamily": "Futura", "fontWeight": "lighter", 'color' : 'grey',  'margin' : '25px'}),
    dcc.Graph(id='line-plot')  # Placeholder for the line plot
])

# Define callback to update line plot based on treemap interaction
@app.callback(
    Output('line-plot', 'figure'),
    Input('treemap', 'clickData')
)
def update_line_plot(click_data):
    if click_data is None:
        return {}
    # Extract attributes from the clicked data
    attributes = click_data['points'][0]['id'].split('/')
    if len(attributes) < 6:
        return {}
    region, country, category, indicator, source = attributes[1:6]

    # Filter the complete dataframe
    filtered_data = df_complete[
        (df_complete['region_name'] == region) &
        (df_complete['country_name'] == country) &
        (df_complete['indicator_ddt_cat'] == category) &
        (df_complete['indicator_ddt_name'] == indicator) &
        (df_complete['indicator_source'] == source)
    ]
    unit = filtered_data['units'].iloc[0]
   
    # Create a line plot
    #line_fig = px.line(filtered_data, x='indicator_year', y='indicator_value', title=f"Values from {source} over the years for {indicator}")
    line_fig = px.line(filtered_data, x='indicator_year', y='indicator_value', title=f"Values from {source} over the years for {indicator} ({unit}) ({country})", line_shape='linear')
    # Apply custom styling
    line_fig.update_traces(line=dict(color='orange'))
    line_fig.update_layout(
        xaxis_title="Years",
        yaxis_title=f"{indicator} ({unit})",
        plot_bgcolor='white',   # Set the plot background color
        paper_bgcolor='white',
        font=dict(family="Futura, sans-serif", size=12, color="black")
    )
    line_fig.update_traces(hovertemplate=f"Year=%{{x}}<br>{indicator}=%{{y}} ({unit})")

    line_fig.update_traces(mode="markers+lines")
 
    line_fig.update_xaxes(showgrid=False)
    line_fig.update_yaxes(showgrid=False)    
    return line_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
