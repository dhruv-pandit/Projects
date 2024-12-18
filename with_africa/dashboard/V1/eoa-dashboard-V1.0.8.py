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
#st.set_page_config(layout="wide")

@st.cache_data
def load_data_new():
    url = 'https://github.com/dhruv-pandit/Projects/raw/main/with_africa/dashboard/results.xlsx'
    df_org_results = pd.read_excel(url, sheet_name='organisations')
    df_ngos_results = pd.read_excel(url, sheet_name='ngos')
    df_gov_results = pd.read_excel(url, sheet_name='government_sources')
    return df_gov_results, df_ngos_results, df_org_results

def load_tables():
    url = 'https://github.com/dhruv-pandit/Projects/raw/main/with_africa/with_eoa_copy.xlsx'
    df_infotext = pd.read_excel(url, sheet_name = 'infottext_new')

    # Query the ScoreLegend table and save to a dataframe
    df_scorelegend = pd.read_excel(url, sheet_name = 'legend_new')

    return df_infotext, df_scorelegend


df_infotext, df_scorelegend = load_tables()
df_gov_results, df_ngos_results, df_org_results = load_data_new()

st.title("African Tourism Data Accessibility (2023)")
st.write("""
    Version 1.0.4
    (**please click on three dots > settings > click on wide mode and change theme to light mode**) 
_____

""")
countries = df_gov_results['country'].unique().tolist()

col1, col2 = st.columns(2)

