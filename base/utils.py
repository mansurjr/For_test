from datetime import date, timedelta
from .models import Attendance, Student, Group

def generate_attendance_for_group(group_id):
    try:
        group = Group.objects.get(id=group_id)
        students = Student.objects.filter(group=group)

        start_date = group.start_date
        end_date = group.end_date

        bugun = start_date

        even_days = {0, 2, 4}
        odd_days = {1, 3, 5}

        choosed_days = even_days if start_date.weekday() in even_days else odd_days

        ignored_dates = {(1, 1), (3, 21)}

        ignored_weekdays = {6}

        sana = start_date
        while sana <= end_date:
            if (sana.weekday() in choosed_days
                and (sana.month, sana.day) not in ignored_dates 
                and sana.weekday() not in ignored_weekdays):
                for student in students:
                    Attendance.objects.get_or_create(student=student, date=sana)
            sana += timedelta(days=1)

    except Group.DoesNotExist:
        print(f"Guruh topilmadi: ID {group_id}")