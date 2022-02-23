# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                                ],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site                        
                                html.Div([ ], id='success-pie-chart'),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div([ ], id='success-payload-scatter-chart'),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback([Output(component_id='success-pie-chart', component_property='children')],
              [Input(component_id='site-dropdown', component_property='value')])
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        succ_data = spacex_df[spacex_df['class'] == 1]
        pie_fig = px.pie(succ_data, values='class', names='Launch Site', title='Total success launches by sites')
        return [dcc.Graph(figure=pie_fig)]
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_succ_count = (site_df['class']==1).sum()
        site_fail_count = site_df.shape[0] - site_succ_count
        
        pie_fig = px.pie(values=[site_succ_count, site_fail_count], names=['Success', 'Failed'], title=entered_site + ' : Success vs. Failed')
        return [dcc.Graph(figure=pie_fig)]          


@app.callback([Output(component_id='success-payload-scatter-chart', component_property='children')],
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_success_payload_chart(site, payload_range):
    low, high = payload_range
    
    if site == 'ALL':
        payload_mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
        scatt_fig = fig = px.scatter(
                                        spacex_df[payload_mask], x="Payload Mass (kg)", y="class", 
                                        color="Booster Version Category", hover_data=['Booster Version'],
                                        title='Correlation between Payload and Success for all sites'
                                    )
        return [dcc.Graph(figure=scatt_fig)]
    else:
        payload_mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high) & (spacex_df['Launch Site'] == site)        
        scatt_fig = fig = px.scatter(
                                        spacex_df[payload_mask], x="Payload Mass (kg)", y="class", 
                                        color="Booster Version Category", hover_data=['Booster Version'],
                                        title='Correlation between Payload and Success for site ' + site
                                    )
        return [dcc.Graph(figure=scatt_fig)]

    
# Run the app
if __name__ == '__main__':
    app.run_server()
