from django.urls import path
from . import views

app_name = 'voters'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('verify/', views.verify_student, name='verify_student'),
    path('register/', views.register_student, name='register_student'),
    path('admin/upload_csv/', views.upload_csv, name='upload_csv'),
]
