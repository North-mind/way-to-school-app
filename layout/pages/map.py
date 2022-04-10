import os
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
from layout.styles import MAP_STYLE
from geodata.adm_units import AdmUnits


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
    {"label": school_type, "value": school_type}
    for school_type in df["school_typ_cat"].unique()
]
public_status = [
    {"label": status, "value": status} for status in df["publicznosc_status"].unique()
]

YEARS = [0, 1, 2, 3, 4, 5, 6, 7]

map_layout = html.Div(
    children=[
        dbc.Row(
            children=[
                html.Div(
                    children=[
                        html.H4(children="Rate of US Poison-Induced Deaths"),
                        html.P(
                            id="description",
                            children="† Deaths are classified using the International Classification of Diseases, \
                                    Tenth Revision (ICD–10). Drug-poisoning deaths are defined as having ICD–10 underlying \
                                    cause-of-death codes X40–X44 (unintentional), X60–X64 (suicide), X85 (homicide), or Y10–Y14 \
                                    (undetermined intent).",
                        ),
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
                                    children="Ustaw przedział czasowy:",

                                ),
                                dcc.RangeSlider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[1, 3],
                                ),
                            ],
                            className="p-3",
                            style={"background-color": "#f8f9fa"}
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=fig
                                ),
                            ],
                            className="mt-3"
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    children=[
                        html.Div(
                            children=[
                                html.P(id="chart-selector", children="Select chart:"),
                                dcc.Dropdown(
                                    options=[
                                        {
                                            "label": "Histogram of total number of deaths (single year)",
                                            "value": "show_absolute_deaths_single_year",
                                        },
                                        {
                                            "label": "Histogram of total number of deaths (1999-2016)",
                                            "value": "absolute_deaths_all_time",
                                        },
                                        {
                                            "label": "Age-adjusted death rate (single year)",
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
                    width=6,
                ),
            ]
        ),
    ],
    className="p-5",
    style={"height": "100%"}
)
