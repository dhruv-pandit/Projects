import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import requests
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

#-----------
# Functions

@st.cache_data
def load_data():
    url = 'https://github.com/dhruv-pandit/Projects/raw/main/with_africa/with_eoa_copy.xlsx'
    url_new = 'https://github.com/dhruv-pandit/Projects/raw/main/with_africa/dashboard/results.xlsx'
    df_org_results = pd.read_excel(url_new, sheet_name='organisations')
    df_ngos_results = pd.read_excel(url_new, sheet_name='ngos')
    df_gov_results = pd.read_excel(url_new, sheet_name='government_sources')
    df_eoa = pd.read_excel(url, sheet_name = 'eoa_dashboard_data').rename(columns={'ISO3 Code' : 'ISO3_Code', 'Ease of Access' : 'EOA_Score'})
    df_infotext = pd.read_excel(url, sheet_name = 'infottext_new')

    # Query the ScoreLegend table and save to a dataframe
    df_scorelegend = pd.read_excel(url, sheet_name = 'legend_new')

    return df_eoa, df_gov_results, df_ngos_results, df_org_results, df_infotext, df_scorelegend
def plot_choropleth(df_gov_results, dic, option, ):
    min_value = df_gov_results[dic[option]].min()
    max_value = df_gov_results[dic[option]].max()
    tick_values = list(range(int(min_value), int(max_value) + 1))
    z_value = df_gov_results[dic[option]]
    colorbar_tickvals = tick_values if option == 'Machine Readability Data Available' else None
    colorbar_ticktext = tick_values if option == 'Machine Readability Data Available' else None

    fig_choro = go.Figure(data=go.Choropleth(
        locations=df_gov_results['country'],
        z=z_value,
        locationmode='country names',
        colorscale='oranges_r',
        colorbar_title=option,
        colorbar_tickvals=colorbar_tickvals,
        colorbar_ticktext=colorbar_ticktext
    ))
    background_color = 'white'

    fig_choro.update_layout(coloraxis={"colorbar":{"dtick":1}})
    fig_choro.update_layout(
        geo_scope='africa',
        #title_text='Ease of Access Scores For Each African Country',  # Title of the map
        geo=dict(
            showframe=False,  # Hide map frame
            showcoastlines=False,  # Hide coastlines
            projection_type='natural earth' , # Choose a projection type
        bgcolor=background_color  # Set geo background color to black
    ),
    paper_bgcolor=background_color,  # Set paper background color to black
    plot_bgcolor=background_color,
        height=700,
        width=400,
        font=dict(family="Open Sans")  # Set the font family to "Open Sans"
    )

    # Customize hover label font size
    fig_choro.update_layout(hoverlabel=dict(bgcolor='grey', bordercolor='black', font=dict(size=8)))
    fig_choro.add_annotation(text="Source: WiTH Africa, 2023, Lighter shades indicate better performance", xref="paper", yref="paper",
                    x=0, y=-0.1, showarrow=False, font=dict(size=15, color="lightgray"))

    return fig_choro
# Function to create a bar chart with Plotly Express

def create_bar_chart(data, x, y, title, range_x, hover_data, color_scale, width=1000):
    background_color = 'white'
    color = 'recency' if y == 'year_score' else y
    fig = px.bar(data, x=x, y=y, color=color, hover_data=hover_data,
                 color_continuous_scale=color_scale, width=width)
    fig.update_layout(
        xaxis=dict(title=x, tickfont=dict(size=20, family="Open Sans"), range=range_x),
        yaxis=dict(title=title, tickfont=dict(size=20, family="Open Sans")),
        font=dict(family="Open Sans", size=19),
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        coloraxis_colorbar=dict(title=title)
    )
    return fig


#-----------

df_eoa, df_gov_results, df_ngos_results, df_org_results, df_infotext, df_scorelegend = load_data()

st.title("African Tourism Data Accessibility (2023)")
st.write("""
    Version 1.0.4
    (**please click on three dots > settings > click on wide mode and change theme to light mode**) 
_____

""")
countries = df_eoa['Country'].unique().tolist()

