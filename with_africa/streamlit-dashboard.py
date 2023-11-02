import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import matplotlib.pyplot as plt
import requests

@st.cache_data
def load_data():
    url = 'https://github.com/dhruv-pandit/Projects/raw/1e99b17eeeb01254051e6b73a158e64e6cef390c/with_africa/tourism_dashboard.sqlite'
    response = requests.get(url)
    with open("tourism_dashboard.sqlite", 'wb') as f:
        f.write(response.content)

    conn = sqlite3.connect('tourism_dashboard.sqlite')
    query = """
    SELECT c.Country_Name as Country, 
        r.Region_Name as Region, 
        c.ISO3_Code, 
        c.Link_to_Statistical_Agency as Link, 
        c.Description as Comments, 
        c.Ease_of_Access_Score as EOA_Score 
    FROM Country c 
    JOIN Region r ON c.Region_ID = r.Region_ID
    """

    # Fetch the data and create a DataFrame
    df = pd.read_sql(query, conn)

    # Close the connection
    conn.close()
    return df

def load_tables():
    url = 'https://github.com/dhruv-pandit/Projects/raw/1e99b17eeeb01254051e6b73a158e64e6cef390c/with_africa/tourism_dashboard.sqlite'
    response = requests.get(url)
    with open("tourism_dashboard.sqlite", 'wb') as f:
        f.write(response.content)

    conn = sqlite3.connect('tourism_dashboard.sqlite')

    # Query the InfoText table and save to a dataframe
    df_infotext = pd.read_sql("SELECT * FROM InfoText", conn)

    # Query the ScoreLegend table and save to a dataframe
    df_scorelegend = pd.read_sql("SELECT * FROM ScoreLegend", conn)
    df_scorelegend.rename(columns = {'Legend_Description' : 'Legend'}, inplace = True)
    # Close the connection
    conn.close()
    return df_infotext, df_scorelegend
df_infotext, df_scorelegend = load_tables()
df_eoa = load_data()
st.title("African Tourism Data Accessibility (2023)")
st.write("""
_____
""")
countries = df_eoa['Country'].unique().tolist()
option = st.selectbox(
    'Select a country',options = countries)
col1, col2 = st.columns(2)

with col1:
    st.write("""
    ## Ease Of Access Score
    ____
    """)
    custom_colorscale = [
        [0, '#Ffe0b2'],
        [0.25, '#ffb74d'],
        [0.5, '#ff9800'],
        [0.75, '#f57c00'],
        [1, '#e65100']
    ]
    df_eoa['EOA_Score'] = df_eoa['EOA_Score'].astype(int)
    min_value = df_eoa['EOA_Score'].min()
    max_value = df_eoa['EOA_Score'].max()

    # Generate a list of integer ticks between the minimum and maximum values
    tick_values = list(range(min_value, max_value + 1))



    # Create the choropleth map figure
    fig_choro = go.Figure(data=go.Choropleth(
        locations=df_eoa['Country'],  # Country names
        z=df_eoa['EOA_Score'],  # Ease of Access scores
        locationmode='country names',  # Use country names as locations
        colorscale=custom_colorscale,  # Use the custom colorscale
        colorbar_title='Ease of Access',
        colorbar_tickvals=tick_values,  # Set the tick values manually
        colorbar_ticktext=tick_values
    ))
    background_color = 'rgb(15, 17, 22)'

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
        font=dict(family="Futura")  # Set the font family to "Futura"
    )

    # Center the title text
    #fig_choro.update_layout(title=dict(x=0.5, y=0.95, xanchor='left', yanchor='top'))

    # Customize hover label font size
    fig_choro.update_layout(hoverlabel=dict(bgcolor='grey', bordercolor='black', font=dict(size=8)))
    # fig.add_annotation(text="Source: WiTH Africa, 2023", xref="paper", yref="paper",
    #                 x=0, y=-0.1, showarrow=False, font=dict(size=15, color="lightgray"))

    st.plotly_chart(fig_choro,  use_container_width=True)

with col2:
    eoa = df_eoa[df_eoa['Country'] == option]['EOA_Score'].iloc[0]
    link = df_eoa[df_eoa['Country'] == option]['Link'].iloc[0]
    comment = df_eoa[df_eoa['Country'] == option]['Comments'].iloc[0]
    st.header(option)
    st.write(f"""
    ______
    ## Score : {eoa}

    {comment}

    Link to Website : {link}
    """)
st.write("Findings reflect the state of the African tourism data ecosystem between late April and early May 2023. Data was rigorously sourced from primary statistical agencies across Africa, supplemented by tourism ministries and central banks where necessary.")

st.write("""
## Ease of Access Indicator
""")

tab1, tab2, tab3 = st.tabs(["Introduction", "Charts", "Methodology"])

with tab1:
    text = df_infotext[df_infotext['InfoText_ID'] == 1]['Section'].iloc[0]
    st.write(f"""
    {text}
    """)

    #st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

