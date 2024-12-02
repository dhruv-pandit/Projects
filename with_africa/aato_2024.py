import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle
import plotly.graph_objects as go
import plotly.express as px
import distinctipy
import requests
from matplotlib import font_manager
streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300&display=swap');

    html, body, [class*="css"] {
    font-family: 'Open Sans';
    }

    h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif;
    }
    </style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)
# Load the data
@st.cache_data
def load_data():
    url = "https://github.com/Data-Science-Knowledge-Center-Nova-SBE/with-africa-platform/raw/refs/heads/main/datasets/new_platform/wa_complete_db.xlsx"#"https://github.com/Data-Science-Knowledge-Center-Nova-SBE/with-africa-platform/blob/main/datasets/new_platform/wa_complete_db.xlsx"
    df = pd.read_excel(url)
    df_unwto = df.query("indicator_source == 'UNWTO'")
    df_unwto_2022 = df_unwto.query("indicator_year == 2022")
    df_regions_2022= df.query("indicator_ddt_cat == 'Inbound Tourism-Regions' and indicator_year == 2022").drop_duplicates().copy()
    df_regions_2022 = pd.DataFrame(df_regions_2022.groupby('indicator_ddt_name')['indicator_value'].sum()).reset_index()
    df_purpose = df_unwto_2022.query("indicator_ddt_cat == 'Inbound Tourism-Purpose' & indicator_year == 2022").copy()
    df_purpose = pd.DataFrame(df_purpose.groupby(['region_name', 'country_name', 'indicator_ddt_name'])['indicator_value'].sum().reset_index())
    df_method = df_unwto_2022.query("indicator_ddt_cat == 'Inbound Tourism-Transport' & indicator_year == 2022").copy()
    df_method = pd.DataFrame(df_method.groupby(['region_name', 'country_name', 'indicator_ddt_name'])['indicator_value'].sum().reset_index())
    df_ind = df_unwto_2022.query("indicator_ddt_cat == 'Tourism Industries' & indicator_year == 2022").copy()
    df_ind = pd.DataFrame(df_ind.groupby(['region_name', 'country_name', 'indicator_ddt_name'])['indicator_value'].sum().reset_index())
    cluster_df = pd.read_excel('https://github.com/Data-Science-Knowledge-Center-Nova-SBE/with-africa-platform/raw/refs/heads/main/datasets/new_platform/bubble/cluster_analysis.xlsx')
    dataframes = pd.read_excel('https://github.com/Data-Science-Knowledge-Center-Nova-SBE/with-africa-platform/raw/refs/heads/main/datasets/research/aato/aato_google_complete.xlsx', sheet_name=None)

    return df_unwto, df_unwto_2022, df, df_regions_2022, df_ind, df_method, df_purpose, cluster_df, dataframes

df_unwto, df_unwto_2022, df, df_regions_2022, df_ind, df_method, df_purpose, cluster_df, dataframes = load_data()

@st.dialog("Welcome!")
def show_welcome():
    st.markdown("#### Welcome to the 2024 edition of the WiTH Africa Annual African Tourism Outlook (AATO 2024)!")
    st.write("As the African tourism sector continues to rebound from the seismic disruptions caused by the COVID-19 pandemic, 2023 and 2024 marked a period of recovery, resilience, and renewed growth. Across the continent, tourism activity has regained momentum, supported by increasing international arrivals, improving infrastructure, and strategic policymaking aimed at fostering a more sustainable industry. Building on the insights of last year’s inaugural report, the Annual African Tourism Outlook 2024 (AATO 2024) broadens its scope to provide a deeper and more comprehensive view of tourism trends, opportunities, and challenges across Africa. This edition features a wider compilation of information on Africa’s tourism sector, covering key strategic areas, as well as new visualizations, detailed plots and insights to provide a more dynamic and actionable understanding of Africa’s tourism landscape. It seeks not only to inform but also to empower stakeholders to make data-driven decisions, adopt sustainable practices, and foster meaningful collaboration across the sector.")
    if st.button("Close"):
        st.session_state.dialog_shown = True
        st.rerun()

if 'dialog_shown' not in st.session_state:
    show_welcome()
