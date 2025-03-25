from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from .models import Teacher, Group, Student, Attendance
from .utils import generate_attendance_for_group
from django import forms
from dateutil.relativedelta import relativedelta

# Resource Classes for Import/Export
class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher

class GroupResource(resources.ModelResource):
    class Meta:
        model = Group

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance

# Admin Classes
@admin.register(Teacher)
class TeacherAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ('full_name', 'username')
    search_fields = ('full_name', 'username')

@admin.register(Student)
class StudentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('full_name', 'unique_id', 'group')
    list_editable = ()
    search_fields = ('full_name', 'unique_id')

@admin.register(Attendance)
class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ('student', 'date', 'status')
    list_editable = ('status',)
    search_fields = ('student__full_name', 'student__group__name')

# ✅ FIXED: Removed ModelAdmin Inheritance
class GroupForm(forms.ModelForm):
    DURATION_CHOICES = [
        (1, "1 Month"),
        (3, "3 Months"),
        (6, "6 Months"),
        (12, "12 Months"),
    ]

    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=True, label="Duration (Months)")

    class Meta:
        model = Group
        fields = ("name", "start_date", "lesson_starts", "teacher")  # ✅ `end_date` will be handled separately

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
        """✅ Ensures `end_date` is saved correctly"""
        instance = super().save(commit=False)
        duration = int(self.cleaned_data["duration"])
        instance.end_date = instance.start_date + relativedelta(months=duration)

        if commit:
            instance.save()
        return instance

class GroupAdmin(ExportMixin, admin.ModelAdmin):
    form = GroupForm  
    list_display = ('name', 'start_date', 'end_date', "lesson_starts", 'teacher',)
    actions = ['generate_attendance']
    list_editable = ("teacher",)
    search_fields = ('name', 'teacher__full_name')

    def generate_attendance(self, request, queryset):
        for group in queryset:
            generate_attendance_for_group(group.id)
        self.message_user(request, "Davomat jadvali yaratildi!")

    generate_attendance.short_description = "Create attendance for selected groups"

admin.site.register(Group, GroupAdmin)
