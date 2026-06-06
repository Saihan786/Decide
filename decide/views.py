from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from decide.models import Writer, Session, Reviewer, Document


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
    return render(
        request,
        "waiting_room.html",
        {
            "reviewers": session.reviewers.all(),
            "current_reviewer": reviewer,
        },
    )


def write_document(request):
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    join_code = request.POST.get("join_code")

    if join_code:
        session = get_object_or_404(Session, join_code=join_code)
        document = get_object_or_404(Document, session=session)
    else:
        writer, _ = Writer.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
        )
        session = Session.objects.create(writer=writer)
        document = Document.objects.create(session=session)

    context = {
        "writer": session.writer,
        "revision": document.revision,
        "document": document.content,
    }

    return HttpResponse()

    # return render(request, "write_document.html", context)
