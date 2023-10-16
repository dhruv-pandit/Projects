import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import plotly.graph_objs as go
import numpy as np
import itertools
import statsmodels.tsa.vector_ar.vecm as vecm

# Load the data
data_df = pd.read_excel(r'/Users/dhruvpandit/Documents/GitHub/Projects/Macroeconometrics/macrodata.xlsm', index_col='Date')
data_df.rename(columns={' GBP-EOM-VAL-CUR': 'GBP',
                        'USD-EOM-VAL-CUR': 'USD',
                        'CPI-YOY-ROC-PERC': 'CPI',
                        'IR-L-IND-CONCRED-PERC': 'IR-C',
                        'IR-L-IND-HOU-PERC': 'IR-H',
                        'GAC-BM-MIL-EUR': 'GAC'}, inplace=True)
data_df['GAC'] = data_df['GAC'] / 1000
data_df['USD'] = data_df['USD'] / 10000
data_df['GBP_d'] = data_df['GBP'].diff()
data_df['USD_d'] = data_df['USD'].diff()
data_df['CPI_d'] = data_df['CPI'].diff()
data_df['IR-C_d'] = data_df['IR-C'].diff()
data_df['IR-H_d'] = data_df['IR-H'].diff()
data_df['GAC_d'] = data_df['GAC'].diff()
data_df.dropna(inplace=True)
vars_order_d = ['CPI_d', 'GBP_d', 'USD_d', 'IR-C_d', 'IR-H_d', 'GAC_d']
# Define the lag length
lags = 2
# Split the data into training and testing sets (e.g., 80% for training and 20% for testing)
nobs = int(len(data_df) * 0.9)
train, test = data_df[0:nobs], data_df[nobs:]

# Define the variables and their order (CPI is the dependent variable)
y_vars_d = ['CPI_d']
x_vars_d = ['GBP_d',
 'USD_d',
 'IR-C_d',
 'IR-H_d',
 'GAC_d']
y_vars = ['CPI']
x_vars = ['GBP',
 'USD',
 'IR-C',
 'IR-H',
 'GAC']
vars_order = y_vars+x_vars
vars_order_d = y_vars_d+x_vars_d

vecm_order = vecm.select_order(train[vars_order], maxlags = 10)
from statsmodels.tsa.api import VECM
model = VECM(train[['CPI','GBP', 'USD', 'IR-H', 'IR-C', 'GAC']], k_ar_diff=0, coint_rank=1)
result = model.fit()
# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # Header
    html.Header([
        html.H1("Macroeconometrics Dashboard", style={'text-align': 'center'}),
    ], style={'padding': '20px'}),
    
    # Layout for Variable Selection and Time Series Plots (Left Section)
    html.Div([
        # Variable Selection Section
        html.Div([
            # Variable Dropdown
            html.Label("Select Variable(s):"),
            dcc.Dropdown(
                id="variable-selector",
                options=[
                    {'label': variable, 'value': variable} for variable in data_df.columns
                ],
                multi=True  # Allow multiple variable selection
            ),
        ]),
        
        # Date Range Picker
        html.Div([
            html.Label("Select Timeframe:"),
            dcc.DatePickerRange(
                id="date-range-selector",
                start_date=data_df.index.min(),
                end_date=data_df.index.max()
            ),
        ]),
        
        # Time Series Plots Section
        html.Section([
            dcc.Graph(id="time-series-plots"),
        ]),
    ], style={'width': '45%', 'margin': '10px', 'float': 'left'}),
    
    # Layout for ACF/PACF Selection and Plots (Right Section)
    html.Div([
        # ACF/PACF Selection Section
        html.Div([
            # Radio Buttons for ACF and PACF choice
            html.Label("Select ACF/PACF:"),
            dcc.RadioItems(
                id="acf-pacf-selector",
                options=[
                    {'label': 'ACF', 'value': 'acf'},
                    {'label': 'PACF', 'value': 'pacf'}
                ],
                value='acf',  # Default selection
                labelStyle={'display': 'block'}
            ),
            
            # Dropdown for variable selection
            html.Label("Select Variable:"),
            dcc.Dropdown(
                id="variable-acf-pacf-selector",
                options=[
                    {'label': variable, 'value': variable} for variable in data_df.columns
                ],
            ),
        ]),
        
        # ACF/PACF Plots Section
        html.Section([
            dcc.Graph(id="acf-pacf-plots"),
        ]),
    ], style={'width': '45%', 'margin': '10px', 'float': 'right'}),



])

# Define a callback function to update the Granger test results


# Define callback to update ACF and PACF plots based on user input
@app.callback(
    Output("acf-pacf-plots", "figure"),
    Input("variable-acf-pacf-selector", "value"),
    Input("acf-pacf-selector", "value")
)
def update_acf_pacf_plots(selected_variable, acf_or_pacf):
    if not selected_variable:
        return {}

    lags = 10  # Number of lags for ACF/PACF
    title = f"{acf_or_pacf.upper()} Plot for {selected_variable}"

    data = data_df[selected_variable]
    
    if acf_or_pacf == 'acf':
        vals_to_plot = sm.tsa.acf(data, nlags=lags)
        plot_type = 'ACF'
    else:
        vals_to_plot = sm.tsa.pacf(data, nlags=lags)
        plot_type = 'PACF'

    lags = np.arange(len(vals_to_plot))
    fig = go.Figure(data=[
        go.Bar(x=lags, y=vals_to_plot, name=plot_type)
    ])

    fig.update_layout(title=title, xaxis_title='Lag', yaxis_title=plot_type)

    return fig
# Define callback to update time series plots based on variable selection and timeframe
@app.callback(
    Output("time-series-plots", "figure"),
    Input("variable-selector", "value"),
    Input("date-range-selector", "start_date"),
    Input("date-range-selector", "end_date")
)
def update_time_series_plots(selected_variables, start_date, end_date):
    if not selected_variables:
        return {}

    filtered_df = data_df.loc[start_date:end_date, selected_variables]
    fig = px.line(
        filtered_df,
        x=filtered_df.index,
        y=selected_variables,
        labels={'index': 'Date', 'value': 'Value'},
        title="Time Series Plots"
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
