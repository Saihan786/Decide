import random
from django.db import models


def generate_join_code() -> str:
    # Generates a random 6-digit string, preserving leading zeros (e.g., '004321')
    return f"{random.randint(0, 999999):06d}"


class Writer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["first_name", "last_name"], name="unique_writer"),
        ]


class Session(models.Model):
    class Status(models.TextChoices):
        WRITING = "WRITING", "Writing"
        REVIEW = "REVIEW", "Review"
        RESULT = "RESULT", "Result"
        COMPLETE = "COMPLETE", "Complete"

    writer = models.ForeignKey(Writer, on_delete=models.CASCADE, related_name="sessions")
    join_code = models.CharField(unique=True, editable=False, max_length=6, default=generate_join_code)
    status = models.CharField(
        choices=Status.choices,
        default="WRITING",
    )


class Reviewer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="reviewers")

    class Meta:
        unique_together = ("first_name", "last_name", "session")


class Document(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="document")
    revision = models.IntegerField(default=1)
    content = models.TextField(blank=True)


class Review(models.Model):
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE, related_name="review")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="reviews")
    approved = models.BooleanField()
    reason = models.TextField()
    comments = models.TextField(blank=True)
    document_revision_snapshot = models.IntegerField(editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "document", "document_revision_snapshot"], name="review_per_revision"
            )
        ]

    def save(self, *args, **kwargs):
        # Automatically grab the revision from the connected document before saving

        if not self.pk:  # Only do this when the review is created the first time
            self.document_revision_snapshot = self.document.revision

        super().save(*args, **kwargs)