un_iso_regions = {'Total Travelers Originating From Africa': ['DZA','BEN', 'COD','BWA','TCD','CIV','ERI','GAB','KEN','LSO','MDG','MUS','MAR','NAM','NGA','SYC','ZAF','TZA','TUN','ZWE','MOZ','STP','SEN','GMB','CMR','GIN','RWA','COG','SLE','REU','AGO','BFA','BDI','CPV','CAF','COM','DJI','ETH','GHA','MWI','MLI','NER','SDN','TGO','UGA','ZMB','MRT','GNB','LBR','SSD','GNQ','SOM'],'Total Travelers Originating From Americas': ['AIA','ATG','ARG','ABW','BHS','BRB','BLZ','BMU','BRA','CAN','CYM','CHL','COL','CRI','CUB','DOM','ECU','SLV','GUF','GRL','GRD','GLP','BOL','GTM','GUY','HND','JAM','MTQ','MSR','NIC','PAN','PRY','PER','PRI','LCA','SPM','VCT', 'VEN','SUR','USA','TTO','TCA','URY','HTI','MEX'],'Total Travelers Originating From East Asia and the Pacific': ['CHN','HKG','JPN','KOR','MNG','KHM','IDN','MYS','MMR','PHL','SGP','THA','TLS','VNM','AUS','NZL','FJI','NCL','PNG','SLB','VUT','GUM','KIR','MHL','NRU','MNP','PLW','ASM','COK','PYF','NIU','WSM','TKL','TON','TUV'],'Total Travelers Originating From Europe': ['ARM','AZE','BLR','BGR','EST','GEO','HUN','KAZ','KGZ','LVA','LTU','MDA','POL','ROU','RUS','SVK','TJK','TKM','UKR','UZB','DNK','FIN','ISL','IRL','NOR','SWE','GBR','ALB','AND','BIH','HRV','GRC','ITA','TUR','MLT','MNE','MKD','PRT','SMR','SRB','SVN','ESP','AUT','BEL','FRA','DEU','LIE','LUX','MCO','NLD','CHE','CYP','ISR'],'Total Travelers Originating From Middle East': ['BHR','EGY','IRQ','JOR','KWT','LBN','LBY','OMN','QAT','SAU','SYR','ARE','YEM'],'Total Travelers Originating From South Asia': ['AFG','BGD','BTN','IRN','IND','MDV','NPL','PAK','LKA']}
# Custom color map for regions
region_colors = {
    "Western Africa": "#6EA8B4",
    "Central Africa": "#0069B4",
    "Eastern Africa": "#B60057",
    "Southern Africa": "#E42313",
    "Northern Africa": "#3D195C"
}

# Header
st.title("AATO (2024)")

st.markdown("### UNWTO Data Dashboard")
st.toast('All plots on the AATO Dashboard are interactive!', icon='🎉')
col1, col2 = st.columns(2)
with col1:
    option = st.selectbox(
        "Select Data",
        options=["International Arrivals", "Expenditure on Inbound Tourism"],label_visibility='hidden'
    )
with col2:
# Segmented Control
    st.markdown("")



# Prepare data based on selection
if option == "International Arrivals":
    df_selected = df_unwto_2022.query("indicator_ddt_name == 'Total International Arrivals'").copy()
    df_selected['indicator_value'] = df_selected['indicator_value'].astype(float)
    df_selected.sort_values(by=['indicator_value'], ascending=False, inplace=True)
    title_prefix = "Total International Arrivals"
    colors_waffle = "tab20b"
else:
    df_selected = df_unwto_2022.query("indicator_ddt_name == 'Total Expenditure on Inbound Tourism'").copy()
    df_selected['indicator_value'] = df_selected['indicator_value'].astype(float)
    df_selected.sort_values(by=['indicator_value'], ascending=False, inplace=True)
    title_prefix = "Total Expenditure on Inbound Tourism"
    colors_waffle = distinctipy.get_colors(len(df_selected), pastel_factor=0.9)


# Waffle Chart
st.markdown(f"""
#### {title_prefix}, {df_selected['units'].unique()[0]} - (2022)
""")
# fig, ax = plt.subplots(figsize=(8, 4))
# font_dir = [r'/Users/dhruvnovaims/Library/Fonts']
# font_files = font_manager.findSystemFonts(fontpaths=font_dir)
# for font in font_files:
#     font_manager.fontManager.addfont(font)

