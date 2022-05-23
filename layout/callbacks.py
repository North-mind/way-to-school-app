import dash
from dash import Input, Output, dcc, html, no_update
import dash_bootstrap_components as dbc
import geopandas as gpd
#from shapely.geometry import Polygon
import numpy as np
import matplotlib as plt
from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout
from layout.pages.map import map_layout
from layout.navbar import navbar

import pandas as pd
from shapely.geometry import Polygon
import shapely as shapely
import plotly.express as px
import numpy as np
import os
from layout.KDTree_gmi import distance_gmi
from layout.def_polygon_map import create_grid
from fiona.crs import from_epsg
import plotly.graph_objects as go


#from sklearn.neighbors import KDTree

from geodata.adm_units import AdmUnits
      
df = pd.read_csv("data/school.csv", usecols=['rspo','Kategoria_szkoły', 'lon', 'lat', 'kod_terytorialny_powiat','teryt_geo','Nazwa', 'Status','Województwo','Powiat','Miejscowość', 'Ulica', 'Nr_budynku','Nr_lokalu','dl_centroid_pow', 'dl_centroid_gmi'])

school_types = [school_type for school_type in df["Kategoria_szkoły"].unique()]

adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))

#prep polygon for gmi
locations_school = df[['rspo', 'lat', 'lon','Kategoria_szkoły']].copy()
locations_school = locations_school[~locations_school['lon'].isnull()]

geo_df = adm_data.get_data(data_level='gmi')
geo_df.teryt = geo_df.teryt.astype(int)
geo_df['centroid']=geo_df.geometry.centroid
geo_df['gps_sz_gmi'] = geo_df['centroid'].apply(lambda x: str(x).split(' ')[2].replace(')',''))
geo_df['gps_dl_gmi'] = geo_df['centroid'].apply(lambda x: str(x).split(' ')[1].replace('(',''))
locations_gmi = geo_df[['teryt', 'gps_dl_gmi', 'gps_sz_gmi']].copy()


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
        height=1000,
        color="Kategoria_szkoły",
        hover_data = {'lat':False, 'lon':False, 'Kategoria_szkoły':False},
        hover_name = None,
        opacity=0.4,
        size_max=6,
        
        
        #color_discrete_sequence=[matplotlib.to_hex(c) for c in sns.color_palette('BrBG_r', 6)],
    )

    fig.update_layout(
        #mapbox_style="light", 
        margin={"r": 0, "t": 0, "l": 0, "b": 0}, 
        mapbox_center={"lat": 52.1089496, "lon": 19.443120},
        hovermode="closest")

       
    return fig

def prep_map(data_level:str, teryt_filter:list=[1], types_s:list=school_types):
    #adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))

    geo_df = adm_data.get_data(data_level=data_level)
    geo_df.teryt = geo_df.teryt.astype(int)
    geo_df.parent_id = geo_df.parent_id.astype(int)
    #locations_school_1 = locations_school[locations_school['Kategoria_szkoły'].isin(types_s)].copy()
    locations_school_1 = locations_school[['rspo', 'lat', 'lon']]

    if data_level == 'pow':
        col_cent = 'dl_centroid_pow'
        school_pow = df[['kod_terytorialny_powiat', 'dl_centroid_pow']].groupby('kod_terytorialny_powiat').agg('min').reset_index()
        geo_pow = pd.merge(geo_df, school_pow, how='inner', left_on="teryt", right_on="kod_terytorialny_powiat") 
    elif data_level == 'gmi':
        #col_cent = 'dl_centroid_gmi'
        col_cent = 'distance'
        dist_df = distance_gmi(locations_school_1, locations_gmi).copy()

        #school_gmi = df[['teryt_geo', 'dl_centroid_gmi']].groupby('teryt_geo').agg('mean').reset_index()
        #geo_pow = pd.merge(geo_df, school_gmi, how='inner', left_on="teryt", right_on="teryt_geo")
        dist_df.teryt = dist_df.teryt.astype(int)
        geo_pow = pd.merge(geo_df, dist_df, how='left', left_on="teryt", right_on="teryt")
        
    
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
    col_cent: "Najbliższa odległość do centroidy"}
    )

    fig_pow.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120})

    return fig_pow

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

        fig_pow = create_grid()
        
        return fig_pow

    # @app.callback(
    #     Output("county-choropleth-gmi", "figure"),
    #     [
    #         Input('input', 'checked'),
    #         Input('school_types-indicator','s_type')
    #     ],
    # )
    # def display_selected_data(checked, s_type):

    #     fig_gmi = prep_map('gmi', checked,s_type)
        
    #     return fig_gmi

    @app.callback(Output("tabs-example-content-1", "children"), Input("tabs-example-1", "value"))

    def render_content(tab):
        if tab == "tab-1":
            return html.Div(
                [
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Graph(id="county-choropleth-points", figure=prep_map_point([0]),
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
                            dcc.Dropdown(list(school_types),list(school_types),
                                        multi=True,id='school_types-indicator'),
                            dcc.Graph(id="county-choropleth-pow", figure=create_grid()
                                ),
                            # #dcc.Loading(id='loading', parent_style=loading_style),
                            # dcc.Tooltip(
                            # #     id="graph-tooltip-1",
                            # #     background_color="darkblue",
                            # #     border_color="white",
                            # #     style={"color": "white", "width": "450px", "white-space": "normal"},
                            # #     loading_text="Wczytywanie danych ...",
                                
                            # ),
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
                            dcc.Dropdown(list(school_types),list(school_types),
                                        multi=True,id='school_types-indicator'),
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
        Output("county-choropleth-gmi", "figure"),
        [
            Input('input', 'checked'),
            Input('school_types-indicator','s_type')
        ],
    )
    def display_selected_data(checked, s_type):

        fig_gmi = prep_map('gmi', checked,s_type)
        
        return fig_gmi

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
