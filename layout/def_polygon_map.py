import os
import numpy as np
import pandas as pd
import shapely
import geopandas as gpd
import plotly.express as px

from fiona.crs import from_epsg
from geodata.adm_units import AdmUnits
from sklearn.neighbors import KDTree, BallTree

import warnings
warnings.filterwarnings("ignore")

data_dir = "data"
geojson_file = "admin_units_pl.geojson"

adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
geo_df = adm_data.get_data(data_level="pow") 

df = pd.read_csv('data/school.csv')
df_school = df[['rspo','Kategoria_szkoły', 'lon', 'lat', 'kod_terytorialny_powiat','teryt_geo','Nazwa', 'Status','Województwo','Miejscowość']].copy()

def KDTree_find_points(df_school, df_polygon, k:int=1):

    kd = KDTree(df_school[["lon", "lat"]].values, metric='euclidean')
    k = k
    distances, indices = kd.query(df_polygon[["gps_sz_gmi", "gps_dl_gmi"]].values, k = k)

    return distances, indices

def BallTree_find_points(df_school, df_polygon, k:int=1):

    for column in df_school[["lon", "lat"]]:
        rad = np.deg2rad(df_school[column].values)
        df_school[f'{column}_rad'] = rad
    
    for column in df_polygon[["gps_sz_gmi", "gps_dl_gmi"]]:
        rad = np.deg2rad(df_polygon[column].values)
        df_polygon[f'{column}_rad'] = rad

    ball = BallTree(df_school[["lat_rad", "lon_rad"]].values, metric='haversine')
    k = 1

    distances, indices = ball.query(df_polygon[["gps_sz_gmi_rad", "gps_dl_gmi_rad"]].values, k = k)
    return distances, indices

def init_data(geo_df):
    global g_country
    country_regions = geo_df.geometry.explode().tolist()
    max_region = max(country_regions, key=lambda a: a.area)
    g_country = max_region

    return g_country

def prep_country_polygon():
    adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
    geo_df = adm_data.get_data(data_level="pow") 
    pow = geo_df[['typ', 'geometry']]

    geo_country = pow.dissolve(by='typ').copy()

    return geo_country

def create_grid(w:float=.1, h:float=.1):
    geo_country = prep_country_polygon()
    school = df[['lat', 'lon','rspo', 'Nazwa', 'Miejscowość', 'Województwo']]
    school = school[~school['lon'].isnull()]
    g_country = init_data(geo_country)
    ymin,xmin,ymax,xmax = 48.994068,14.185213, 54.70,24.092474
    cell_width  = w
    cell_height = h

    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_width, cell_width ):
        for y0 in np.arange(ymin, ymax+cell_height, cell_height):
            x1 = x0-cell_width
            y1 = y0+cell_height
            new_cell = shapely.geometry.box(x0, y0, x1, y1)
            #if new_cell.intersects(g_country):
            if new_cell.intersects(g_country):
                grid_cells.append(new_cell)
            else:
                pass

    cell_df = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=from_epsg(4326))
    cell_df['centroid'] = cell_df.geometry.centroid
    cell_df['is_incentroid'] = cell_df.apply(lambda x: geo_country.contains(x.centroid), axis=1)
    cell_df['gps_sz_gmi'] = cell_df['centroid'].apply(lambda x: str(x).split(' ')[2].replace(')',''))
    cell_df['gps_dl_gmi'] = cell_df['centroid'].apply(lambda x: str(x).split(' ')[1].replace('(',''))

    kd = KDTree(school[["lon", "lat"]].values, metric='euclidean')
    k =1
    distances, indices = kd.query(cell_df[["gps_sz_gmi", "gps_dl_gmi"]].values, k = k)

    schools_distances = pd.DataFrame(distances)
  
    result = [[school.iloc[idx].rspo for idx in idx_set] for idx_set in indices]
    res = pd.DataFrame(result)
    cell_df = pd.concat([cell_df, res,schools_distances], axis=1)
    cell_df.columns = ['geometry','centroid','is_incentroid', 'gps_sz_gmi','gps_dl_gmi','indices_index','distance']
    
    cell_df = cell_df.merge(school, left_on="indices_index", right_on='rspo', how='left')

    cell_df_copy_2 = cell_df[cell_df['is_incentroid']==True].copy()

    cell_df['distance_2'] = cell_df['distance']*-1
    #cell_df = cell_df[cell_df['is_incentroid']==True]

    fig = px.choropleth_mapbox(
    cell_df,
    geojson=cell_df.geometry, 
    locations=cell_df.index, 
    mapbox_style="carto-positron", 
    hover_data = {'lon':True, 'lat':True,'gps_sz_gmi':True, 'gps_dl_gmi':True, 'Nazwa':True, 'Miejscowość':True, "Województwo":True},
    zoom=6, 
    color='distance_2',
    color_continuous_scale="Magma",
    opacity=.6,
    height=1000,
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120}, hovermode="closest")

    return fig