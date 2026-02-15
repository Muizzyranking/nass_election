from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("toggle-voting/", views.toggle_voting, name="toggle_voting"),
    path("students/", views.student_management, name="student_management"),
    path(
        "students/detail/<int:student_id>/", views.student_detail, name="student_detail"
    ),
    path(
        "students/delete/<int:student_id>/", views.student_delete, name="student_delete"
    ),
    path("departments/", views.department_list, name="department_list"),
    path("departments/create/", views.department_create, name="department_create"),
    path(
        "departments/edit/<int:department_id>/",
        views.department_edit,
        name="department_edit",
    ),
    path(
        "departments/delete/<int:department_id>/",
        views.department_delete,
        name="department_delete",
    ),
    path("upload-csv/", views.csv_upload, name="csv_upload"),
    path("candidates/", views.candidate_management, name="candidate_management"),
    path("candidates/create/", views.candidate_create, name="candidate_create"),
    path(
        "candidates/edit/<int:candidate_id>/",
        views.candidate_edit,
        name="candidate_edit",
    ),
    path(
        "candidates/delete/<int:candidate_id>/",
        views.candidate_delete,
        name="candidate_delete",
    ),
    path("positions/", views.position_list, name="position_list"),
    path("positions/create/", views.position_create, name="position_create"),
    path(
        "positions/edit/<int:position_id>/", views.position_edit, name="position_edit"
    ),
    path(
        "positions/delete/<int:position_id>/",
        views.position_delete,
        name="position_delete",
    ),
]
