import os
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
from layout.styles import MAP_STYLE
from geodata.adm_units import AdmUnits
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
from dash.dependencies import Input, Output
from dash import dash, dcc, html

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# Load data
adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))
geo_df = adm_data.get_data(data_level="gmi")
df = pd.read_csv("data/school.csv")

fig = px.scatter_mapbox(
    df,
    lat="lon",
    lon="lat",
    hover_name="nazwa",
    hover_data=["publicznosc_status", "data_zalozenia", "school_typ_cat"],
    mapbox_style="carto-positron",
    zoom=6,
    height=900
)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox_center={"lat": 52.1089496, "lon": 19.443120},
)

# Options
school_types = [
    school_type for school_type in df["school_typ_cat"].unique()
]
public_status = [
    {"label": status, "value": status} for status in df["publicznosc_status"].unique()
]

#YEARS = [0, 1, 2, 3, 4, 5, 6, 7]external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
YEARS = [6, 10, 17, 23, 33, 57, 440]

wojewodztwo = [
    
    wojewodztwo for wojewodztwo in df["wojewodztwo"].unique()
]

map_layout = html.Div(
    children=[
        dbc.Row(
            children=[
                html.Div(
                    children=[
                        html.H4(children="Szkoły i placówki oświatowe"),
                        html.P(
                            id="description",
                            #children="ffff.",
                        ),
                        html.Label('Wybierz województwo:'),
                                dcc.Dropdown(list(wojewodztwo),list(wojewodztwo),    
                                            multi=True)
                    ],
                    className="m-3 p-3 w-100",
                    style={"background-color": "#f8f9fa"}

                    
                ),
            ],
        ),
        
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.Div(
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Ustaw przedział czasowy wieku szkoły:",

                                ),
                                dcc.RangeSlider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[1, 440],
                                ),
                                
                                
                                dcc.Dropdown(list(school_types),list(school_types),    
                                            multi=True)
                                
                            ],
                            className="p-3",
                            style={"background-color": "#f8f9fa"}
                        ),
                        dcc.Tabs(
                            id="tabs-with-classes-2",
                            value='tab-2',
                            parent_className='custom-tabs',
                            className='custom-tabs-container',
                            children=[
                                dcc.Tab(
                                    label='Mapa szczegółowa',
                                    value='tab-1',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected'
                                ),
                                dcc.Tab(
                                    label='Województwo',
                                    value='tab-2',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected'
                                ),
                                dcc.Tab(
                                    label='Powiat',
                                    value='tab-3', className='custom-tab',
                                    selected_className='custom-tab--selected'
                                ),
                                dcc.Tab(
                                    label='Wyznacz drogę do szkoły',
                                    value='tab-4',
                                    className='custom-tab',
                                    selected_className='custom-tab--selected'
                                ),
                            ]),
                            html.Div(id='tabs-content-classes-2')
                        #html.Div(
                        #    id="id='tabs-content'",
                        #    children=[
                        #        dcc.Graph(
                        #            id="county-choropleth",
                        #            figure=fig
                        #        ),
                        #    ],
                        #    className="mt-3"
                        #),
                    ],
                    width=7,
                ),
                dbc.Col(
                    children=[
                        html.Div(
                            children=[
                                html.P(id="chart-selector", children="Wybierz wykres:"),
                                dcc.Dropdown(
                                    options=[
                                        {
                                            "label": "Histogram of total number of deaths (single year)",
                                            "value": "show_absolute_deaths_single_year",
                                        },
                                        {
                                            "label": "Podział wg statusu szkoły",
                                            "value": "absolute_deaths_all_time",
                                        },
                                        {
                                            "label": "Histogram wieku szkół",
                                            "value": "show_death_rate_single_year",
                                        },
                                        {
                                            "label": "Trends in age-adjusted death rate (1999-2016)",
                                            "value": "death_rate_all_time",
                                        },
                                    ],
                                    value="show_death_rate_single_year",
                                    id="chart-dropdown",

                                ),
                            ],
                                className="p-3",
                                style={"background-color": "#f8f9fa"}
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    template="plotly_dark",
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                            className="mt-4"
                        ),
                    ],
                    width=5,
                ),
            ]
        ),
    ],
    className="p-5",
    style={"height": "100%"}
)

@app.callback(Output('tabs-content-classes-2', 'children'),
              Input('tabs-with-classes-2', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])

if __name__ == "__main__":
    app.run_server(debug=True)
'''
import os
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
from layout.styles import MAP_STYLE
from geodata.adm_units import AdmUnits
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
from dash.dependencies import Input, Output
from dash import dash, dcc, html

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "US Opioid Epidemic"

app.map_layout = html.Div([
    dcc.Tabs(
        id="tabs-with-classes-2",
        value='tab-2',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Tab one',
                value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Tab two',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Tab three, multiline',
                value='tab-3', className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Tab four',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ]),
    html.Div(id='tabs-content-classes-2')
])

@app.callback(Output('tabs-content-classes-2', 'children'),
              Input('tabs-with-classes-2', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])

#if __name__ == '__main__':
#    map_layout.run_server(debug=True)'''
