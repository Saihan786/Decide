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
    content = models.CharField(blank=True)
