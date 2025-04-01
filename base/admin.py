from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from .models import Staffs, Group, Student, Attendance
from .utils import generate_attendance_for_group
from django import forms
from dateutil.relativedelta import relativedelta

class TeacherResource(resources.ModelResource):
    class Meta:
        model = Staffs

class GroupResource(resources.ModelResource):
    class Meta:
        model = Group

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance

@admin.register(Staffs)
class TeacherAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ("username", "phone_number", "position", "is_active", "last_login")
    list_filter = ("is_active", "position")
    search_fields = ("username", "phone_number")
    readonly_fields = ("last_login",)

@admin.register(Student)
class StudentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ("name", "surname", "unique_id", "group")
    search_fields = ("name", "surname", "unique_id")

@admin.register(Attendance)
class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ("student", "date", "status")
    list_editable = ("status",)
    search_fields = ("student__name", "student__surname", "student__group__name")

class GroupForm(forms.ModelForm):
    DURATION_CHOICES = [
        (1, "1 Month"),
        (3, "3 Months"),
        (6, "6 Months"),
        (8, "8 Months"),
    ]

    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=True, label="Duration (Months)")

    class Meta:
        model = Group
        fields = ("name", "start_date", "lesson_start_time", "teacher")

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        duration = cleaned_data.get("duration")

        if start_date and duration:
            try:
                duration = int(duration)
                cleaned_data["end_date"] = start_date + relativedelta(months=duration)
            except ValueError:
                raise forms.ValidationError("Invalid duration format.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        duration = int(self.cleaned_data["duration"])
        instance.end_date = instance.start_date + relativedelta(months=duration)

        if commit:
            instance.save()
        return instance

@admin.register(Group)
class GroupAdmin(ExportMixin, admin.ModelAdmin):
    form = GroupForm  
    list_display = ("name", "start_date", "end_date", "lesson_start_time", "teacher")
    actions = ["generate_attendance"]
    list_editable = ("teacher",)
    search_fields = ("name", "teacher__username")

    def generate_attendance(self, request, queryset):
        for group in queryset:
            generate_attendance_for_group(group.id)
        self.message_user(request, "Attendance records created successfully!")

    generate_attendance.short_description = "Generate attendance for selected groups"
