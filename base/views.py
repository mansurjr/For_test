from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now, localtime
from django.utils import timezone
from datetime import timedelta
from .models import Teacher, Group, Student, Attendance
import json
from django.http import JsonResponse

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        teacher = Teacher.objects.filter(username=username, password=password).first()

        if teacher:
            request.session["teacher_id"] = teacher.id

            current_time = localtime(now())
            midnight = current_time.replace(hour=23, minute=59, second=59)
            seconds_until_midnight = (midnight - current_time).seconds

            request.session.set_expiry(seconds_until_midnight)

            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def dashboard(request):
    teacher_id = request.session.get("teacher_id")
    if not teacher_id:
        return redirect("login")

    teacher = get_object_or_404(Teacher, id=teacher_id)
    groups = teacher.groups.all()

    return render(request, "dashboard.html", {"teacher": teacher, "groups": groups}, status=200)

def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group)

    attendances = Attendance.objects.filter(student__group=group).select_related('student')

    return render(request, 'group_details.html', {
        'group': group,
        'students': students,
        'attendances': attendances
    })

def update_attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            student_id = data.get("student_id")
            date = data.get("date")
            status = data.get("status")

            if not student_id or not date or not status:
                return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)
            
            return JsonResponse({"status": "success", "message": "Attendance updated"})
        
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)

