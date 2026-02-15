from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    LEVEL_CHOICES = (
        ("ND I", "ND I"),
        ("ND II", "ND II"),
        ("ND III", "ND III"),
        ("HND I", "HND I"),
        ("HND II", "HND II"),
        ("HND III", "HND III"),
    )
    SEX_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    matric = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=True, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.matric = self.matric.upper().strip()
        self.first_name = self.first_name.title().strip()
        self.last_name = self.last_name.title().strip()
        if self.middle_name:
            self.middle_name = self.middle_name.title().strip()
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matric})"
