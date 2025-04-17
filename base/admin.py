from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from .models import Staffs, Group, Student, Attendance
from .utils import generate_attendance_for_group
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from dateutil.relativedelta import relativedelta


# ======================== Resources ========================
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


# ======================== Custom Staff Forms ========================
class StaffsCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = Staffs
        fields = ("username", "phone_number", "position")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class StaffsChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Staffs
        fields = ("username", "phone_number", "position", "password", "is_active", "is_staff")

    def clean_password(self):
        return self.initial["password"]


# ======================== Staffs Admin ========================
@admin.register(Staffs)
class TeacherAdmin(ExportMixin, UserAdmin):
    add_form = StaffsCreationForm
    form = StaffsChangeForm
    model = Staffs
    resource_class = TeacherResource
    list_display = ("username", "phone_number", "position", "is_active", "last_login")
    list_filter = ("is_active", "position")
    search_fields = ("username", "phone_number")
    readonly_fields = ("last_login",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("phone_number", "position", "profile_picture")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "phone_number", "position", "password1", "password2"),
        }),
    )


# ======================== Student Admin ========================
@admin.register(Student)
class StudentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ("name", "surname", "unique_id", "group")
    search_fields = ("name", "surname", "unique_id")


# ======================== Attendance Admin ========================
@admin.register(Attendance)
class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ("student", "date", "status")
    list_editable = ("status",)
    search_fields = ("student__name", "student__surname", "student__group__name")


# ======================== Group Admin ========================
class GroupForm(forms.ModelForm):
    DURATION_CHOICES = [
        (1, "1 Month"),
        (3, "3 Months"),
        (5, "5 Months"),
        (7, "7 Months"),
        (8, "8 Months"),
    ]

    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=True, label="Duration (Months)")

    class Meta:
        model = Group
        fields = ("name", "start_date", "lesson_start_time", "lesson_end_time", "teacher")

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
    resource_class = GroupResource
    list_display = ("name", "start_date", "end_date", "lesson_start_time", "lesson_end_time", "teacher_display")
    actions = ["generate_attendance"]
    list_editable = ("lesson_start_time", "end_date")
    search_fields = ("name", "teacher__username")

    def teacher_display(self, obj):
        return obj.teacher.username if obj.teacher else "No Teacher"
    teacher_display.short_description = "Teacher"

    def generate_attendance(self, request, queryset):
        for group in queryset:
            generate_attendance_for_group(group.id)
        self.message_user(request, "Attendance records created successfully!")

    generate_attendance.short_description = "Generate attendance for selected groups"