with tab2:
    tabmean, tabmedian, tabbox, tabbar = st.tabs(["Mean", "Median", "Box-Plots", "Stacked Bar Plot"])
    with tabmean:
        # Colors and grouped data
        colors = ["#0069b4", "#66a6b0", "#fdc237", "#ee2e22", "#a21352"]
        grouped_df = df_eoa.groupby('Region')['EOA_Score'].mean().reset_index()

        # Create the horizontal bar plot using Plotly
        fig = go.Figure(go.Bar(
            y=grouped_df['Region'],
            x=grouped_df['EOA_Score'],
            orientation='h',
            marker_color=colors,
            text=grouped_df['EOA_Score'].round(1),
            textposition='outside'
        ))

        # Customize the layout
        fig.update_layout(
            title=dict(text='Mean Value by Region', font=dict(size=25, family="Futura", color="white")),
            xaxis=dict(title='Mean Value', tickfont=dict(size=20, family="Futura"), range=[0, 4]),
            yaxis=dict(title='Region', tickfont=dict(size=20, family="Futura")),
            font=dict(family="Futura", size=19),
            showlegend=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            #margin=dict(l=200)  # Adjust left margin for long region names if needed
        )

        st.plotly_chart(fig,  use_container_width=True)
    with tabmedian:
        # Colors and grouped data
        colors = ["#0069b4", "#66a6b0", "#fdc237", "#ee2e22", "#a21352"]
        grouped_df = df_eoa.groupby('Region')['EOA_Score'].median().reset_index()

        # Create the horizontal bar plot using Plotly
        fig = go.Figure(go.Bar(
            y=grouped_df['Region'],
            x=grouped_df['EOA_Score'],
            orientation='h',
            marker_color=colors,
            text=grouped_df['EOA_Score'].round(1),
            textposition='outside'
        ))

        # Customize the layout
        fig.update_layout(
            title=dict(text='Mean Value by Region', font=dict(size=25, family="Futura", color="white")),
            xaxis=dict(title='Mean Value', tickfont=dict(size=20, family="Futura"), range=[0, 4]),
            yaxis=dict(title='Region', tickfont=dict(size=20, family="Futura")),
            font=dict(family="Futura", size=19),
            showlegend=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            #margin=dict(l=200)  # Adjust left margin for long region names if needed
        )

        st.plotly_chart(fig,  use_container_width=True)
    with tabbox:
        # Colors
        colors = {"Region": {"#0069b4", "#66a6b0", "#fdc237", "#ee2e22", "#a21352"}}

        # Create the box plot using plotly express
        fig = px.box(df_eoa.sort_values(by=['Region'], ascending=True), 
                    x="Region", 
                    y="EOA_Score", 
                    color="Region",
                    color_discrete_map=colors)

        # Customize the layout
        fig.update_layout(
            title=dict(text='Box Plot of Values by Region', font=dict(size=25, family="Futura", color="white")),
            xaxis=dict(title='Region', tickfont=dict(size=20, family="Futura")),
            yaxis=dict(title='Value', tickfont=dict(size=20, family="Futura")),
            font=dict(family="Futura", size=19),
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            showlegend=False
        )


        # Show the figure
        st.plotly_chart(fig,  use_container_width=True)
        st.write("""
        The box plot illustrates the distribution of 'Ease of Access' scores across African regions. Each box captures the range of scores within a region, with the line marking the median. Outliers represent countries with scores deviating notably from their regional trend.
        """)
    with tabbar:
        # Ensure the data is in long format suitable for plotly express
        df_long = df_eoa.groupby(['Region', 'EOA_Score']).size().reset_index(name='Count')
        from matplotlib.colors import ListedColormap
        custom_cmap = ListedColormap(['#Ffe0b2', '#ffb74d', '#ff9800', '#f57c00', '#e65100'])

        # Define the colors
        color_map = {
            0: '#Ffe0b2',
            1: '#ffb74d',
            2: '#ff9800',
            3: '#f57c00',
            4: '#e65100'
        }

        # Create the stacked horizontal bar plot
        fig_bar = px.bar(df_long,
                    x='Count',
                    y='Region',
                    color='EOA_Score',
                    orientation='h',
                    title='Stacked Bar Plot Showing the Number of Countries for Each Ease of Access Score by Region',
                    color_discrete_map=color_map,
                    labels={'Ease of Access': 'Ease of Access Score'}
        )

        # Customize the layout
        fig_bar.update_layout(
            barmode='stack',
            xaxis=dict(title='Count', tickfont=dict(size=20, family="Futura")),
            yaxis=dict(title='Region', categoryorder='total ascending', tickfont=dict(size=20, family="Futura")),
            font=dict(family="Futura", size=19),
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            legend_title=dict(text="Ease of Access Score")
        )
        # Show the figure
        st.plotly_chart(fig_bar,  use_container_width=True)



with tab3:
    text = df_infotext[df_infotext['InfoText_ID'] == 2]['Section'].iloc[0]
    st.write(f"""
    {text}
    """)
    
    st.dataframe(df_scorelegend.set_index('Score'))  # Same as st.write(df)