# plt.rcParams['font.family'] = 'Open Sans'
# plt.rcParams['font.size'] =14
# plt.rcParams['font.weight'] = 250
# if option == "International Arrivals":
#     Waffle.make_waffle(
#         ax=ax,
#         rows=8,
#         columns=10,
#         values=df_selected['indicator_value'],
#         labels=[
#             f"{country} ({value / df_selected['indicator_value'].sum() * 100:.1f}%)"
#             for country, value in zip(df_selected['country_name'], df_selected['indicator_value'])
#         ],
#         legend={
#             'loc': 'upper left',
#             'bbox_to_anchor': (1, 1),
#             'fontsize': 12,
#             'framealpha': 0
#         },
#         cmap_name="tab20b"

#     )
# else:
#     Waffle.make_waffle(
#         ax=ax,
#         rows=15,
#         columns=20,
#         values=df_selected['indicator_value'],
#         labels=[
#             f"{country} ({value / df_selected['indicator_value'].sum() * 100:.1f}%)"
#             for country, value in zip(df_selected['country_name'], df_selected['indicator_value'])
#         ],
#         legend={
#             'loc': 'upper left',
#             'bbox_to_anchor': (1, 1),
#             'fontsize': 12,
#             'framealpha': 0
#         },
#         colors=colors_waffle   
#     )     
# st.pyplot(fig)


fig_tree = px.treemap(
    df_selected, 
    path=["region_name", "country_name"], 
    values="indicator_value",
    color="region_name",
    color_discrete_map=region_colors,  # Use your custom region colors
    #title="Hierarchical Breakdown of Indicator Values by Region, Country, and Indicator"
)

fig_tree.update_layout(
    margin=dict(t=50, l=10, r=10, b=10),
        width = 1200,
    height = 600,
    font=dict(
        family="Open Sans",  # Set font to Open Sans
        size=12,             # Default font size
        color="black" ,
              weight = 250      # Font color
    ),
)

fig_tree.data[0].hovertemplate = '%{label} <br> %{value}' 
fig_tree.update_traces(hoverinfo='none')
st.plotly_chart(fig_tree, use_container_width=True)
st.markdown("(–) countries missing from visualization did not report any values to UNWTO for the “Compendium of Tourism Statistics, Data 2017 – 2021, 2023 Edition” ")

# Dumbbell Chart
st.markdown(f"""
#### {title_prefix}, {df_selected['units'].unique()[0]} (2021 vs 2022)""")
df_compare = df_unwto.query(f"indicator_ddt_name == '{title_prefix}'").copy()
df_compare = df_compare[df_compare['indicator_year'].isin([2021, 2022])]
df_compare['indicator_year'] = df_compare['indicator_year'].astype(int)
#A21352
#68C3CD
# Ensure the dataframe is pivoted correctly
df_pivot = df_compare.pivot(index=["country_name"], columns="indicator_year", values="indicator_value").reset_index()
df_pivot.dropna(subset=[2022], inplace=True)

fig_dumbell = go.Figure()
# Add previous year markers
fig_dumbell.add_trace(go.Scatter(
    x=df_pivot[2021], y=df_pivot["country_name"],
    mode='markers',
    name="Previous Year (2021)",
    marker=dict(color="#B60057", size=10)
))
# Add current year markers
fig_dumbell.add_trace(go.Scatter(
    x=df_pivot[2022], y=df_pivot["country_name"],
    mode='markers',
    name="Current Year (2022)",
    marker=dict(color="#68C3CD", size=10)
))
# Add connecting lines
for i, row in df_pivot.iterrows():
    fig_dumbell.add_trace(go.Scatter(
        x=[row[2021], row[2022]], y=[row["country_name"], row["country_name"]],
        mode='lines',
        line=dict(color="gray", width=1),
        showlegend=False
    ))

# Update layout
fig_dumbell.update_layout(
    title=f"",
    xaxis_title="Value",
    yaxis_title="Country",
    title_x=0.5,
    template="simple_white",
    xaxis=dict(showgrid=False,showline = False,  showticklabels=True),  # Hide x-axis grid, line, and labels
    yaxis=dict(showgrid=False,showline = False, showticklabels=True), 
    width = 1200,
    height=400,  # Adjust height for better spacing
    margin=dict(l=200, r=50, t=50, b=50),  # Add left margin for long country names
        #title="African Regions with Country Indicators",
    font=dict(
        family="Open Sans",  # Set font to Open Sans
        size=12,             # Default font size
        color="black" ,
              weight = 250      # Font color
    )
)

st.plotly_chart(fig_dumbell, use_container_width=True)

