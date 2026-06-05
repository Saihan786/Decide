from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from decide.models import Writer, Session, Reviewer


def home(request):
    return render(request, "home.html")


def make_session(request):
    writer = Writer.objects.create(
        first_name=request.POST["first_name"],
        last_name=request.POST["last_name"],
    )
    session = Session.objects.create(writer=writer)
    return HttpResponse(session.join_code)


def join_session(request):
    session = get_object_or_404(Session, join_code=request.POST["join_code"])
    reviewer = Reviewer.objects.create(
        first_name=request.POST["first_name"],
        last_name=request.POST["last_name"],
        session=session,
    )
    return HttpResponse(f"Joined as {reviewer.first_name} {reviewer.last_name}")
