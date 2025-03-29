from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    login_view, logout_view, dashboard, group_details, 
    update_attendance, user_info
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("group/<int:group_id>/", group_details, name="group_details"),
    path("update_attendance/", update_attendance, name="update_attendance"),
    path("user_info/", user_info, name="user_info"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
