from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from decide.models import Writer, Session, Reviewer, Document, Review


def home(request):
    return render(request, "home.html")


def join_session(request):
    session = get_object_or_404(Session, join_code=request.POST["join_code"])
    reviewer, _ = Reviewer.objects.get_or_create(
        first_name=request.POST["first_name"],
        last_name=request.POST["last_name"],
        session=session,
    )

    if session.status == Session.Status.REVIEW:
        already_reviewed = reviewer.review.filter(
            document=session.document,
            document_revision_snapshot=session.document.revision,
        ).exists()
        if already_reviewed:
            return render(
                request, "home.html", {"message": f"{reviewer.first_name}, your review has already been submitted."}
            )
        return render(
            request,
            "document_under_review.html",
            {
                "session": session,
                "reviewer": reviewer,
                "document": session.document,
            },
        )
    elif session.status == Session.Status.WRITING:
        return render(
            request,
            "waiting_room.html",
            {
                "reviewers": session.reviewers.all(),
                "current_reviewer": reviewer,
            },
        )
    else:
        return render(
            request, "home.html", {"message": f"{reviewer.first_name}, the document can no longer be reviewed."}
        )


def submit_review(request):
    reviewer = get_object_or_404(Reviewer, pk=request.POST["reviewer_id"])
    document = get_object_or_404(Document, pk=request.POST["document_id"])
    approved = request.POST["approved"] == "true"
    reason = request.POST["reason"]
    comments = request.POST.get("comments", "")

    Review.objects.create(reviewer=reviewer, document=document, approved=approved, reason=reason, comments=comments)

    return render(request, "home.html")


def write_document(request):
    first_name = request.POST.get("first_name", "")
    last_name = request.POST.get("last_name", "")
    join_code = request.POST.get("join_code", "")

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

    if request.POST.get("new_revision") == "true":
        session.status = Session.Status.WRITING
        session.save()

        document.revision += 1
        document.save()

    context = {
        "writer": session.writer,
        "session": session,
        "revision": document.revision,
        "document": document.content,
    }

    if session.status == Session.Status.REVIEW:
        return render(
            request,
            "document_under_review_waiting_room.html",
            {"session": session, "reviewed_ids": get_reviewed_ids(session)},
        )
    elif session.status == Session.Status.WRITING:
        return render(request, "document_editing.html", context)
    else:
        reviews, approved_count, disapproved_count = get_session_results(session)
        return render(
            request,
            "results.html",
            {
                "session": session,
                "reviews": reviews,
                "approved_count": approved_count,
                "disapproved_count": disapproved_count,
            },
        )


def save_document(request):
    session = get_object_or_404(Session, join_code=request.POST["join_code"])
    document = get_object_or_404(Document, session=session)
    document.content = request.POST["content"]
    document.save()
    return HttpResponse(status=200)


def submit_document(request):
    session = get_object_or_404(Session, join_code=request.POST["join_code"])
    session.status = Session.Status.REVIEW
    session.save()
    return render(
        request,
        "document_under_review_waiting_room.html",
        {"session": session, "reviewed_ids": get_reviewed_ids(session)},
    )


def results(request):
    session = get_object_or_404(Session, join_code=request.POST["join_code"])
    reviews, approved_count, disapproved_count = get_session_results(session)
    return render(
        request,
        "results.html",
        {
            "session": session,
            "reviews": reviews,
            "approved_count": approved_count,
            "disapproved_count": disapproved_count,
        },
    )


def mark_complete(request):
    return HttpResponse()


def get_reviewed_ids(session):
    return session.document.reviews.filter(document_revision_snapshot=session.document.revision).values_list(
        "reviewer_id", flat=True
    )


def get_session_results(session):
    reviews = session.document.reviews.select_related("reviewer").order_by("-document_revision_snapshot")
    approved_count = reviews.filter(approved=True).count()
    disapproved_count = reviews.filter(approved=False).count()
    return reviews, approved_count, disapproved_count
