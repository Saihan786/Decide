from django.test import TestCase
from decide.models import Session, Writer, Reviewer, Document


class JoinSessionViewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Begum")
        self.session = Session.objects.create(writer=writer)

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
        response = self.client.post("/document/save/", {"join_code": self.session.join_code, "content": "updated content"})
        self.assertEqual(response.status_code, 200)
