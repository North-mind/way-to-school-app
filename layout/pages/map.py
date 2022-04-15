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

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Load data
adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))
geo_df = adm_data.get_data(data_level="gmi")
df = pd.read_csv("data/school.csv")

# fig = px.scatter_mapbox(
#      df,
#      lat="lon",
#      lon="lat",
#      hover_name="Nazwa",
#      #hover_data=["Status", "Data_założenia",'Kategoria_szkoły'],
#      mapbox_style="carto-positron",
#      zoom=6,
#      height=900
#  )
# fig.update_layout(
#      margin={"r": 0, "t": 0, "l": 0, "b": 0},
#      mapbox_center={"lat": 52.1089496, "lon": 19.443120},
#  )

# Options
school_types = [
    school_type for school_type in df["Kategoria_szkoły"].unique()
]
public_status = [
    {"label": status, "value": status} for status in df["Status"].unique()
]

#YEARS = [0, 1, 2, 3, 4, 5, 6, 7]external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
YEARS = [0, 6, 10, 17, 23, 33, 57, 440]

wojewodztwo = [
    
    wojewodztwo for wojewodztwo in df["Województwo"].unique()
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
                                dcc.Checklist(list(wojewodztwo),list(wojewodztwo),    
                                            id='wojewodztwo-indicator', inline=False)
                    ],
                    className="m-3 p-3 w-100",
                    style={"background-color": "#2D2C3B", 'color':'white'}

                    
                ),
            ],
        ),
        
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.Div(
                            children=[
                                # html.P(
                                #     id="slider-text",
                                #     children="Ustaw przedział czasowy wieku szkoły:",
                                    
                                # ),
                                # dcc.RangeSlider(
                                #     id="years-slider",
                                #     min=min(YEARS),
                                #     max=max(YEARS),
                                #     value=[1, 440],
                                # ),
                                
                                
                                # dcc.Dropdown(list(school_types),list(school_types),    
                                #             multi=True,id='school_types-indicator')
                            ],
                            className="p-3",
                            style={"background-color": "#2D2C3B", 'color':'white'}
                        ),
                        dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
                        dcc.Tab(label='Mapa szczegółowa', value='tab-1'),
                        #dcc.Dropdown(list(school_types),list(school_types),    
                        #                    multi=True,id='school_types-indicator'),
                        dcc.Tab(label='Powiat', value='tab-2'),
                        dcc.Tab(label='Gmina', value='tab-3'),
                        #dcc.Tab(label='Gmina', value='tab-4')
                        
                        #dcc.Tab(label='Powiat', value='tab-3'),
                        #dcc.Tab(label='Wyznacz drogę do szkoły', value='tab-4'),
                        ]),
                        html.Div(id='tabs-example-content-1'),
                        
                        #html.Div(
                        #    id="tabs-content'",
                        #    children=[
                        #        dcc.Graph(
                        #            id="county-choropleth",
                        #            figure=fig
                        #        ),
                        #    ],
                        #    className="mt-3"
                        #),
                    ],
                    width=8,
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
                                style={"background-color": '#2D2C3B', 'color':'black'}
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
                                    backgroundColor='#2D2C3B'
                                ),
                            ),
                            className="mt-4",
                            
                        ),
                    ],
                    width=4,
                ),
            ]
        ),
    ],
    className="p-5",

    style={"height": "100%", 'backgroundColor':'#1B1B24'}
)
