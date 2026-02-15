from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Department # Import Department
from .forms import StudentForm
import csv
from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_superuser


def landing_page(request):
    return render(request, "voters/landing_page.html")


def verify_student(request):
    if request.method == "POST":
        matric = request.POST.get("matric")
        email = request.POST.get("email")

        try:
            student = Student.objects.get(
                matric=matric.upper().strip(),
                email=email.lower().strip()
            )
            return render(
                request, "voters/student_details.html", {"student": student}
            )
        except Student.DoesNotExist:
            messages.error(request, "Student details not found. Please register.")
            return redirect("voters:register_student")
    return render(request, "voters/verify_student.html")


def register_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # Normalization is now handled in the Student model's save method
            student = form.save()
            messages.success(
                request, "Registration successful. You can now verify your details."
            )
            return redirect("voters:verify_student")
    else:
        form = StudentForm()
    return render(request, "voters/register_student.html", {"form": form})


@user_passes_test(is_admin)
def upload_csv(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a .csv file.")
            return redirect("voters:upload_csv")

        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                department = None
                if "department" in row and row["department"]:
                    department, _ = Department.objects.get_or_create(name=row["department"].strip())

                student_data = {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "level": row["level"],
                    "sex": row["sex"],
                    "department": department,
                }
                
                if "middle_name" in row and row["middle_name"]:
                    student_data["middle_name"] = row["middle_name"]

                Student.objects.update_or_create(
                    matric=row["matric"],
                    defaults=student_data,
                )
            messages.success(request, "Students uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")

        return redirect("voters:upload_csv")

    return render(request, "voters/upload_csv.html")
