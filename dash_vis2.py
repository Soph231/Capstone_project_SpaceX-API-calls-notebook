# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique site names
unique_sites = spacex_df['Launch Site'].unique()
options = [{'label': 'All Sites', 'value': 'All'}] + [{'label': site, 'value': site} for site in unique_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown', 
                 options=options,
                 value='All',
                 placeholder='Select a Launch site here',
                 searchable=True
    ),
    html.Br(),

    # Add a pie chart to show the total successful launches count for all sites
    dcc.Graph(id='success-pie-chart'),
    
    html.P("Payload range (Kg):"),
    
    # Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={int(i): str(i) for i in range(int(min_payload), int(max_payload) + 1000, 1000)},
                    value=[min_payload, max_payload]),
    
    html.Br(),
    
    # Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Define callback to update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All':
        # Calculate total successful launches for all sites
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        fig = px.pie(success_counts, 
                     names=success_counts.index, 
                     values=success_counts.values, 
                     title='Total Successful Launches by Site')
    else:
        # Calculate success vs. failed counts for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_failed_counts = filtered_df['class'].value_counts()
        fig = px.pie(success_failed_counts, 
                     names=['Success', 'Failed'], 
                     values=success_failed_counts.values, 
                     title=f'Success vs. Failed Launches for {selected_site}')
    
    return fig

# Define callback to update scatter chart based on selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if selected_site != 'All':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title=f'Success by Payload Mass for {selected_site}' if selected_site != 'All' else 'Success by Payload Mass for All Sites',
                     labels={'class': 'Launch Outcome'})
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