#-----------------
# Regions
# Expand the dataframe to associate each country ISO with its indicator value
expanded_data = []
for idx, row in df_regions_2022.iterrows():
    indicator = row['indicator_ddt_name']
    value = row['indicator_value']
    countries = un_iso_regions.get(indicator, [])
    for country in countries:
        expanded_data.append({'country_iso': country, 'indicator_value': value, 'region' : indicator})

# Create the expanded dataframe
df_expanded = pd.DataFrame(expanded_data)

# Create the choropleth map
fig_regions = px.choropleth(
    df_expanded,
    locations="country_iso",
    color="indicator_value",
    hover_data = 'region', 
    hover_name="country_iso",
    projection="natural earth",
    color_continuous_scale=px.colors.sequential.Teal
)

fig_regions.update_geos(
    showland=True,
    landcolor="lightgray",           # Light gray country fill color
    showcountries=True,             # Remove country borders
    
    coastlinecolor="white",          # Coastline color in white
    projection_type="natural earth",  # Change projection to rectangular
    lataxis_showgrid=False,          # Remove latitude gridlines
    lonaxis_showgrid=False     ,      # Remove longitude gridlines
        countrycolor="white",            # Set country borders to white
)
fig_regions.update_traces(marker_line_width=0.1,marker_line_color = 'white', selector=dict(type='choropleth'))
# Remove whitespace around the plot
fig_regions.update_layout(       geo=dict(        showframe=False,
            showcoastlines=True,
        ),
    margin=dict(l=0.1, r=0.1, t=0.1, b=0.1),  # Remove margins
    width=1200,                      # Adjust width
    height=600                       # Adjust height
)
fig_regions.update_layout(
    #title="Indicator Value by Country",
    font=dict(
        family="Open Sans",  # Set font to Open Sans
        size=12,             # Default font size
        color="black" ,
              weight = 250      # Font color
    ),
    dragmode=False,
    coloraxis_colorbar=dict(title="Value")
)
fig_regions.add_annotation(text="Source: WiTH Africa, 2023, Lighter shades indicate better performance", xref="paper", yref="paper",
                    x=0, y=-0.1, showarrow=False, font=dict(size=15, color="black"))
fig_regions.data[0].hovertemplate = '%{customdata[0]}<br>%{z} (Thousands)' 
fig_regions.update_traces(hoverinfo='none')
fig_regions.update_layout(coloraxis_colorbar=dict(title="Total Visitors (Thousands)"))
fig_regions.update_layout(coloraxis_showscale=False)

st.markdown(""" 
#### Inbound Tourism By Regions

Travelers originating from Africa, Americas, East Asia and the Pacific, Middle East, South Asia, other not classified and nationals residing abroad – 2022 (UNWTO)

""")
# Show the plot
st.plotly_chart(fig_regions, use_container_width=True)

#------
# Segmented Control
st.markdown("#### Breaking Down Key Tourism Categories")
col1, col2 = st.columns(2)
with col1: 
    option2 = st.selectbox(
    "Select Category",
    options=["Purpose of Arrival", "Method of Arrival", "Tourism Industries"], label_visibility='hidden')
with col2: 
    st.markdown(f"     ##### {option2}")
if option2 == "Purpose of Arrival":

    df_filtered = df_purpose[~df_purpose['indicator_ddt_name'].isin(['Total (Inbound Tourism-Purpose)'])]

    more_colors = ['#EF7D00', '#FAB54D', '#AFD8C1', '#D1E2A8','#FAEB8B']

    more_colors= {key : value for key, value in zip(df_filtered.indicator_ddt_name.unique(), more_colors[:df_filtered.indicator_ddt_name.nunique()])}
    country_to_color = {country: region_colors[region] for country, region in dict(zip(df_filtered.country_name, df_filtered.region_name)).items()}
    colors_map = {**region_colors, **more_colors, **country_to_color}
    hovertemplate = '%{parent}<br>%{label}: %{value} (Total Travelers, Thousands)' 

elif option2 == "Method of Arrival":
    df_filtered = df_method[~df_method['indicator_ddt_name'].isin(['Total (Inbound Tourism-Transport)'])]

    more_colors = ['#EF7D00', '#FAB54D', '#AFD8C1', '#D1E2A8','#FAEB8B']
    more_colors.reverse()
    more_colors= {key : value for key, value in zip(df_filtered.indicator_ddt_name.unique(), more_colors[:df_filtered.indicator_ddt_name.nunique()])}
    country_to_color = {country: region_colors[region] for country, region in dict(zip(df_filtered.country_name, df_filtered.region_name)).items()}
    colors_map = {**region_colors, **more_colors, **country_to_color}
    hovertemplate = '%{parent}<br>%{label}: %{value} (Total Travelers, Thousands)' 

