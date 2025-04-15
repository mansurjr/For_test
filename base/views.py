from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Staffs, Group, Student, Attendance
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

@api_view(["POST"])
def login_view(request):
    data = request.data
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    logger.debug(f"Login attempt for username: {username}")

    try:
        user = Staffs.objects.get(username=username)
        logger.debug(f"User found: {user.username}")

        if not user.is_active:
            return Response({"status": "error", "message": "Your account is inactive. Please contact support."},
                            status=status.HTTP_403_FORBIDDEN)

        if check_password(password, user.password):
            user.last_login = datetime.now()
            user.save(update_fields=["last_login"])

            refresh = RefreshToken.for_user(user)
            role = user.position

            if role == 'CEO':
                teacher_ids = Staffs.objects.filter(position="Teacher").values_list('id', flat=True)
                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "teacher_ids": list(teacher_ids),
                    "role": role
                })
            elif role == 'Teacher':
                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "teacher_id": user.id,
                    "role": role
                })
            else:
                return Response({"status": "error", "message": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error("Invalid password")
            return Response({"status": "error", "message": "Invalid username or password"},
                            status=status.HTTP_401_UNAUTHORIZED)

    except Staffs.DoesNotExist:
        logger.error(f"User not found for username: {username}")
        return Response({"status": "error", "message": "Invalid username or password"},
                        status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response({"status": "error", "message": "Unexpected error occurred"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({"status": "success", "message": "Logged out successfully"})

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = get_object_or_404(Staffs, id=request.user.id)

    if user.position == "Teacher":
        groups = [{"id": group.id, "name": group.name} for group in Group.objects.filter(teacher=user)]

        return Response({
            "status": "success",
            "teacher": {"id": user.id, "name": user.username, "last_login": user.last_login},
            "groups": groups
        })
    elif user.position == "CEO":
        teachers = Staffs.objects.filter(position="Teacher").values("id", "username", "last_login")
        return Response({
            "status": "success",
            "teachers": list(teachers)
        })
    else:
        return Response({"status": "error", "message": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    students = [
    {"id": student.id, "full_name": f"{student.name} {student.surname}", "unique_id": student.unique_id}
    for student in group.students.all()
]

    attendances = [
        {"id": attendance.id, "student_id": attendance.student.id, "date": str(attendance.date), "status": attendance.status}
        for attendance in Attendance.objects.filter(student__group=group).select_related('student')
    ]

    return Response({
        "status": "success",
        "group": {"id": group.id, "name": group.name},
        "students": students,
        "attendances": attendances
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = get_object_or_404(Staffs, id=request.user.id)

    return Response({
        "status": "success",
        "user": {
            "id": user.id,
            "full_name": user.first_name + " " + user.last_name,
            "last_login": user.last_login,
            "role": user.position,
            "email": user.email,
            "image": user.profile_picture.url if user.profile_picture else None
        }
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_attendance(request):

    data = request.data
    student_id = data.get("student_id")
    date = data.get("date")
    status_value = data.get("status")

    if not student_id or not date or not status_value:
        return Response({"status": "error", "message": "Invalid data"},
                        status=status.HTTP_400_BAD_REQUEST)

    student = get_object_or_404(Student, id=student_id)

    attendance, created = Attendance.objects.update_or_create(
        student=student, date=date,
        defaults={"status": status_value}
    )

    message = "Attendance updated" if not created else "Attendance recorded"

    return Response({"status": "success", "message": message, "attendance_id": attendance.id})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    user = request.user

    if 'profile_picture' in request.FILES:
        user.profile_picture = request.FILES['profile_picture']
        user.save()

        return Response({"status": "success", "message": "Profile picture uploaded successfully"})

    return Response({"status": "error", "message": "No file uploaded"}, status=400)