import random
from django.db import models


def generate_join_code() -> str:
    # Generates a random 6-digit string, preserving leading zeros (e.g., '004321')
    return f"{random.randint(0, 999999):06d}"


class Writer(models.Model):
    name = models.CharField(max_length=100)


class Session(models.Model):
    STATUS_CHOICES = [
        ("WRITING", "Writing"),
        ("REVIEW", "Review"),
        ("RESULT", "Result"),
    ]

    writer = models.ForeignKey(Writer, on_delete=models.CASCADE, related_name="sessions")
    join_code = models.CharField(unique=True, editable=False, max_length=6, default=generate_join_code)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="WRITING",
    )


class Reviewer(models.Model):
    name = models.CharField(max_length=100)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="reviewers")

    class Meta:
        unique_together = ("name", "session")