else:
    more_colors = ['#EF7D00', '#FAB54D', '#AFD8C1', '#D1E2A8','#FAEB8B', '#871262']
    df_filtered = df_ind.copy()
    more_colors= {key : value for key, value in zip(df_filtered.indicator_ddt_name.unique(), more_colors[:df_filtered.indicator_ddt_name.nunique()])}
    country_to_color = {country: region_colors[region] for country, region in dict(zip(df_filtered.country_name, df_filtered.region_name)).items()}
    colors_map = {**region_colors, **more_colors, **country_to_color}
    hovertemplate = '%{parent}<br>%{label}: %{value} (Total Units)' 
fig = px.sunburst(
    df_filtered, 
    path=["region_name", "country_name", "indicator_ddt_name"], 
    values="indicator_value",
    color="region_name",
    color_discrete_map=region_colors,  # Use your custom region colors
    #title="Hierarchical Breakdown of Indicator Values by Region, Country, and Indicator"
)

fig.update_layout(
    margin=dict(t=50, l=10, r=10, b=10),
        width = 1000,
    height = 600,
    font=dict(
        family="Open Sans",  # Set font to Open Sans
        size=12,             # Default font size
        color="black" ,
            weight = 250      # Font color
    ),
)

fig.update_traces(marker_colors=[colors_map[cat] for cat in fig.data[-1].labels])
fig.data[0].hovertemplate = hovertemplate
fig.update_traces(hoverinfo='none')
st.plotly_chart(fig, use_container_width=True)

st.markdown(""" 
#### Classifying Africa's Tourism Markets

Our analysis of Africa's tourism industries has led to the creation of a categorization system that groups countries into four distinct categories: Established Tourism Industry, Emerging Tourism Industry, Advancing Tourism Economy, and Nascent Tourism Market. This classification is based on a range of indicators reflecting tourism activity, infrastructure, and accessibility. Through this lens, countries such as Egypt, Morocco, and South Africa are identified as having Established Tourism Industries, showcasing their advanced infrastructure and strong international appeal. Emerging Tourism Industry nations, like Kenya and Mauritius, are experiencing rapid growth, signaling their rising importance in global tourism. The Advancing Tourism Economy category highlights countries like Ghana and Ethiopia, which are steadily developing their tourism potential. Lastly, the Nascent Tourism Market includes countries where tourism remains underdeveloped, offering significant opportunities for investment and growth.

""")
cluster_df['size'] = 2
cluster_df.sort_values(by=['Cluster'], inplace=False)
# Add custom colors for Tourism Category groups
tourism_category_colors = {
    "Nascent Tourism Market": "#D1E2A8",  # Replace with your desired color
    "Emerging Tourism Industry": "#AFD8C1",
    "Advancing Tourism Economy": "#68C3CD",
    "Established Tourism Industry": "#009BD0"
}
more_colors = ['#EF7D00', '#FAB54D', '#AFD8C1', '#D1E2A8','#FAEB8B', '#871262']


df_filtered = cluster_df.copy()
more_colors= {key : value for key, value in zip(df_filtered['Tourism Category'].unique(), more_colors[:df_filtered['Tourism Category'].nunique()])}
country_to_color = {country: region_colors[region] for country, region in dict(zip(df_filtered.country_name, df_filtered.region_name)).items()}
colors_map = {**region_colors, **more_colors, **country_to_color}


fig = px.sunburst(cluster_df, 
                 path=['Tourism Category', 'country_name'],
                 values='size',  # Total Expenditure on Inbound Tourism
                 color='region_name',
                 color_discrete_map=region_colors,  # Use your custom combined colors
                       labels={

                     "region_name": "Region"
                 },
)

fig.update_layout(
    margin=dict(t=50, l=10, r=10, b=10),
        coloraxis_colorbar=dict(title="Region"),  # Rename the legend to "Region"

    width=1000,
    height=600,
    font=dict(
        family="Open Sans",  # Set font to Open Sans
        size=12,             # Default font size
        color="black",       # Font color
        weight=250           # Font weight
    ),
)

