from django.shortcuts import render

def static_view(request):
    return render(request, "home.html")
