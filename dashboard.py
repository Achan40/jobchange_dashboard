import dash 
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

# Create pandas dataframe from cleaned data
jobdf = pd.read_csv('cleaneddata.csv')

# Items in dataset for education_level
education_options =  [{'label': i, 'value': i} for i in jobdf['education_level'].unique()]

# Items in dataset for column choice (pie chart selection)
column_options =  [{'label': i, 'value': i} for i in ['major_discipline','gender','education_level']]

# Items in dataset for value choice (pie chart selection)
value_options = [{'label': i, 'value': i} for i in ['target','training_hours']]

# Items in dataset for city selection (bubble chart)
city_options = [{'label': i, 'value': i} for i in jobdf['city'].unique()]

# Create Dash object
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Function to add titles to graphs
def cardTitle(sometext):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H4(sometext),
                ], style={'textAlign': 'center'})
            ])
        )
    ])

# Create layout for first card
card1 = dbc.Card(
    dbc.CardBody([
        cardTitle('Histogram: Education Level v Searching for Job Change'),
        dbc.CardBody([
            dcc.Dropdown(
                id='education-dropdown',
                options=education_options,
                multi=True,
                # All values of education_level will be selected by default
                value=list(jobdf['education_level'].unique())
            ),
            dcc.Graph(id='hist-edu-chart'),
        ])
    ])
)

# Create layout for second card
card2 = dbc.Card(
    dbc.CardBody([
        cardTitle('Pie Chart: User selected variables'),
        dbc.CardBody([
            html.P('Name:'),
            html.Div([
                dcc.Dropdown(
                    id='column-dropdown',
                    options=column_options,
                    clearable=False,
                    value='education_level',
                ),
            ], style = {'textAlign': 'center'}),
            html.P('Value:'),
            html.Div([
                dcc.Dropdown(
                    id='value-dropdown',
                    options=value_options,
                    clearable=True
                ),
            ], style = {'textAlign': 'center'}),
            dcc.Graph(id='multi-pi-chart'),
            html.Div(id='average-training-hours'),
        ])
        
    ])
)

# Create layout for third card
# df.query(city) this should be user selected, x = city dev index, y = training hours, size = experience, color = column options
card3 = dbc.Card(
    dbc.CardBody([
        cardTitle('Bubble Plot: User selected variables'),
        dbc.CardBody([
            html.P('City:'),
            dcc.Dropdown(
                id='city-dropdown',
                options=city_options,
                value='city_1',
            ),
            html.P('Color:'),
            dcc.Dropdown(
                id='column-dropdown-2',
                options=column_options,
            ),
            dcc.Graph(id='bubble-chart'),
            html.P('When a color variable has been selected, click on a bubble to see the corresponding data in the table'),
            dash_table.DataTable(id='bubble-info',columns=[{'name':col, 'id':col} for col in jobdf.columns]),
        ])
    ])
)

# Generate layout
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    card1
                ],width="6"),
                dbc.Col([
                    card2
                ],width="6"),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    card3
                ],width="12"),
            ])
        ]),color="dark"
    )
])

# Visiualizing distribution of job searchers depending on education level
@app.callback(
    Output('hist-edu-chart','figure'),
    Input('education-dropdown','value')
)
def update_hist(selected_edu):
    # .isin method will allow for multiple input selection
    filtered_jobdf = jobdf[jobdf['education_level'].isin(selected_edu)]
    fig = px.histogram(filtered_jobdf, x='education_level', color='target', barmode='group', labels={'education_level': 'Education Level','target': 'Searching for Job Change'})
    return fig

# Pie chart with multiple selections and average training hours output for clicked element
@app.callback(
    Output('multi-pi-chart','figure'),
    Output('average-training-hours','children'),
    Input('column-dropdown','value'),
    Input('value-dropdown','value'),
    Input('multi-pi-chart','clickData')
)
def generate_pie(names,values,clicked_data):
    # Pie chart generation
    fig = px.pie(jobdf, values=values, names=names)
    # Clicked data only works for px.pie(jobdf,values='training_hours', names=names)
    # This is due to the nature of teh training_hours column
    if clicked_data is None or values != 'training_hours':
        return [fig,f'When Value is set to training_hours, click on a color!']
    # Calculating average of selected data
    selected_name = clicked_data['points'][0]['label']
    # All rows for that selected_name given names
    selected_avg_filter = jobdf.loc[jobdf[names] == selected_name]
    # avg of the values column after filter
    selected_avg = selected_avg_filter[[values]].mean()[0]
    return fig, f'The average {values} for {names} is {selected_avg}'

# Bubble Plot with data table
@app.callback(
    Output('bubble-chart','figure'),
    Output('bubble-info','data'),
    Input('city-dropdown','value'),
    Input('column-dropdown-2','value'),
    Input('bubble-chart','clickData')
)
def generate_bubble(city,color,clicked_data):
    fig = px.scatter(jobdf[jobdf['city'] == city], x='company_type',y='training_hours',size='experience',color=color, labels={'company_type': 'Company Type','training_hours': 'Training Hours'})
    # filter by city
    filtered_data = jobdf[jobdf['city'] == city]
    # conditon so that data for city selection will appear without a click
    if clicked_data is None or color is None:
        return fig,filtered_data.to_dict('records')
    else:
        # Index of selected choice in selected color's unique value list
        selected_color = clicked_data['points'][0]['curveNumber']
        # Unique values of the selected color option
        color_options =  filtered_data[color].unique()
        # Filter data table by color clicked
        filtered_data = filtered_data[filtered_data[color] == color_options[selected_color]]
        return fig,filtered_data.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