fig.data[0].hovertemplate = '%{label}<br>Tourism Market: %{parent}' 
fig.update_traces(hoverinfo='none')
fig.update_traces(marker_colors=[colors_map[cat] for cat in fig.data[-1].labels])
st.plotly_chart(fig, use_container_width=True)

st.markdown("The categorization of African countries into tourism market clusters is based on our own analysis and methodology, utilizing selected indicators relevant to the tourism industry. These classifications are intended to provide a generalized perspective and should not be interpreted as definitive rankings or assessments.")



def create_demand_trend_plot(df, x_column = 'date', y_current = 'current_market_queries', y_last_year = 'last_year_market_queries', height=600, width = 1000):
    """
    Creates a demand trend line plot comparing current year and last year's demand.

    Parameters:
        df (pd.DataFrame): The dataframe containing the data.
        x_column (str): The column to use for the x-axis (e.g., 'date').
        y_current (str): The column representing the current year's demand data.
        y_last_year (str): The column representing the last year's demand data.
        height (int): The height of the plot. Default is 600.

    Returns:
        fig (plotly.graph_objects.Figure): The Plotly figure.
    """
    fig = go.Figure()
    
    # Add the current year's demand trend
    fig.add_trace(go.Scatter(
        x=df[x_column], 
        y=df[y_current],
        mode='lines',
        name='2024 Demand Trend'
    ))
    
    # Add the last year's demand trend
    fig.add_trace(go.Scatter(
        x=df[x_column], 
        y=df[y_last_year],
        mode='lines',
        name='2023 Demand Trend'
    ))
    
    # Update layout
    fig.update_layout(
        title = "", 
        xaxis_title="Month",
        yaxis_title="Demand",
        title_x=0.5,
        template="simple_white",
        xaxis=dict(showgrid=False, showline=False, showticklabels=True),
        yaxis=dict(showgrid=False, showline=False, showticklabels=True),
        height=height,
        margin=dict(l=200, r=50, t=50, b=50),
        font=dict(
            family="Open Sans",  # Set font to Open Sans
            size=12,             # Default font size
            color="black",       # Font color
            weight=250
        ),
    )
    
    return fig

def create_choropleth_with_custom_country(df, country_name, country_code,  custom_color="Green",color_scale = px.colors.sequential.Oranges_r,width=1200, height=600):
    """
    Creates a choropleth map highlighting a specific country in a custom color and applying a color scale to others.

    Parameters:
        df (pd.DataFrame): The dataframe containing the data.
        country_name (str): The name of the country to highlight (e.g., 'South Africa').
        country_code (str): The ISO country code to highlight (e.g., 'ZAF').
        color_scale (str): Color scale for other countries (default is 'oranges').
        custom_color (str): Color for the highlighted country (default is 'green').
        width (int): Width of the plot (default is 800).
        height (int): Height of the plot (default is 600).

    Returns:
        fig (plotly.graph_objects.Figure): The Plotly figure.
    """


    # Add the country row to the dataframe with a specific rank for highlighting
    df = df.copy()
    df_custom = pd.DataFrame(
    {    'location' : [country_name],
        'rank' : [0],
        'iso' : [country_code]}
    )


    fig = px.choropleth(
        df, 
        locations="iso", 
        color="rank",    # Use the custom color column
        hover_name="location", 
        projection="natural earth",
        color_continuous_scale=color_scale,
    )

    # Update geographical details
    fig.update_geos(
        showland=True,
        landcolor="lightgray",
        showcountries=True,
        countrycolor="white",
        coastlinecolor="white",
    )
    fig.add_traces(go.Choropleth(locations=df_custom['iso'],
                                z = [1],
                                colorscale = [[0, custom_color],[1, custom_color]],
                                colorbar=None,
                                showscale = False)
                )


    # Update layout
    fig.update_layout(dragmode=False,coloraxis_colorbar=dict(title="Rank"))
    fig.update_geos(
    showland=True,
    landcolor="lightgray",           # Light gray country fill color
    showcountries=True,             # Remove country borders
    
    coastlinecolor="white",          # Coastline color in white
    projection_type="natural earth",  # Change projection to rectangular
    lataxis_showgrid=False,          # Remove latitude gridlines
    lonaxis_showgrid=False     ,      # Remove longitude gridlines
        countrycolor="white",            # Set country borders to white
    )
    fig.update_traces(marker_line_width=0.1,marker_line_color = 'white', selector=dict(type='choropleth'))
    # Remove whitespace around the plot
    fig.update_layout(       geo=dict(        showframe=False,
                showcoastlines=True,
            ),
        margin=dict(l=0.1, r=0.1, t=0.1, b=0.1),  # Remove margins
        font=dict(
            family="Open Sans",  # Set font to Open Sans
            size=12,             # Default font size
            color="black" ,
                weight = 250      # Font color
        ),
        width=1200,                      # Adjust width
        height=600                       # Adjust height
    )
    # fig.update_layout(
    #     #title="Scatter Geo Plot of Cities in South Africa",  # Title for the plot
    #     geo=dict(        showframe=False,
    #         showcoastlines=True,
    #     ),
    #     font=dict(
    #         family="Open Sans",  # Set font to Open Sans
    #         size=12,             # Default font size
    #         color="black" ,
    #             weight = 250      # Font color
    #     ),
    #     #coloraxis_colorbar=dict(title="Region"),  # Rename the legend to "Region"
    #     #coloraxis_showscale=False        ,         # Hide color scale if necessary
    #     width=width,                               # Set custom width
    #     height=height   
    # )


    return fig

