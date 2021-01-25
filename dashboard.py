import dash 
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Create pandas dataframe from cleaned data
jobdf = pd.read_csv('cleaneddata.csv')

# Items in dataset for gender column
gender_options =  [{'label': i, 'value': i} for i in jobdf['gender'].unique()]

# Items in dataset for education_level
education_options =  [{'label': i, 'value': i} for i in jobdf['education_level'].unique()]

# Items in dataset in relevant_experience column
relevent_exp_options =  [{'label': i, 'value': i} for i in jobdf['relevent_experience'].unique()]

# Create Dash object
app = dash.Dash()

app.layout = html.Div([
    html.H1('This is a title'),
    dcc.Dropdown(
        id='education-dropdown',
        options=education_options,
        multi=True,
        # All values of education_level will be selected by default
        value=list(jobdf['education_level'].unique())
    ),
    dcc.Graph(id='hist-edu-chart')
])

# Visiualizing distribution of job searchers depending on education level
@app.callback(
    Output('hist-edu-chart','figure'),
    Input('education-dropdown','value')
)
def update_hist(selected_edu):
    # .isin method will allow for multiple input selection
    filtered_jobdf = jobdf[jobdf['education_level'].isin(selected_edu)]
    fig = px.histogram(filtered_jobdf, x='education_level', color='target', barmode='group')
    return fig

# Bar chart for relevent experience v searching for a position
if __name__ == '__main__':
    app.run_server(debug=True)
