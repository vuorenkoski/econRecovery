import pandas as pd
import numpy as np
import json

from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage

def index_view(request):
    df = pd.read_csv(staticfiles_storage.path('stat.csv')).rename(columns={'Country or Area':'Area'})
    if request.method == "POST":
        area = request.POST['area']
        areadata = df[df.Area == request.POST['area']]
        datatable = json.loads(areadata.to_json(orient ='records'))
        areadata=areadata[areadata.Item=='Real GDP growth (Annual percent change)']
        gdp_data = {'labels':areadata.Year.to_numpy().tolist(), 'datasets': [{'label':'Real GDP growth (Annual percent change)','data':areadata.Value.to_numpy().tolist()}]}
        gdp = json.dumps(gdp_data)
    else:
        datatable = None
        gdp = None
        area = None

    datapoints = df.shape[0]
    countries = df.Area.unique()
    data={'datapoints':datapoints, 'countries_nr':len(countries), 'countries':np.sort(countries), 'datatable':datatable, 'gdp':gdp, 'area':area}
    return render(request, 'econr_app/index.html', data) 