gd_keys = [key for key in dataframes.keys() if 'SourcesDemand' in key]

isos = {'df_ang_SourcesDemand' : 'AGO',
 'df_eqg_SourcesDemand' : 'GNQ',
 'df_moz_SourcesDemand' : 'MOZ',
 'df_stp_SourcesDemand' : 'STP',
 'df_mor_SourcesDemand' : 'MAR',
 'df_egy_SourcesDemand' : 'EGY',
 'df_sa_SourcesDemand' : 'ZAF',
 'df_gb_SourcesDemand' : 'GNB',
 'df_cpv_SourcesDemand': 'CPV'}
st.markdown("### Google Destination Insights for Selected African Countries (2024)")
with st.expander("**What Are Google Destination Insights?**"):
    st.write('''
             This section introduces new visualizations powered by data from Google Destination Insights, which leverages aggregated and anonymized data from Google searches related to travel trends. These insights are derived from Google Trends and other data points, offering a unique view into travel demand and preferences. 

             Our analysis focuses on two key groups of countries. The first group comprises Africa’s top three countries by Total International Arrivals in 2022, as identified by UNWTO data (South Africa, Egypt, and Morocco). These destinations provide a benchmark for understanding high-performing tourism markets. The second group examines Lusophone countries, highlighting demand trends and source markets specific to Portuguese-speaking nations. 

    ''')
option3 = st.selectbox(
    "Select Country",
    options=["South Africa", "Morocco", "Egypt, 'Mozambique", 'Angola', 'Cabo Verde', 
             'Equatorial Guinea', 'Sao Tome and Principe', 'Guinea-Bissau'], label_visibility='hidden'
)


if option3 == 'South Africa':
    country = 'sa'
elif option3 == 'Morocco':
    country = 'mor'
elif option3 == 'Egypt':
    country = 'egy'
elif option3 == 'Mozambique':
    country = 'moz'
elif option3 == 'Angola':
    country = 'ang'
elif option3 == 'Cabo Verde':
    country = 'cpv'

elif option3 == 'Equatorial Guinea':
    country = 'eqg'
elif option3 == 'Sao Tome and Principe':
    country = 'stp'
else:
    country = 'gb'

trend_fig = create_demand_trend_plot(dataframes[f"df_{country}_TravelTrends"])
map_fig = create_choropleth_with_custom_country(dataframes[f"df_{country}_SourcesDemand"], country_code=isos[f"df_{country}_SourcesDemand"], country_name=option3)

st.markdown("#### Travel Demand (2024 vs 2023)")

st.plotly_chart(trend_fig, use_container_width=True)
st.markdown("The y-axis represents the relative search volume index for travel demand to the selected country, where 0 indicates no interest and 100 represents peak popularity, reflecting search activity as a percentage of its highest observed level. We smooth the time series using a 7-day rolling mean to increase the interpretability. ")
st.markdown("#### Sources of Demand")
st.plotly_chart(map_fig, use_container_width=True)
st.markdown("The world plot illustrates the source of travel demand for the selected destination, with countries ranked on a scale from 0 to 100; higher values (darker green) indicate stronger relative demand based on search activity.")