col1, col2 = st.columns(2)
with col1:
    option = st.selectbox(
    'Select an Indicator',options = ['Recency', 'Ease of Access Score', 'Machine Readability Data Available', 'Number of Indicators'])
    st.write(f"""
    ## {option}
    ____
    """)

    dic = {
        'Recency' : 'recency',
        'Ease of Access Score': 'final_score', 
        'Machine Readability Data Available' : 'machine_read', 
        'Number of Indicators' : 'num_indicators'
    }
    fig_choro = plot_choropleth(df_gov_results, dic, option)
    st.plotly_chart(fig_choro,  use_container_width=True)
    st.write("Findings reflect the state of the African tourism data ecosystem between late August and early October 2023. Data was rigorously sourced from primary statistical agencies across Africa, supplemented by tourism ministries and central banks where necessary.")
with col2:
    option = st.selectbox(
    'Select a country',options = countries)
    country_data = df_gov_results[df_gov_results['country'] == option].iloc[0]
    eoa = country_data['final_score']
    link = country_data['link']
    comment = df_eoa[df_eoa['Country'] == option]['Comments'].iloc[0]
    num_indic = country_data['num_indicators']
    machine_read = 'Available' if country_data['machine_read'] == 1 else 'Not Available'
    security_stat = 'Warning Present' if country_data['security_warning'] == 0 else 'No Warning'
    
    st.header(option)
    st.write(f"""
    ______
    ## Score : {eoa:.2f}

    {comment}

    **Number of Indicators Tracked**: {num_indic}

    **Machine Readable Data Status**: {machine_read[0]}

    **Security Warning Status**: {security_stat[0]} 

    *Link to Website*: {link} (Last accessed October 2023)
    """)

#-----------

# Treemap

df_org_results['group'] = 'Institutions'
df_gov_results['group'] = 'Government Sources'
df_ngos_results['group'] = 'NGOS'
df_gov_results['source'] =df_gov_results['country']
df_gov_results['full form'] =df_gov_results['country']


columns = ['num_indicators', 'source', 'full form', 'recency', 'final_score', 'group']
df_combined = pd.concat([df_gov_results[columns], df_ngos_results[columns], df_org_results[columns]], join='inner')

# Filter out rows where num_indicators is zero or missing
df_combined = df_combined[df_combined['num_indicators'] > 0]

treemap = px.treemap(df_combined, 
                 path=[px.Constant("All Sources"), 'group', 'full form'],
                 values='num_indicators',
                 color='recency',
                 color_continuous_scale='oranges_r',
                 hover_data=['num_indicators', 'recency'], width=1000
                )
treemap.data[0].hovertemplate = '%{label} <br>Recency: %{color:.0f} <br>Number of Indicators: %{value}' 

treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25),   font=dict(family="Open Sans, sans-serif", size=12, color="grey"),
    coloraxis_colorbar=dict(title="Recency"))
treemap.add_annotation(text="Source: WiTH Africa, 2023, Lighter shades indicate better performance", xref="paper", yref="paper",
                    x=0, y=-0.065, showarrow=False, font=dict(size=15, color="lightgray"))

st.write("""
        # Number of Indicators Across All Data Sources
        Explore the hierarchical breakdown of the number of indicators, starting from the broad categories of data sources down to the specific entities. This treemap visually represents the number of indicators for each source, allowing you to discern which entities provide the most comprehensive data in the ecosystem.
         """)
st.plotly_chart(treemap)


#-----------

st.write("""
         # WiTH Africa Continental Crosscheck
         Welcome to the comparison section of our dashboard! Here, you can dive deep into the data accessibility metrics of multiple countries and regions side-by-side. Use the tabs to switch between countries and regions. 
         Use the multi-select dropdown to pick the countries or regions you're interested in. The visualizations will adjust based on your selections.
         """)



# Tabs for countries and regions
tabcount, tabreg = st.tabs(['Countries', 'Regions'])

with tabcount:
    selected_countries = st.multiselect("Select countries for comparison", df_gov_results['country'].tolist())
    if selected_countries:
        selected_df = df_gov_results[df_gov_results['country'].isin(selected_countries)]
        # Tabs for plots
        tabindic, tabrec, tabscore = st.tabs(['Number of Indicators', 'Recency', 'Ease of Access Score'])
        plot_options = {
            'Number of Indicators': ('country', 'num_indicators', 'Number of Indicators'),
            'Recency': ('country', 'year_score', 'Recency of Data'),
            'Ease of Access Score': ('country', 'final_score', 'Ease of Access Score')
        }
        for tab, (x, y, title) in zip([tabindic, tabrec, tabscore], plot_options.values()):
            with tab:
                fig = create_bar_chart(selected_df, x, y, title, [0, 4], [y], 'oranges_r')
                st.plotly_chart(fig)
    else:
        st.warning('Please Select Countries to Compare', icon="⚠️")

