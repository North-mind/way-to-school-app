import dash
from dash import Input, Output, dcc, html, no_update
import dash_bootstrap_components as dbc
from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout
from layout.pages.map import map_layout
from layout.navbar import navbar
from layout.def_polygon_map import get_df,get_adm_data,prep_map_point,school_types,prep_map,create_grid
import time

df = get_df()

school_types = school_types()

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
            Input('input', 'checked'),
            # Input("loading-input-1", "value")
        ],
    )
    # def input_triggers_spinner(value):
    #    time.sleep(1)

    #    return value

    def display_selected_data(checked):

        fig = prep_map_point(checked)
        
        return fig
    
    # @app.callback(Output("tabs-example-1", "children"), Input("loading-1", "value"))
    # def input_triggers_spinner(value):
    #     time.sleep(1)
    #     return value

    # @app.callback(Output("tab-2", "children"), Input("loading-2", "value"))
    # def input_triggers_spinner(value):
    #     time.sleep(1)
    #     return value

    # @app.callback(Output("tab-3", "children"), Input("loading-3", "value"))
    # def input_triggers_spinner(value):
    #     time.sleep(1)
    #     return value

    # @app.callback(Output("county-choropleth-pow", "children"), Input("loading-input-2", "value"))
    # def input_triggers_spinner(value):
    #     time.sleep(1)
    #     return value

    

    # @app.callback(
    #     Output("county-choropleth-gmi", "figure"),
    #     [
    #         Input('input', 'checked'),
    #       #  Input('school_types-indicator')#,'s_type')
    #     ],dcc.Loading(
                            #     id="loading-3",
                            #     type="default",
                            #     children=html.Div(id="county-choropleth-gmi")
                            # ),
    # )
    # def display_selected_data(checked):#, s_type):

    #     fig_gmi = prep_map('gmi')#,s_type)
        
    #     return fig_gmi

    @app.callback(Output("tabs-example-content-1", "children"), Input("tabs-example-1", "value"))

    def render_content(tab):
        if tab == "tab-1":
            return html.Div(
                [
                    dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=html.Div(id="tab-1")
                            ),
                    html.Div(
                        id="tabs-content'",
                        
                        children=[
                            # dcc.Loading(
                            #     id="loading-1",
                            #     type="default",
                            #     children=html.Div(id="county-choropleth-points")
                            # ),
                            dcc.Graph(id="county-choropleth-points", figure=prep_map_point([0]),
                                ),
                            #dcc.Loading(id='loading-input-1")', type="circle"),
                            
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
                    dcc.Loading(
                                id="loading-2",
                                type="default",
                                children=html.Div(id="tab-2")
                       ),
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Dropdown(list(school_types),value='Szkoła podstawowa',
                                        multi=False,
                                        id='school_types-indicator-1'),
                            dcc.Graph(id="county-choropleth-pow", figure=create_grid(.12, .12)
                                ),
                            # dcc.Loading(
                            #     id="loading-2",
                            #     type="default",
                            #     children=html.Div(id="county-choropleth-pow")
                            # ),
                            # dcc.Tooltip(
                            # #     id="graph-tooltip-1",
                            # #     backvalue=ground_color="darkblue",
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
                    dcc.Loading(
                                id="loading-3",
                                type="default",
                                children=html.Div(id="tab-3")
                            ),
                    html.Div(
                        id="tabs-content'",
                        children=[
                            dcc.Dropdown(list(school_types),value='Szkoła podstawowa',
                                        multi=False,id='school_types-indicator'),
                            dcc.Graph(id="county-choropleth-gmi", figure=prep_map('gmi')
                                ),
                            # dcc.Loading(
                            #     id="loading-3",
                            #     type="default",
                            #     children=html.Div(id="county-choropleth-gmi")
                            # ),
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
            Input('school_types-indicator','value')
        ],
    )
    def display_selected_data(checked, value):
  
        fig_gmi = prep_map('gmi',value, checked)
        
        return fig_gmi

    # @app.callback(Output("county-choropleth-gmi", "children"), Input("loading-input-3", "value"))
    # def input_triggers_spinner(value):
    #     time.sleep(6)
    #     return value
    # def display_selected(checked, value):
  
    #     return f'Output: {value}'
    @app.callback(
        Output("county-choropleth-pow", "figure"),
        [
            Input('input', 'checked'),
            Input('school_types-indicator-1','value')
        ],
    )
    
    def display_selected_data(checked, value):

        fig_pow = create_grid(.12, .12, value)
        
        return fig_pow    
       

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
