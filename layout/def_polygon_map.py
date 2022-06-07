import os
import numpy as np
import pandas as pd
import shapely
import geopandas as gpd
import plotly.express as px

from fiona.crs import from_epsg
from geodata.adm_units import AdmUnits
from sklearn.neighbors import KDTree, BallTree
from layout.KDTree_gmi import distance_gmi

import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('data/school.csv')

locations_school = df[['rspo', 'lat', 'lon','Kategoria_szkoły']].copy()

locations_school = locations_school[~locations_school['lat'].isnull()]


#dataframe
def get_df():
    df_school = df[['rspo','Kategoria_szkoły', 'lon', 'lat', 'kod_terytorialny_powiat','teryt_geo','Nazwa', 'Status','Województwo','Miejscowość','Powiat', 'Ulica','Nr_budynku','Nr_lokalu']].copy()

    return df_school

def school_types():
    school_types = [school_type for school_type in df["Kategoria_szkoły"].unique()]

    return school_types

def get_adm_data(data_level:str):
    data_dir = "data"
    geojson_file = "admin_units_pl.geojson"

    adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
    geo_df = adm_data.get_data(data_level=data_level) 
    
    return geo_df


#maps
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
    
def prep_map(data_level:str, types_s:str='Szkoła podstawowa', teryt_filter:list=[1]):
    
    geo_df = get_adm_data(data_level)
    geo_df.teryt = geo_df.teryt.astype(int)
    geo_df.parent_id = geo_df.parent_id.astype(int)
    #locations_school_1 = locations_school[locations_school['Kategoria_szkoły'].isin(types_s)].copy()
    #locations_school_ = locations_school[locations_school['Kategoria_szkoły'].isin['Szkoła podstawowa']].copy()
   #typ = locations_school["Kategoria_szkoły"]==types_s)
     # if types_s:
    #     typ = [types_s]
    # else:
    #     typ = school_type
    # displaying data with gender = male only
    locations_school_ = locations_school[locations_school["Kategoria_szkoły"]==types_s]
    #locations_school_ = locations_school.copy()teryt_filter = [int(teryt) for teryt in teryt_filter ]
    # if len(teryt_filter)>0 and data_level=='pow':
    #     geo_pow = geo_pow[geo_pow['teryt'].isin(teryt_filter)]
    # elif teryt_filter[0] != 1 and len(teryt_filter)!=1 and data_level=='gmi':
    #     geo_pow = geo_pow[(geo_pow['parent_id'].isin(teryt_filter))]
    
    locations_school_1 = locations_school_[['rspo', 'lat', 'lon']]
    geo_df['centroid']=geo_df.geometry.centroid
    geo_df['gps_sz_gmi'] = geo_df['centroid'].apply(lambda x: str(x).split(' ')[2].replace(')',''))
    geo_df['gps_dl_gmi'] = geo_df['centroid'].apply(lambda x: str(x).split(' ')[1].replace('(',''))
    locations_gmi = geo_df[['teryt', 'gps_dl_gmi', 'gps_sz_gmi']].copy()

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
    if teryt_filter[0] == 1:
        geo_pow = geo_pow.copy()
    elif len(teryt_filter)>0 and data_level=='pow':
        geo_pow = geo_pow[geo_pow['teryt'].isin(teryt_filter)]
    elif teryt_filter[0] != 1 and len(teryt_filter)!=1 and data_level=='gmi':
        geo_pow = geo_pow[(geo_pow['parent_id'].isin(teryt_filter))]
    
    
    fig_pow = px.choropleth_mapbox(
    geo_pow, geojson=geo_pow.geometry, locations=geo_pow.index, mapbox_style="carto-positron", zoom=6,color=col_cent ,height=900,
    color_continuous_scale="Magma", opacity = 0.6, hover_data=['nazwa','podpowiedz'],labels={'index':data_level,'nazwa': 'Nazwa', 'podpowiedz':'Szczegóły',
    col_cent: "Najbliższa odległość do centroidy"}
    )

    fig_pow.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120})

    return fig_pow

#grid
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
    #adm_data = AdmUnits(data_path=os.path.join(data_dir, geojson_file))
    geo_df = get_adm_data(data_level="pow") 
    pow = geo_df[['typ', 'geometry']]
    geo_country = pow.dissolve(by='typ').copy()

    return geo_country


def create_grid(w:float=.15, h:float=.15, school_type:str='Szkoła podstawowa', teryt_filter:list=[]):
    geo_country = prep_country_polygon()
    school = df[df['Kategoria_szkoły']==school_type][['lat', 'lon','rspo', 'Nazwa', 'Miejscowość', 'Województwo']].copy()
    school = school[~school['lon'].isnull()]
    g_country = init_data(geo_country)
    
    geo_gmi = get_adm_data('gmi')
    geo_gmi.teryt = geo_gmi.teryt.astype(int)

    ymin,xmin,ymax,xmax = 48.994068,14.185213, 54.70,24.092474
    #xmin, ymin, xmax, ymax= geo_country.total_bounds
    cell_width  = w
    cell_height = h
    # 1 -> 111km
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
    #cell_df['teryt_gmi'] = cell_df['centroid'].map(lambda x: find_gmi(x))
    
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
    cell_df = cell_df.sjoin(geo_gmi, how="left", predicate='intersects')
    
    fig = px.choropleth_mapbox(
    cell_df,
    geojson=cell_df.geometry, 
    locations=cell_df.index, 
    mapbox_style="carto-positron", 
    hover_data = {'lon':True, 'lat':True,'podpowiedz':True, 'gps_sz_gmi':True, 'gps_dl_gmi':True,'Nazwa':True, 'Miejscowość':True, "Województwo":True},
    zoom=6, 
    color='distance_2',
    color_continuous_scale="Magma",
    opacity=.6,
    height=1000,
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120}, hovermode="closest")

    return fig