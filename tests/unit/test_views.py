from django.test import TestCase
from decide.models import Session, Writer, Reviewer


class MakeSessionViewTests(TestCase):

    def test_make_session_creates_writer_and_session(self):
        self.client.post("/new/", {"first_name": "Saudia", "last_name": "Begum"})
        self.assertEqual(Writer.objects.count(), 1)
        self.assertEqual(Session.objects.count(), 1)

    def test_make_session_links_writer_to_session(self):
        self.client.post("/new/", {"first_name": "Saudia", "last_name": "Begum"})
        session = Session.objects.first()
        self.assertIsNotNone(session.writer)

    def test_make_session_returns_join_code_in_response(self):
        response = self.client.post("/new/", {"first_name": "Saudia", "last_name": "Begum"})
        session = Session.objects.first()
        self.assertContains(response, session.join_code)


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