with col1:
    option = st.selectbox(
    'Select an Indicator',options = ['Ease of Access Score', 'Recency of Data', 'Machine Readability Data Available', 'Number of Indicators'])
    st.write(f"""
    ## {option}
    ____
    """)

    dic = {
        'Recency of Data' : 'recency',
        'Ease of Access Score': 'final_score', 
        'Machine Readability Data Available' : 'machine_read', 
        'Number of Indicators' : 'num_indicators'
    }
    custom_colorscale = [
        [0, '#Ffe0b2'],
        [0.25, '#ffb74d'],
        [0.5, '#ff9800'],
        [0.75, '#f57c00'],
        [1, '#e65100']
    ]

    min_value = df_gov_results[dic[option]].min()
    max_value = df_gov_results[dic[option]].max()

    # Generate a list of integer ticks between the minimum and maximum values
    tick_values = list(range(int(min_value), int(max_value) + 1))

    # Create the choropleth map figure


    
    if option == 'Machine Readability Data Available':
        fig_choro = go.Figure(data=go.Choropleth(
            locations=df_gov_results['country'],  # Country names
            z=df_gov_results[dic[option]],  # Ease of Access scores
            locationmode='country names',  # Use country names as locations
            colorscale='oranges_r',  # Use the custom colorscale
            colorbar_title=option,
            colorbar_tickvals=tick_values,  # Set the tick values manually
            colorbar_ticktext=tick_values
        ))
    else: 
        fig_choro = go.Figure(data=go.Choropleth(
            locations=df_gov_results['country'],  # Country names
            z=df_gov_results[dic[option]],  # Ease of Access scores
            locationmode='country names',  # Use country names as locations
            colorscale='oranges_r',  # Use the custom colorscale
            colorbar_title=option,
            # colorbar_tickvals=tick_values,  # Set the tick values manually
            # colorbar_ticktext=tick_values
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

    # Center the title text
    #fig_choro.update_layout(title=dict(x=0.5, y=0.95, xanchor='left', yanchor='top'))

    # Customize hover label font size
    fig_choro.update_layout(hoverlabel=dict(bgcolor='grey', bordercolor='black', font=dict(size=8)))
    fig_choro.add_annotation(text="Source: WiTH Africa, 2023, Lighter shades indicate better performance", xref="paper", yref="paper",
                    x=0, y=-0.1, showarrow=False, font=dict(size=15, color="lightgray"))

    st.plotly_chart(fig_choro,  use_container_width=True)
    st.write("Findings reflect the state of the African tourism data ecosystem between late August and early October 2023. Data was rigorously sourced from primary statistical agencies across Africa, supplemented by tourism ministries and central banks where necessary.")

with col2:
    option = st.selectbox(
    'Select a country',options = countries)
    eoa = df_gov_results[df_gov_results['country'] == option]['final_score'].iloc[0]
    link = df_gov_results[df_gov_results['country'] == option]['link'].iloc[0]
    comment = df_gov_results[df_gov_results['country'] == option]['comments'].iloc[0]
    num_indic = df_gov_results[df_gov_results['country'] == option]['num_indicators'].iloc[0]

    machine_read = ['Available' if df_gov_results[df_gov_results['country'] == option]['machine_read'].iloc[0] == 1 else 'Not Available']
    security_stat = ['Warning Present' if df_gov_results[df_gov_results['country'] == option]['security_warning'].iloc[0] == 0 else 'No Warning']

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

st.write("""
         # WiTH Africa Continental Crosscheck
         Welcome to the comparison section of our dashboard! Here, you can dive deep into the data accessibility metrics of multiple countries and regions side-by-side. Use the tabs to switch between countries and regions. 
         Use the multi-select dropdown to pick the countries or regions you're interested in. The visualizations will adjust based on your selections.
         """)
# Multi-select widget for selecting countries

tabcount, tabreg = st.tabs(['Countries', 'Regions'])
with tabcount:
    selected_countries = st.multiselect("Select countries for comparison", df_gov_results['country'].tolist())

    if selected_countries:
        selected_df = df_gov_results[df_gov_results['country'].isin(selected_countries)]
        
        # Tabs for plots
        tabindic, tabrec, tabscore = st.tabs(['Number of Indicators', 'Recency', 'Ease of Access Score'])

        with tabindic:
            fig = px.bar(selected_df, x='country', y='num_indicators', color='num_indicators',hover_data = ['recency','num_indicators'],

                                            color_continuous_scale= 'oranges_r', width = 1000)
            fig.update_layout(
                xaxis=dict(title='Country', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Number of Indicators', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),

                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Number of Indicators")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            )
            st.plotly_chart(fig)
        with tabrec:
            fig = px.bar(selected_df,
                    x='country',
                    y='year_score',
                    color='recency', 
                    hover_data = ['recency'],
                    color_continuous_scale= 'oranges_r'
                    )  # Color based on recency
            fig.update_layout(
                xaxis=dict(title='Country', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Recency of Data', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Recency")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            )        
            st.plotly_chart(fig)
        with tabscore:
            fig = px.bar(selected_df, x='country', y='final_score', color='final_score',hover_data = ['recency','final_score'],
                                            color_continuous_scale= 'oranges_r')
            fig.update_layout(
                xaxis=dict(title='Country', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Ease of Access Score', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Ease of Access Score")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            ) 
            st.plotly_chart(fig)
    else:
        st.warning('Please Select Countries to Compare', icon="⚠️")

with tabreg:
    selected_regions = st.multiselect("Select regions for comparison", df_gov_results['region'].unique().tolist())
    region_df =  df_gov_results.groupby('region')[['final_score', 'recency', 'num_indicators', 'year_score']].median().reset_index()


    if selected_regions:
        selected_df_region = region_df[region_df['region'].isin(selected_regions)]
        selected_df_region_box = df_gov_results[df_gov_results['region'].isin(selected_regions)]

        # Tabs for plots
        tabindic, tabrec, tabscore, tabbox = st.tabs(['Number of Indicators', 'Recency', 'Ease of Access Score', 'Box-Plots of Ease of Access'])

        with tabindic:
            fig = px.bar(selected_df_region, x='region', y='num_indicators', color='num_indicators',hover_data = ['recency','num_indicators'],
                                            color_continuous_scale= 'oranges_r', width=1000)
            fig.update_layout(
                xaxis=dict(title='Region', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Number of Indicators', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Number of Indicators")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            )
            st.plotly_chart(fig)
        with tabrec:
            fig = px.bar(selected_df_region,
                    x='region',
                    y='year_score',
                    color='recency', 
                    hover_data = ['recency'],
                    color_continuous_scale= 'oranges_r', width=1000
                    )  # Color based on recency
            fig.update_layout(
                xaxis=dict(title='Region', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Recency of Data', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Recency")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            )        
            st.plotly_chart(fig)
        with tabscore:
            fig = px.bar(selected_df_region, x='region', y='final_score', color='final_score',hover_data = ['recency','final_score'],
                                            color_continuous_scale= 'oranges_r', width=1000)
            fig.update_layout(
                xaxis=dict(title='Region', tickfont=dict(size=20, family="Open Sans"), range=[0, 4]),
                yaxis=dict(title='Ease of Access Score', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                coloraxis_colorbar=dict(title="Ease of Access Score")
                #margin=dict(l=200)  # Adjust left margin for long region names if needed
            ) 
            st.plotly_chart(fig)

        with tabbox:
            # Colors
            colors = {"Region": {"#0069b4", "#66a6b0", "#fdc237", "#ee2e22", "#a21352"}}

            # Create the box plot using plotly express
            fig = px.box(selected_df_region_box.sort_values(by=['region'], ascending=True), 
                        x="region", 
                        y="final_score", 
                        color="region", width=1000)

            # Customize the layout
            fig.update_layout(
                xaxis=dict(title='Region', tickfont=dict(size=20, family="Open Sans")),
                yaxis=dict(title='Value', tickfont=dict(size=20, family="Open Sans")),
                font=dict(family="Open Sans", size=19),
                plot_bgcolor=background_color,
                paper_bgcolor=background_color,
                showlegend=False
            )


            # Show the figure
            st.plotly_chart(fig,  use_container_width=True)
            st.write("""
            The box plot illustrates the distribution of 'Ease of Access' scores across African regions. Each box captures the range of scores within a region, with the line marking the median. Outliers represent countries with scores deviating notably from their regional trend.
            """)
    else:
        st.warning('Please Select Regions to Compare', icon="⚠️")





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

