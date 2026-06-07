from django.test import TestCase
from django.db.utils import IntegrityError
from decide.models import Session, Writer, Reviewer, Document, Review


class WriterTests(TestCase):

    def test_writer_has_name(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Ali")
        self.assertEqual(writer.first_name, "Saudia")
        self.assertEqual(writer.last_name, "Ali")

    def test_writer_can_have_multiple_sessions(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Ali")
        Session.objects.create(writer=writer)
        Session.objects.create(writer=writer)
        self.assertEqual(writer.sessions.count(), 2)
        self.assertEqual(writer.last_name, "Ali")

    def test_writer_uniqueness(self):
        Writer.objects.create(first_name="Saudia", last_name="Ali")
        with self.assertRaises(IntegrityError):
            Writer.objects.create(first_name="Saudia", last_name="Ali")


class ReviewerTests(TestCase):

    def setUp(self):
        self.writer = Writer.objects.create(first_name="Saudia", last_name="Ali")
        self.session = Session.objects.create(writer=self.writer)

    def test_reviewer_has_name(self):
        reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)
        self.assertEqual(reviewer.first_name, "Yusuf")
        self.assertEqual(reviewer.last_name, "Ahmed")

    def test_duplicate_reviewer_name_in_same_session_is_rejected(self):
        Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)
        with self.assertRaises(IntegrityError):
            Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)

    def test_same_reviewer_name_allowed_in_different_sessions(self):
        other_session = Session.objects.create(writer=self.writer)
        Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)
        Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=other_session)
        self.assertEqual(Reviewer.objects.filter(first_name="Yusuf", last_name="Ahmed").count(), 2)

    def test_reviewer_can_be_removed(self):
        reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)
        reviewer.delete()
        self.assertFalse(Reviewer.objects.filter(pk=reviewer.pk).exists())


class SessionTests(TestCase):

    def setUp(self):
        self.writer = Writer.objects.create(first_name="Saudia", last_name="Ali")

    def test_session_generates_join_code_on_creation(self):
        session = Session.objects.create(writer=self.writer)
        self.assertIsNotNone(session.join_code)
        self.assertEqual(len(session.join_code), 6)
        self.assertTrue(session.join_code.isdigit())

    def test_session_join_codes_are_unique(self):
        session1 = Session.objects.create(writer=self.writer)
        session2 = Session.objects.create(writer=self.writer)
        self.assertNotEqual(session1.join_code, session2.join_code)

    def test_session_default_status_is_writing(self):
        session = Session.objects.create(writer=self.writer)
        self.assertEqual(session.status, "WRITING")

    def test_session_status_transitions(self):
        session = Session.objects.create(writer=self.writer)
        session.status = "REVIEW"
        session.save()
        self.assertEqual(Session.objects.get(pk=session.pk).status, "REVIEW")

    def test_deleting_writer_deletes_session(self):
        session = Session.objects.create(writer=self.writer)
        self.writer.delete()
        self.assertFalse(Session.objects.filter(pk=session.pk).exists())


class DocumentTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Ali")
        self.session = Session.objects.create(writer=writer)

    def test_document_is_linked_to_session(self):
        doc = Document.objects.create(session=self.session, content="Hello world")
        self.assertEqual(doc.session, self.session)

    def test_document_default_revision_is_1(self):
        doc = Document.objects.create(session=self.session, content="Hello world")
        self.assertEqual(doc.revision, 1)

    def test_document_stores_content(self):
        doc = Document.objects.create(session=self.session, content="<p>Draft text</p>")
        self.assertEqual(Document.objects.get(pk=doc.pk).content, "<p>Draft text</p>")

    def test_document_content_can_be_updated(self):
        doc = Document.objects.create(session=self.session, content="v1")
        doc.content = "v2"
        doc.save()
        self.assertEqual(Document.objects.get(pk=doc.pk).content, "v2")

    def test_document_content_can_be_blank(self):
        Document.objects.create(session=self.session)
        self.assertEqual(Document.objects.count(), 1)

    def test_deleting_session_deletes_document(self):
        Document.objects.create(session=self.session, content="Hello world")
        self.session.delete()
        self.assertFalse(Document.objects.exists())


class ReviewTests(TestCase):

    def setUp(self):
        writer = Writer.objects.create(first_name="Saudia", last_name="Ali")
        self.session = Session.objects.create(writer=writer)
        self.document = Document.objects.create(session=self.session)
        self.reviewer = Reviewer.objects.create(first_name="Yusuf", last_name="Ahmed", session=self.session)

    def test_review_is_linked_to_reviewer_and_document(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Well written.")
        self.assertEqual(review.reviewer, self.reviewer)
        self.assertEqual(review.document, self.document)

    def test_review_stores_approval_decision(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Clear and concise.")
        self.assertTrue(Review.objects.get(pk=review.pk).approved)

    def test_review_stores_reason(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=False, reason="Needs more detail.")
        self.assertEqual(Review.objects.get(pk=review.pk).reason, "Needs more detail.")

    def test_review_comments_can_be_blank(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Looks good.")
        self.assertEqual(review.comments, "")

    def test_review_stores_comments(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Looks good.", comments="Minor typo on line 2.")
        self.assertEqual(Review.objects.get(pk=review.pk).comments, "Minor typo on line 2.")

    def test_reviewer_can_only_review_document_once_per_revision(self):
        Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Good.")
        with self.assertRaises(IntegrityError):
            Review.objects.create(reviewer=self.reviewer, document=self.document, approved=False, reason="Actually not good.")

    def test_reviewer_can_review_same_document_on_new_revision(self):
        Review.objects.create(reviewer=self.reviewer, document=self.document, approved=False, reason="Needs work.")
        self.document.revision = 2
        self.document.save()
        Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Much better.")
        self.assertEqual(Review.objects.filter(reviewer=self.reviewer).count(), 2)

    def test_review_snapshots_document_revision_on_create(self):
        review = Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Good.")
        self.assertEqual(review.document_revision_snapshot, self.document.revision)

    def test_deleting_reviewer_deletes_review(self):
        Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Good.")
        self.reviewer.delete()
        self.assertFalse(Review.objects.exists())

    def test_deleting_document_deletes_review(self):
        Review.objects.create(reviewer=self.reviewer, document=self.document, approved=True, reason="Good.")
        self.document.delete()
        self.assertFalse(Review.objects.exists())
