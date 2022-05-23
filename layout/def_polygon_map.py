import os
import numpy as np
import pandas as pd
import shapely
import geopandas as gpd
import plotly.express as px

from fiona.crs import from_epsg
from geodata.adm_units import AdmUnits
from sklearn.neighbors import KDTree

import warnings
warnings.filterwarnings("ignore")

data_dir = "data"
geojson_file = "admin_units_pl.geojson"

adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
geo_df = adm_data.get_data(data_level="pow") 

df = pd.read_csv('data/school.csv')

def prep_country_polygon():
    adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
    geo_df = adm_data.get_data(data_level="pow") 
    pow = geo_df[['typ', 'geometry']]

    geo_country = pow.dissolve(by='typ').copy()

    return geo_country

def create_grid():
    geo_country = prep_country_polygon()
    school = df[['lat', 'lon','rspo']]
    school = school[~school['lon'].isnull()]

    ymin,xmin,ymax,xmax = 48.994068,14.185213, 54.70,24.092474
    cell_width  = .1
    cell_height = .1

    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_width, cell_width ):
            for y0 in np.arange(ymin, ymax+cell_height, cell_height):
                x1 = x0-cell_width
                y1 = y0+cell_height
                new_cell = shapely.geometry.box(x0, y0, x1, y1)
                #if new_cell.intersects(g_country):
                #if new_cell.intersects(geo_country.geometry):
                grid_cells.append(new_cell)
                #else:
                #    pass

    cell_df = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=from_epsg(4326))
    cell_df['centroid'] = cell_df.geometry.centroid
    cell_df['is_incentroid'] = cell_df.apply(lambda x: geo_country.contains(x.centroid), axis=1)
    
    cell_df['gps_sz_gmi'] = cell_df['centroid'].apply(lambda x: str(x).split(' ')[2].replace(')',''))
    cell_df['gps_dl_gmi'] = cell_df['centroid'].apply(lambda x: str(x).split(' ')[1].replace('(',''))

    kd = KDTree(school[["lon", "lat"]].values, metric='euclidean')
    k =1
    distances, indices = kd.query(cell_df[["gps_sz_gmi", "gps_dl_gmi"]].values, k = k, return_distance=True, dualtree=True)

    schools_indices = pd.DataFrame(indices)
    schools_distances = pd.DataFrame(distances)

    cell_df = pd.concat([cell_df, schools_indices,schools_distances], axis=1)
    cell_df.columns = ['geometry','centroid','is_incentroid', 'gps_sz_gmi','gps_dl_gmi','rspo','distance']

    dist = pd.DataFrame(distances)
    cell_df_copy = pd.concat([cell_df, dist], axis=1)

    cell_df_copy_2 = cell_df_copy[cell_df_copy['is_incentroid']==True].copy()
    cell_df_copy_2['distance_2'] = cell_df_copy_2['distance']*-1

    fig = px.choropleth_mapbox(
    cell_df_copy_2,
    geojson=cell_df_copy_2.geometry, 
    locations=cell_df_copy_2.index, 
    mapbox_style="carto-positron", 
    zoom=6, 
    color='distance_2',
    color_continuous_scale="Magma",
    opacity=.6,
    height=1000,
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120}, hovermode="closest")
    
    return fig