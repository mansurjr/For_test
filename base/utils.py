from datetime import date, timedelta
from .models import Attendance, Student, Group

def generate_attendance_for_group(group_id):
    try:
        group = Group.objects.get(id=group_id)
        students = Student.objects.filter(group=group)
        
        start_date = group.start_date
        end_date = group.end_date

        bugun = date.today()
        juft_hafta_kunlari = {0, 2, 4}
        toq_hafta_kunlari = {1, 3, 5}

        if bugun.weekday() in juft_hafta_kunlari:
            tanlangan_kunlar = juft_hafta_kunlari
        else:
            tanlangan_kunlar = toq_hafta_kunlari

        sana = start_date
        while sana <= end_date:
            if sana.weekday() in tanlangan_kunlar:
                for student in students:
                    Attendance.objects.get_or_create(student=student, date=sana)
            sana += timedelta(days=1)

    except Group.DoesNotExist:
        print(f"Guruh topilmadi: ID {group_id}")