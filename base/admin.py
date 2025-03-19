from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from .models import Teacher, Group, Student, Attendance
from .utils import generate_attendance_for_group
from django.contrib.auth.hashers import make_password

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

@admin.register(Teacher)
class TeacherAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TeacherResource
    list_display = ('full_name', 'username', 'password',)
    list_editable = ('username',)
    search_fields = ('full_name', 'username')

    def save_model(self, request, obj, form, change):
        if change:
            if 'password' in form.changed_data:
                obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Student)
class StudentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('full_name', 'unique_id', 'group')
    list_editable = ('unique_id',)
    search_fields = ('full_name', 'unique_id')

@admin.register(Attendance)
class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ('student', 'date', 'status')
    list_editable = ('status',)
    search_fields = ('student__full_name', 'student__group__name')

@admin.register(Group)
class GroupAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = GroupResource
    list_display = ('name', 'start_date', 'end_date', 'teacher')
    actions = ['generate_attendance']
    list_editable = ('start_date', 'end_date')
    search_fields = ('name', 'teacher__full_name')

    def generate_attendance(self, request, queryset):
        for group in queryset:
            generate_attendance_for_group(group.id)
        self.message_user(request, "Davomat jadvali yaratildi!")

    generate_attendance.short_description = "Create attendance to selected groups (from start_date to end_date)"
