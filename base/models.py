from django.db import models

class Teacher(models.Model):
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name

class Group(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return f"{self.name}"

class Student(models.Model):
    full_name = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=50, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return self.full_name

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
