import pandas as pd
from sklearn.neighbors import KDTree

#locations_school = pd.read_csv("data/school.csv", usecols=['rspo', 'lat', 'lon', 'Kategoria_szkoły'])
#locations_gmi = pd.read_csv('data/gmi_centroid.csv')
#locations_school = locations_school[~locations_school['lon'].isnull()]

def distance_gmi(locations_school, locations_gmi, Kategoria_szkoły = [], k = 1):
    #locations_school = pd.read_csv("data/school.csv", usecols=['rspo', 'lat', 'lon', 'Kategoria_szkoły'])
    #locations_gmi = pd.read_csv('data/gmi_centroid.csv')
    #locations_school = locations_school[~locations_school['lon'].isnull()]
    #locations_school = locations_school[locations_school['Kategoria_szkoły'].isin(Kategoria_szkoły)]

    kd = KDTree(locations_gmi[["gps_sz_gmi", "gps_dl_gmi"]].values, metric='euclidean')

    distances, indices = kd.query(locations_school[["lon", "lat"]].values, k = k)

    # #dataframe distanse
    # dist = pd.DataFrame(distances)
    # gmi_dict = locations_gmi[['teryt']].to_dict()
    # teryt_dict = gmi_dict['teryt']

    # #dataframe teryt for gminy
    # gmi = pd.DataFrame(indices)
    # gmi.columns = ['teryt_gmi']

    # distance_min = (
    # pd.concat([dist, gmi], axis=1)
    # .groupby('teryt_gmi')
    # .agg('min')
    # .reset_index()
    # )
    # distance_min.columns = ['teryt_gmi', 'distance']

    #dataframe distanse
    dist = pd.DataFrame(distances)
    gmi_dict = locations_gmi[['teryt']].to_dict()
    teryt_dict = gmi_dict['teryt']

    gmi = pd.DataFrame(indices)
    gmi.columns = ['teryt']

    gmi.teryt = gmi.teryt.map(teryt_dict)

    distance_min = (
    pd.concat([dist, gmi], axis=1)
    .groupby('teryt')
    .agg('min')
    .reset_index()
    )

    distance_min.columns = ['teryt', 'distance']
    
    return distance_min