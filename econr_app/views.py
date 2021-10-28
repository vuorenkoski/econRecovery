from numpy.lib.arraysetops import unique
import pandas as pd
import numpy as np
import json

from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage

def get_countries():
    return np.sort(pd.read_csv(staticfiles_storage.path('countries.csv')).loc[:,'Name'].to_numpy())

def get_features(groups='features'):
    df = pd.read_csv(staticfiles_storage.path('features.csv'))
    if groups=='all':
        return df
    if groups=='combined':
        return df[df.feature_id>100] 
    return df[df.feature_id<100]

def get_feature_name(id):
    if id is None:
        return None
    df = get_features(groups='all')
    return df[df.feature_id==id].name.iloc[0]

def get_feature_description(id):
    if id is None:
        return None
    df = get_features(groups='all')
    return df[df.feature_id==id].short_description.iloc[0]

def get_data():
    df = pd.read_csv(staticfiles_storage.path('data.csv'))
    countries = pd.read_csv(staticfiles_storage.path('countries.csv'))[['country_code','Code2','Name']]
    df = pd.merge(df, countries, on=['country_code'], how='left')

    df.value = pd.to_numeric(df.value, errors='coerce')
    return df

def get_cluster_data():
    df = pd.read_csv(staticfiles_storage.path('clusters.csv'))
    countries = pd.read_csv(staticfiles_storage.path('countries.csv'))[['country_code','Code2','Name']]
    df = pd.merge(df, countries, on=['country_code'], how='left')
    return df

def to_maptable(df, indicator):
    if df.empty:
        return None
    datatable = "[['Country', 'Name', '" + indicator + "']"
    for i,r in df.iterrows():
        datatable+=",[\"" + r['Code2'] + "\",\"" + r['Name'] + "\"," + str(r['value']) + "]"
    datatable+=']'
    return datatable

def index_view(request):
    df = get_data()
    data={'datapoints':df.shape[0], 'countries_nr':len(df.country_code.unique())}
    return render(request, 'econr_app/index.html', data) 

def countries_view(request):
    df = get_data()
    if request.method == "POST":
        area = request.POST['area']
        areadata = df[df.Name == request.POST['area']]
        datatable = pd.merge(areadata, get_features()[['feature_id','name']], on=['feature_id'], how='left')
        datatable = json.loads(datatable.to_json(orient ='records'))
        areadata=areadata[areadata.feature_id==4] # 4='Real GDP growth (Annual percent change)'
        gdp_data = {'labels':areadata.year.to_numpy().tolist(), 'datasets': [{'label':'Real GDP growth (Annual percent change)','backgroundColor':'rgba(0, 0, 128, 0.5)','data':areadata.value.to_numpy().tolist()}]}
        gdp = json.dumps(gdp_data)
    else:
        datatable = None
        gdp = None
        area = None

    countries = get_countries()
    data={'countries':countries, 'datatable':datatable, 'gdp':gdp, 'area':area}
    return render(request, 'econr_app/countries.html', data) 

def world_view(request):
    df = get_data()
    if request.method == 'POST':
        indicator = int(request.POST['indicator'])
        year = int(request.POST['year'])
        indicator_data = df[(df.feature_id == indicator) & (df.year == year)]
        datatable = to_maptable(indicator_data, get_feature_name(indicator))
    else:
        indicator = None
        datatable = None
        year = None

    years = df.year.unique()
    data={'indicators':get_features()[['feature_id','name']].values.tolist(), 'indicator':indicator, 'indicator_name':get_feature_name(indicator), 'indicator_description':get_feature_description(indicator), 'datatable':datatable, 'year':year, 'years':years}
    return render(request, 'econr_app/world.html', data)

def clustering_view(request):
    if request.method == 'POST':
        df = get_cluster_data()
        indicator = int(request.POST['indicator'])
        df['value']=df[str(indicator)]
        indicator_data=df[['value','Code2','Name']]    
        datatable = to_maptable(indicator_data, 'Cluster')
    else:
        indicator = None
        datatable = None

    indicators = get_features(groups='all')[['feature_id','name']].values.tolist()
    data={'indicators':indicators, 'indicator':indicator, 'datatable':datatable, 'indicator_name':get_feature_name(indicator), 'indicator_description':get_feature_description(indicator)}
    return render(request, 'econr_app/clustering.html', data)

def about_view(request):
    data ={'features':json.loads(get_features(groups='features').to_json(orient ='records')), 'combinations':json.loads(get_features(groups='combined').to_json(orient ='records'))}
    return render(request, 'econr_app/about.html', data)

def average_view(request):
    df = get_data()
    if request.method == 'POST':
        area = request.POST['area']
        df = df[df.year==2019].sort_values(by=['feature_id'])
        items = df.feature_id.unique()

        areadata = df[df.Name == request.POST['area']]
        areadata = pd.merge(areadata, get_features()[['feature_id','name']], on=['feature_id'], how='left')
        feature_names = areadata.name.unique()
        areadata = areadata.value.to_numpy()

        avrgdata = df[df.feature_id.isin(items)].groupby('feature_id').mean().value.to_numpy()
        areadata = areadata / avrgdata
        avrgdata =avrgdata / avrgdata
        gdp_data = {'labels':feature_names.tolist(), 'datasets': [{'label':area,'borderColor':'blue','data':areadata.tolist()}, {'label':'Average','borderColor':'red','data':avrgdata.tolist()}]}
        gdp = json.dumps(gdp_data)
    else:
        gdp = None
        area = None

    countries = get_countries()
    data={'countries':countries, 'gdp':gdp, 'area':area}
    return render(request, 'econr_app/average.html', data)