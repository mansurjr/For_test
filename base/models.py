from django.db import models
import random

class Teacher(models.Model):
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name

class Group(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    lesson_starts = models.TimeField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return f"{self.name}"

class Student(models.Model):
    full_name = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=6, unique=True, editable=False, null=True, blank=True) 
    group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="students")

    def save(self, *args, **kwargs):
        """Ensure unique_id is set before saving"""
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_id(cls):
        """Generate a unique 6-digit ID with fewer database queries"""
        existing_ids = set(Student.objects.values_list('unique_id', flat=True))
        
        while True:
            unique_id = str(random.randint(100000, 999999))
            if unique_id not in existing_ids:
                return unique_id

    def __str__(self):
        return f"{self.full_name} ({self.unique_id})"
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True, default=None)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.full_name} - {self.date}: {self.status}"
