from django.shortcuts import render

def static_view(request, template):
    return render(request, template)
