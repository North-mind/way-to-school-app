import dash
from dash import Input, Output, dcc, html, no_update
import dash_bootstrap_components as dbc

from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout
from layout.pages.map import map_layout
from layout.navbar import navbar

import pandas as pd
import plotly.express as px
import numpy as np
import os

from geodata.adm_units import AdmUnits

df = pd.read_csv("data/school.csv")

def prep_map_point(teryt_filter:list=[]):

    teryt_filter = [int(teryt) for teryt in teryt_filter ]

    if len(teryt_filter)==1 and teryt_filter[0]==0:
        df_1 = df.copy()
    else:
        df_1 = df[df['kod_terytorialny_powiat'].isin(teryt_filter)].copy()

    fig = px.scatter_mapbox(
        data_frame = df_1,
        lat="lon",
        lon="lat",
        mapbox_style="carto-positron",
        zoom=6,
        height=900,
        color="Kategoria_szkoły",
        hover_data = {'lat':False, 'lon':False, 'Kategoria_szkoły':False},
        hover_name = None,
        opacity=0.8,
        size_max=6,
        #color_discrete_sequence=[to_hex(c) for c in sns.color_palette('BrBG_r', 6)],
    )

    return fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120},hovermode="closest")

def prep_map(data_level:str, teryt_filter:list=[]):
    adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))

    geo_df = adm_data.get_data(data_level=data_level)
    geo_df.teryt = geo_df.teryt.astype(int)
    geo_df.parent_id = geo_df.parent_id.astype(int)

    
    if data_level == 'pow':
        col_cent = 'dl_centroid_pow'
        school_pow = df[['kod_terytorialny_powiat', 'dl_centroid_pow']].groupby('kod_terytorialny_powiat').agg('mean').reset_index()
        geo_pow = pd.merge(geo_df, school_pow, how='inner', left_on="teryt", right_on="kod_terytorialny_powiat") 
    elif data_level == 'gmi':
        col_cent = 'dl_centroid_gmi'
        school_gmi = df[['teryt_geo', 'dl_centroid_gmi']].groupby('teryt_geo').agg('mean').reset_index()
        geo_pow = pd.merge(geo_df, school_gmi, how='inner', left_on="teryt", right_on="teryt_geo")
        
    
    teryt_filter = [int(teryt) for teryt in teryt_filter ]
    if teryt_filter == []:
        geo_pow = geo_pow.copy()
    elif len(teryt_filter)>0 and data_level=='pow':
        geo_pow = geo_pow[geo_pow['teryt'].isin(teryt_filter)]
    elif len(teryt_filter)>0 and data_level=='gmi':
        geo_pow = geo_pow[geo_pow['parent_id'].isin(teryt_filter)]
    
    
    fig_pow = px.choropleth_mapbox(
    geo_pow, geojson=geo_pow.geometry, locations=geo_pow.index, mapbox_style="carto-positron", zoom=6,color=col_cent ,height=900,
    color_continuous_scale="Magma", opacity = 0.6, hover_data=['nazwa','podpowiedz'],labels={'index':data_level,'nazwa': 'Nazwa', 'podpowiedz':'Szczegóły',
    col_cent: "Srednia odległość od centroidy"}
    )

    return fig_pow.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120})


