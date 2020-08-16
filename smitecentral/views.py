from django.views import View
from django.shortcuts import render

def handle_404(request, exception):
    context = {
        "status_code": "404",
        "message": "You Took A Wrong Turn On Your Way To Vahalla."
    }
    return render(request, "errors.html", context, status=404)

def handle_500(request):
    context = {
        "status_code": "500",
        "message": "The Gods Did An Ooof"
    }
    return render(request, "errors.html", context, status=500)

def handle_403(request, exception):
    context = {
        "status_code": "403",
        "message": "You Were Not Ordained Access."
    }
    return render(request, "errors.html", context, status=403)

def handle_400(request, exception):
    context = {
        "status_code": "400",
        "message": "The Gods Can't Meet Your Request."
    }
    return render(request, "errors.html", context, status=400)
