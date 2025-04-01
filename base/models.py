from django.db import models
import random
from django.contrib.auth.models import AbstractUser


class Staffs(AbstractUser):
    POSITION_CHOICES = [
        ("Administrator", "Administrator"),
        ("Teacher", "Teacher"),
        ("CEO", "CEO"),
    ]

    phone_number = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=15, choices=POSITION_CHOICES)

    def __str__(self):
        return f"{self.username} - {self.position}"


class Group(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    lesson_start_time = models.TimeField()
    teacher = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name="teacher_groups")

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=6, unique=True, editable=False, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="students")

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_id(cls):
        while True:
            unique_id = str(random.randint(100000, 999999))
            if not cls.objects.filter(unique_id=unique_id).exists():
                return unique_id

    def __str__(self):
        return f"{self.name} {self.surname} ({self.unique_id})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Absent")

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} {self.student.surname} - {self.date}: {self.status}"
