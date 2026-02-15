from django.db import models
from voters.models import Student

class Election(models.Model):
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "Active" if self.is_active else "Inactive"

class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    matric = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    manifesto = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    photo = models.ImageField(upload_to="candidates")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'position')
