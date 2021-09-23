from django.shortcuts import render

def index_view(request):
    return render(request, 'econr_app/index.html') 
