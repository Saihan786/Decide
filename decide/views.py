from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world! Index page for 'Decide'")
