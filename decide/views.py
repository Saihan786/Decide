from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def make_session(request):
    """Makes model instances and generates join code."""

    return HttpResponse()


def join_session(request):
    """Displays form to join existing session."""

    return HttpResponse()
