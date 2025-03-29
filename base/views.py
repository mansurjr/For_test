from django.shortcuts import get_object_or_404
from django.utils.timezone import now, localtime
from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Teacher, Group, Student, Attendance
from datetime import datetime

@api_view(["POST"])
def login_view(request):
    data = request.data
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    try:
        teacher = Teacher.objects.get(username=username)

        if not teacher.is_active:
            return Response(
                {"status": "error", "message": "Your account is inactive. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        if teacher.check_password(password):
            teacher.last_login = datetime.now()
            teacher.save(update_fields=["last_login"])

            refresh = RefreshToken.for_user(teacher)
            login(request, teacher)

            return Response({
                "status": "success",
                "message": "Login successful",
                "teacher_id": teacher.id,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })

    except Teacher.DoesNotExist:
        return Response({"status": "error", "message": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"status": "success", "message": "Logged out successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    teacher = request.user
    groups = [{"id": group.id, "name": group.name} for group in teacher.teacher_groups.all()]

    return Response({
        "status": "success", 
        "teacher": {"id": teacher.id, "name": teacher.full_name, "last_login": teacher.last_login}, 
        "groups": groups
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    students = [
        {"id": student.id, "full_name": student.full_name, "unique_id": student.unique_id}
        for student in group.students.all()
    ]

    attendances = [
        {"id": attendance.id, "student_id": attendance.student.id, "date": attendance.date, "status": attendance.status}
        for attendance in Attendance.objects.filter(student__group=group).select_related('student')
    ]

    return Response({
        "status": "success", 
        "group": {"id": group.id, "name": group.name}, 
        "students": students, 
        "attendances": attendances
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_attendance(request):
    data = request.data 
    student_id = data.get("student_id")
    date = data.get("date")
    status_value = data.get("status")

    if not student_id or not date or not status_value:
        return Response({"status": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    student = get_object_or_404(Student, id=student_id)

    attendance, created = Attendance.objects.update_or_create(
        student=student, date=date,
        defaults={"status": status_value}
    )

    message = "Attendance updated" if not created else "Attendance recorded"

    return Response({"status": "success", "message": message, "attendance_id": attendance.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    teacher = request.user

    return Response({
        "status": "success",
        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "username": teacher.username,
            "last_login": teacher.last_login,
        }
    })