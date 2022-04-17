import os

import dash_bootstrap_components as dbc
import dash_treeview_antd
import pandas as pd
import plotly.express as px
from dash import dcc, html

from geodata.adm_units import AdmUnits
from layout.styles import MAP_STYLE

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
from dash import dash, dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
)

# theme = {
#     "dark": True,
#     "detail": "#007439",
#     "primary": "#00EA64",
#     "secondary": "#6E6E6E",
# }

df = pd.read_csv("data/school.csv")

def make_treeview_data(filterLevel=0, filterColumn='Województwo', filterValue=None):
    filterType = [
        ['Województwo', 'kod_terytorialny_wojewodztwo'],
        ['Powiat', 'kod_terytorialny_powiat'],
        ['Gmina', 'kod_terytorialny_gmina']
    ]
    if (filterLevel >= len(filterType)) or filterLevel > 1:
        return []
    selectedColumns = filterType[filterLevel]
    
    if filterValue is None:
         uniqChilds = [title for title in df[selectedColumns].drop_duplicates().values]
    else:
         uniqChilds = [title for title in df[df[filterColumn]==filterValue][selectedColumns].drop_duplicates().values]
    return [
        {'title': title, 'key': key, 'children':make_treeview_data(filterLevel+1,selectedColumns[0],title)}
        for title,key in uniqChilds
    ]

data_tree = make_treeview_data()

# Options
school_types = [school_type for school_type in df["Kategoria_szkoły"].unique()]
public_status = [{"label": status, "value": status} for status in df["Status"].unique()]

# YEARS = [0, 1, 2, 3, 4, 5, 6, 7]external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
YEARS = [0, 6, 10, 17, 23, 33, 57, 440]

#wojewodztwo = [wojewodztwo for wojewodztwo in df["Województwo"].unique()]

map_layout = html.Div(
    children=[
        dbc.Row(
            children=[
                html.Div(children=[
                        html.H4("Szkoły i placówki oświatowe"),
                        #html.P(
                        #    id="description",
                            # children="ffff.",
                        #),
                        #html.Label("Wybierz województwo:"),
                        #dcc.Checklist(list(wojewodztwo), list(wojewodztwo), id="wojewodztwo-indicator", inline=False),
                    ],
                    
                    style={"background-color": "#2D2C3B",'color':'white'},
                    className="m-3 p-3 w-100",
                ),
            ],
            style={'color':'white'}
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
                            style={"background-color": "#2D2C3B", "color": "white"},
                        ),
                        dcc.Tabs(
                            id="tabs-example-1",
                            value="tab-1",
                            children=[
                                dcc.Tab(label="Mapa szczegółowa", value="tab-1"),
                                dcc.Tab(label="Powiat", value="tab-2"),
                                dcc.Tab(label="Gmina", value="tab-3"),
                            ],
                        ),
                        html.Div(id="tabs-example-content-1"),
                        # html.Div(
                        #    id="tabs-content'",
                        #    children=[
                        #        dcc.Graph(
                        #            id="county-choropleth",
                        #            figure=fig
                        #        ),
                        #    ],
                        #    className="mt-3"
                        # ),
                    ],
                    width=10,
                ),
                dbc.Col(
                    
                     children=[
                         html.Div(
                             children=[

                                    dash_treeview_antd.TreeView(
                                        id='input',
                                        multiple=True,
                                        checkable=True,
                                        checked=['0'],
                                        selected=['0'],
                                        expanded=['0'],
                                        data={
                                            
                                            'title': 'Polska',
                                            'key': '0',
                                            'children': data_tree
                                            },
                                    ),
                                    html.Div(id='output-checked'),
                                    html.Div(id='output-selected'),
                                    html.Div(id='output-expanded'),],

                    #             html.P(id="chart-selector", children="Wybierz wykres:"),
                    #             dcc.Dropdown(
                    #                 options=[
                    #                     {
                    #                         "label": "Histogram of total number of deaths (single year)",
                    #                         "value": "show_absolute_deaths_single_year",
                    #                     },
                    #                     {
                    #                         "label": "Podział wg statusu szkoły",
                    #                         "value": "absolute_deaths_all_time",
                    #                     },
                    #                     {
                    #                         "label": "Histogram wieku szkół",
                    #                         "value": "show_death_rate_single_year",
                    #                     },
                    #                     {
                    #                         "label": "Trends in age-adjusted death rate (1999-2016)",
                    #                         "value": "death_rate_all_time",
                    #                     },
                    #                 ],
                    #                 value="show_death_rate_single_year",
                    #                 id="chart-dropdown",
                    #             ),
                    #         ],
                    #         className="p-3",
                    #         style={"background-color": "#2D2C3B", "color": "black"},
                    #     ),
                    #     dcc.Graph(
                    #         id="selected-data",
                    #         figure=dict(
                    #             data=[dict(x=0, y=0)],
                    #             layout=dict(
                    #                 paper_bgcolor="#F4F4F8",
                    #                 plot_bgcolor="#F4F4F8",
                    #                 autofill=True,
                    #                 template="plotly_dark",
                    #                 margin=dict(t=75, r=50, b=100, l=50),
                    #                 backgroundColor="#2D2C3B",
                    #             ),
                    #         ),
                    #         className="mt-4",
                         ),
                     ],
                    
                    width=2,
                ),
            ]
        ),
    ],
    className="p-5",
    style={"height": "100%", "backgroundColor": "white",'color':'black'}
)