with tabreg:
    selected_regions = st.multiselect("Select regions for comparison", df_gov_results['region'].unique().tolist())
    if selected_regions:
        region_df = df_gov_results.groupby('region')[['final_score', 'recency', 'num_indicators', 'year_score']].median().reset_index()
        selected_df_region = region_df[region_df['region'].isin(selected_regions)]
        selected_df_region_box = df_gov_results[df_gov_results['region'].isin(selected_regions)]
        # Tabs for plots
        tabindic, tabrec, tabscore, tabbox = st.tabs(['Number of Indicators', 'Recency', 'Ease of Access Score', 'Box-Plots of Ease of Access'])

        # Define plot options for regions
        region_plot_options = {
            'Number of Indicators': ('region', 'num_indicators', 'Number of Indicators'),
            'Recency': ('region', 'year_score', 'Recency of Data'),
            'Ease of Access Score': ('region', 'final_score', 'Ease of Access Score')
        }

        # Create plots for regions using the correct column names
        for tab, (x, y, title) in zip([tabindic, tabrec, tabscore], region_plot_options.values()):
            with tab:
                fig = create_bar_chart(selected_df_region, x, y, title, [0, len(selected_regions) - 1], [y], 'oranges_r')
                st.plotly_chart(fig)
        with tabbox:
            colors = {"Region": {"#0069b4", "#66a6b0", "#fdc237", "#ee2e22", "#a21352"}}
            fig = px.box(selected_df_region_box.sort_values(by=['region'], ascending=True), 
                        x="region", 
                        y="final_score", 
                        color="region")
            fig.update_layout(
                xaxis=dict(title='Region', tickfont=dict(size=20, family="Open Sans")),
                yaxis=dict(title='Value', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            st.write("""
            The box plot illustrates the distribution of 'Ease of Access' scores across African regions. Each box captures the range of scores within a region, with the line marking the median. Outliers represent countries with scores deviating notably from their regional trend.
            """)
    else:
        st.warning('Please Select Regions to Compare', icon="⚠️")

#----------------------
# Methodology Section / footer
st.write("""
## Ease of Access Indicator
""")
tab1, tab3 = st.tabs(["Introduction", "Methodology"])

with tab1:
    text = df_infotext[df_infotext['InfoText_ID'] == 1]['Section'].iloc[0]
    st.write(f"""
    {text}
    """)

with tab3:
    text = df_infotext[df_infotext['InfoText_ID'] == 2]['Section'].iloc[0]
    st.latex(r'''
    Score_{EaseOfAccess} = 0.3 * (Score_{year}) + 0.3 * (Score_{indicators}) + 0.3 * (Machine Readability) + 0.1 * (Security)
    
    ''')
    st.write("""
    * The recency of data was scored between 0 to 5. The exact criteria is available in the dataframe below. 
    * Datasets were scored from 0 to 5 based on the number of indicators they contained. A logarithmic transformation was applied to the number of indicators such that the impact of each additional indicator diminishes as the total number increases. This transformation was aimed to avoid disproportionately high scores for sources with a large number of indicators while still accounting for their comprehensiveness. The scoring was contained to each subset of sources, i.e the transformation was applied at the category level (government, insitutions, ngos). 
    * *MachineReadability* is a binary variable, taking the value one if machine readable data is provided, and zero otherwise. 
    * *Security* is also a binary variable, taking the value one if no warning was given by the internet browser when accessing the website, and 0 otherwise. 
             """)
    df_score = pd.DataFrame(
        {
            'Year_Score' : [0 , 1, 2, 3, 4, 5],
            'Legend' : ['Data not available', 'Data available before the year 2000', 'Data from 2001 to 2006 ', 'Data from 2007 to 2012' , 'Data from 2013 to 2018', 'Data from 2018 and above']
        }
    )
    st.dataframe(df_score)
    st.write(f"""
    {text}
    """)
    
    st.dataframe(df_scorelegend.rename(columns={'Score' : 'Ease of Access Score', 'Legend_Description' : 'Description'}))  # Same as st.write(df)
