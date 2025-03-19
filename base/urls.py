from django.urls import path
from .views import login_view, logout_view, dashboard, group_details,update_attendance
from django.conf import settings


urlpatterns = [
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("group/<int:group_id>/", group_details, name="group_details"),
    path("update_attendence/", update_attendance, name='update_attendance'),
]
