from django.test import TestCase
from decide.models import Session, Writer, Reviewer, Document, Review


class JoinSessionViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer)
        Document.objects.create(session=self.session, content="original content")

    def test_join_session_creates_reviewer(self):
        self.client.post("/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"})
        self.assertEqual(Reviewer.objects.count(), 1)

    def test_join_session_links_reviewer_to_correct_session(self):
        self.client.post("/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"})
        reviewer = Reviewer.objects.first()
        self.assertEqual(reviewer.session, self.session)

    def test_join_session_invalid_code_does_not_create_reviewer(self):
        self.client.post("/join/", {"join_code": "000000", "first_name": "Yusuf", "last_name": "Khan"})
        self.assertEqual(Reviewer.objects.count(), 0)

    def test_join_session_returns_200(self):
        response = self.client.post(
            "/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"}
        )
        self.assertEqual(response.status_code, 200)

    def test_join_session_already_reviewed_current_revision_shows_message(self):
        self.session.status = Session.Status.REVIEW
        self.session.save()
        reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Khan", session=self.session)
        document = Document.objects.get(session=self.session)
        Review.objects.create(reviewer=reviewer, document=document, approved=True, reason="Good.")
        response = self.client.post("/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"})
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "already been submitted")

    def test_join_session_new_revision_allows_review_again(self):
        self.session.status = Session.Status.REVIEW
        self.session.save()
        reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Khan", session=self.session)
        document = Document.objects.get(session=self.session)
        Review.objects.create(reviewer=reviewer, document=document, approved=True, reason="Good.")
        document.revision = 2
        document.save()
        response = self.client.post("/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"})
        self.assertTemplateUsed(response, "document_under_review.html")

    def test_join_session_result_status_shows_message(self):
        self.session.status = Session.Status.RESULT
        self.session.save()
        response = self.client.post("/join/", {"join_code": self.session.join_code, "first_name": "Yusuf", "last_name": "Khan"})
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "can no longer be reviewed")


class WriteDocumentViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer)

    def test_no_join_code_creates_new_session_and_document(self):
        self.client.post("/document/", {"first_name": "Saudia", "last_name": "Begum"})
        self.assertEqual(Session.objects.count(), 2)
        self.assertEqual(Document.objects.count(), 1)

    def test_no_join_code_links_document_to_new_session(self):
        self.client.post("/document/", {"first_name": "Saudia", "last_name": "Begum"})
        new_session = Session.objects.latest("pk")
        self.assertEqual(Document.objects.first().session, new_session)

    def test_valid_join_code_does_not_create_new_session_or_document(self):
        Document.objects.create(session=self.session, content="existing content")
        self.client.post(
            "/document/", {"first_name": "Saudia", "last_name": "Begum", "join_code": self.session.join_code}
        )
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(Document.objects.count(), 1)

    def test_invalid_join_code_returns_404(self):
        response = self.client.post("/document/", {"first_name": "Saudia", "last_name": "Begum", "join_code": "000000"})
        self.assertEqual(response.status_code, 404)

    def test_new_revision_increments_revision(self):
        Document.objects.create(session=self.session, content="content")
        self.session.status = Session.Status.REVIEW
        self.session.save()
        self.client.post("/document/", {"join_code": self.session.join_code, "new_revision": "true"})
        self.assertEqual(Document.objects.get(session=self.session).revision, 2)

    def test_new_revision_resets_session_to_writing(self):
        Document.objects.create(session=self.session, content="content")
        self.session.status = Session.Status.REVIEW
        self.session.save()
        self.client.post("/document/", {"join_code": self.session.join_code, "new_revision": "true"})
        self.assertEqual(Session.objects.get(pk=self.session.pk).status, Session.Status.WRITING)


class SaveDocumentViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer)
        self.document = Document.objects.create(session=self.session, content="original content")

    def test_save_updates_document_content(self):
        self.client.post("/document/save/", {"join_code": self.session.join_code, "content": "updated content"})
        self.assertEqual(Document.objects.get(pk=self.document.pk).content, "updated content")

    def test_save_does_not_create_new_document(self):
        self.client.post("/document/save/", {"join_code": self.session.join_code, "content": "updated content"})
        self.assertEqual(Document.objects.count(), 1)

    def test_save_invalid_join_code_returns_404(self):
        response = self.client.post("/document/save/", {"join_code": "000000", "content": "updated content"})
        self.assertEqual(response.status_code, 404)

    def test_save_returns_200(self):
        response = self.client.post(
            "/document/save/", {"join_code": self.session.join_code, "content": "updated content"}
        )
        self.assertEqual(response.status_code, 200)


class SubmitDocumentViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer)
        self.document = Document.objects.create(session=self.session, content="original content")

    def test_submit_sets_document_submitted(self):
        self.client.post("/document/submit/", {"join_code": self.session.join_code})
        self.assertTrue(self.session.status, Session.Status.REVIEW)

    def test_submit_invalid_join_code_returns_404(self):
        response = self.client.post("/document/submit/", {"join_code": "000000"})
        self.assertEqual(response.status_code, 404)

    def test_submit_returns_200(self):
        response = self.client.post("/document/submit/", {"join_code": self.session.join_code})
        self.assertEqual(response.status_code, 200)


class SubmitReviewViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer, status=Session.Status.REVIEW)
        self.document = Document.objects.create(session=self.session, content="some content")
        self.reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Khan", session=self.session)

    def test_submit_review_creates_review(self):
        self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": self.reviewer.pk,
                "document_id": self.document.pk,
                "approved": "true",
                "reason": "Well written.",
                "comments": "",
            },
        )
        self.assertEqual(Review.objects.count(), 1)

    def test_submit_review_links_to_reviewer_and_document(self):
        self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": self.reviewer.pk,
                "document_id": self.document.pk,
                "approved": "true",
                "reason": "Well written.",
                "comments": "",
            },
        )
        review = Review.objects.first()
        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.document, self.document)

    def test_submit_review_stores_approval_and_reason(self):
        self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": self.reviewer.pk,
                "document_id": self.document.pk,
                "approved": "true",
                "reason": "Well written.",
            },
        )
        review = Review.objects.first()
        self.assertTrue(review.approved)
        self.assertEqual(review.reason, "Well written.")

    def test_submit_review_stores_comments(self):
        self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": self.reviewer.pk,
                "document_id": self.document.pk,
                "approved": "false",
                "reason": "Needs work.",
                "comments": "Check paragraph 2.",
            },
        )
        self.assertEqual(Review.objects.first().comments, "Check paragraph 2.")

    def test_submit_review_invalid_reviewer_returns_404(self):
        response = self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": 9999,
                "document_id": self.document.pk,
                "approved": "true",
                "reason": "Good.",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_submit_review_returns_200(self):
        response = self.client.post(
            "/join/submit-review/",
            {
                "reviewer_id": self.reviewer.pk,
                "document_id": self.document.pk,
                "approved": "true",
                "reason": "Good.",
            },
        )
        self.assertEqual(response.status_code, 200)


class ResultsViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer, status=Session.Status.RESULT)
        self.document = Document.objects.create(session=self.session, content="some content")
        reviewer1 = Reviewer.objects.create(first_name="Yusuf", last_name="Khan", session=self.session)
        reviewer2 = Reviewer.objects.create(first_name="Aisha", last_name="Ali", session=self.session)
        Review.objects.create(reviewer=reviewer1, document=self.document, approved=True, reason="Good.")
        Review.objects.create(reviewer=reviewer2, document=self.document, approved=False, reason="Needs work.")

    def test_results_returns_200(self):
        response = self.client.post("/document/result/", {"join_code": self.session.join_code})
        self.assertEqual(response.status_code, 200)

    def test_results_uses_correct_template(self):
        response = self.client.post("/document/result/", {"join_code": self.session.join_code})
        self.assertTemplateUsed(response, "results.html")

    def test_results_returns_correct_counts(self):
        response = self.client.post("/document/result/", {"join_code": self.session.join_code})
        self.assertEqual(response.context["approved_count"], 1)
        self.assertEqual(response.context["disapproved_count"], 1)

    def test_results_invalid_join_code_returns_404(self):
        response = self.client.post("/document/result/", {"join_code": "000000"})
        self.assertEqual(response.status_code, 404)
