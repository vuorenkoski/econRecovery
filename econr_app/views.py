from numpy.lib.arraysetops import unique
import pandas as pd
import numpy as np
import json

from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage

def get_countries():
    return np.sort(pd.read_csv(staticfiles_storage.path('countries.csv')).loc[:,'Country or Area'].to_numpy())

def get_data():
    df = pd.read_csv(staticfiles_storage.path('stat.csv')).rename(columns={'Country or Area':'Area'})
    df.Value = pd.to_numeric(df.Value, errors='coerce')
    return df

def to_maptable(df, indicator):
    datatable = "[['Country', 'Name', '" + indicator + "']"
    for i,r in df.dropna().iterrows():
        datatable+=",[\"" + r['Code2'] + "\",\"" + r['Area'] + "\"," + str(r['Value']) + "]"
    datatable+=']'
    return datatable

def index_view(request):
    df = get_data()
    data={'datapoints':df.shape[0], 'countries_nr':len(df.Area.unique())}
    return render(request, 'econr_app/index.html', data) 

def countries_view(request):
    df = get_data()
    if request.method == "POST":
        area = request.POST['area']
        areadata = df[df.Area == request.POST['area']]
        datatable = json.loads(areadata.to_json(orient ='records'))
        areadata=areadata[areadata.Item=='Real GDP growth (Annual percent change)']
        gdp_data = {'labels':areadata.Year.to_numpy().tolist(), 'datasets': [{'label':'Real GDP growth (Annual percent change)','backgroundColor':'rgba(0, 0, 128, 0.5)','data':areadata.Value.to_numpy().tolist()}]}
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
    if request.method == "POST":
        indicator = request.POST['indicator']
        year = int(request.POST['year'])
        indicator_data = df[(df.Item == indicator) & (df.Year == year)]
        datatable = to_maptable(indicator_data, indicator)
    else:
        indicator = None
        datatable = None
        year = None
    indicators=df.Item.unique()
    years = df.Year.unique()
    data={'indicators':indicators, 'indicator':indicator, 'datatable':datatable, 'year':year, 'years':years}
    return render(request, 'econr_app/world.html', data)

def predictions_view(request):
    return render(request, 'econr_app/predictions.html')

def about_view(request):
    return render(request, 'econr_app/about.html')

def average_view(request):
    df = get_data()
    if request.method == "POST":
        area = request.POST['area']
        df = df[df.Year==2019].sort_values(by=['Item'])
        items = df.Item.unique()

        areadata = df[df.Area == request.POST['area']]
        items = areadata.Item.unique()
        areadata = areadata.Value.to_numpy()

        avrgdata = df[df.Item.isin(items)].groupby("Item").mean().Value.to_numpy()
        areadata = areadata / avrgdata
        avrgdata =avrgdata / avrgdata
        gdp_data = {'labels':items.tolist(), 'datasets': [{'label':area,'borderColor':'blue','data':areadata.tolist()}, {'label':'Average','borderColor':'red','data':avrgdata.tolist()}]}
        gdp = json.dumps(gdp_data)
    else:
        gdp = None
        area = None

    countries = get_countries()
    data={'countries':countries, 'gdp':gdp, 'area':area}
    return render(request, 'econr_app/average.html', data)