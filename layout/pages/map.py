from dash import html

# Load data
adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))
geo_df = adm_data.get_data(data_level="gmi")
df = pd.read_csv("data/school.csv")

fig = px.scatter_mapbox(df,
                        lat="lon",
                        lon="lat",
                        hover_name="nazwa",
                        hover_data=[
                            "publicznosc_status",
                            "data_zalozenia",
                            "school_typ_cat"
                        ],
                        mapbox_style="carto-positron",
                        zoom=6,
                        height=900)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120})

# Options
school_types = [{"label": school_type, "value": school_type} for school_type in df["school_typ_cat"].unique()]
public_status = [{"label": status, "value": status} for status in df["publicznosc_status"].unique()]


map_layout = dbc.Row(
    [
        dbc.Col(dbc.Container(
            children=[
                dbc.Label("Typ szkoły:", className="mt-5"),
                dbc.Select(
                    id="school_type",
                    options=school_types
                ),
                dbc.Label("Rodzaj szkoły (prywatna/publiczna)"),
                dbc.Select(
                    id="school_public_status",
                    options=public_status
                )
            ],
            fluid=True
        ), width=2),
        dbc.Col(html.Div(
            dcc.Graph(figure=fig, style={'width': '100%', 'height': '90vh'})
        ), width=10),
    ],
    className="g-0",
    style=MAP_STYLE,
    no_gutters=True
)