def get_callbacks(app):
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == "/":
            return homepage_layout
        elif pathname == "/map":
            return map_layout
        elif pathname == "/contact":
            return contact_layout

        return dbc.Container(
            children=[
                dbc.Jumbotron(
                    [
                        html.H1("404: Not found", className="text-danger"),
                        html.Hr(),
                        html.P(f"The pathname {pathname} was not recognised..."),
                    ],
                    className="mt-5",
                )
            ]
        )


    @app.callback(
        Output("county-choropleth-points", "figure"),#Output('loading', 'parent_style'),
        [
            Input('input', 'checked')
        ],
    )
    def display_selected_data(checked):

        fig = prep_map_point(checked)
        
        return fig
    
    @app.callback(
        Output("county-choropleth-pow", "figure"),
        [
            Input('input', 'checked')
        ],
    )
    def display_selected_data(checked):

        fig_pow = prep_map('pow', checked)
        
        return fig_pow

    @app.callback(
        Output("county-choropleth-gmi", "figure"),
        [
            Input('input', 'checked')
        ],
    )
    def display_selected_data(checked):

        fig_gmi = prep_map('gmi', checked)
        
        return fig_gmi

    @app.callback(Output("tabs-example-content-1", "children"), Input("tabs-example-1", "value"))

    def render_content(tab):
        if tab == "tab-1":
            return html.Div(
                [
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Graph(id="county-choropleth-points", figure=prep_map_point([0])
                                ),
                            #dcc.Loading(id='loading', parent_style=loading_style),
                            dcc.Tooltip(
                                id="graph-tooltip-1",
                                background_color="darkblue",
                                border_color="white",
                                style={"color": "white", "width": "450px", "white-space": "normal"},
                                loading_text="Wczytywanie danych ...",
                                
                            ),
                        ],
                        className="mt-3",
                    )
                ]
            )
        elif tab == "tab-2":
            return html.Div(
                [
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Graph(id="county-choropleth-pow", figure=prep_map('pow')
                                ),
                            #dcc.Loading(id='loading', parent_style=loading_style),
                            dcc.Tooltip(
                            #     id="graph-tooltip-1",
                            #     background_color="darkblue",
                            #     border_color="white",
                            #     style={"color": "white", "width": "450px", "white-space": "normal"},
                            #     loading_text="Wczytywanie danych ...",
                                
                            ),
                        ],
                        className="mt-3",
                    )
                ]
            )
        elif tab == "tab-3":
            return html.Div(
                [
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Graph(id="county-choropleth-gmi", figure=prep_map('gmi')
                                ),
                            #dcc.Loading(id='loading', parent_style=loading_style),
                            dcc.Tooltip(
                            #     id="graph-tooltip-1",
                            #     background_color="darkblue",
                            #     border_color="white",
                            #     style={"color": "white", "width": "450px", "white-space": "normal"},
                            #     loading_text="Wczytywanie danych ...",
                                
                            ),
                        ],
                        className="mt-3",
                    )
                ]
            )

    @app.callback(
        Output("graph-tooltip-1", "show"),
        Output("graph-tooltip-1", "bbox"),
        Output("graph-tooltip-1", "children"),
        
        Input("county-choropleth-points", "hoverData"),
    )
    def update_tooltip_content(hoverData):
        if hoverData is None:
            return no_update

        pt = hoverData["points"][0]
        bbox = pt["bbox"]
        lat = pt["lat"]
        lon = pt["lon"]

        school = df[(df["lon"] == lat) & (df["lat"] == lon)].head(1)

        def my_repl(value):
            return str(value).replace("['", "").replace("']", "")

        name = my_repl(school["Nazwa"].values)
        kat = my_repl(school["Kategoria_szkoły"].values)
        status = my_repl(school["Status"].values)

        woj = my_repl(school["Województwo"].values)
        pow = my_repl(school["Powiat"].values)
        miejscowosc = my_repl(school["Miejscowość"].values)
        ul = my_repl(school["Ulica"].values)
        nr_bud = my_repl(school["Nr_budynku"].values)
        nr_loc = my_repl(school["Nr_lokalu"].values)

        def adres(ul):
            if ul != "[nan]":
                ulica = my_repl(ul) + " " + my_repl(nr_bud)
            else:
                ulica = my_repl(miejscowosc) + " " + my_repl(nr_bud)

            return ulica

        ulica = adres(ul)

        children = [
            html.P(name, style={"font-weight": "bold", "font-size": "15px"}),
            html.P(f"Typ: {kat} ({status}) \n Miejscowość: {miejscowosc} Adres: {ulica} Woj: {woj}", style={"font-size": "13px"})
        ]

        return True, bbox, children
