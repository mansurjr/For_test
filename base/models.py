from django.db import models
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class TeacherManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

class Teacher(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)

    objects = TeacherManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.full_name

class Group(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    lesson_starts = models.TimeField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_groups")

    def __str__(self):
        return f"{self.name}"

class Student(models.Model):
    full_name = models.CharField(max_length=255)
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