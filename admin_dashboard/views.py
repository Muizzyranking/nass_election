from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from elections.models import Election, Position, Candidate
from voters.models import Student, Department
from django.db.models import Count
import csv
from django.http import HttpResponse
import io
from .forms import CandidateForm, PositionForm, DepartmentForm


@login_required
def dashboard(request):
    """Main admin dashboard"""
    try:
        election = Election.objects.get()
        voting_open = election.is_active
    except Election.DoesNotExist:
        voting_open = False

    # Statistics
    total_students = Student.objects.count()
    total_positions = Position.objects.count()
    total_candidates = Candidate.objects.count()

    # Get vote counts
    total_votes = 0
    for position in Position.objects.all():
        total_votes += (
            Candidate.objects.filter(position=position)
            .annotate(vote_count=Count("vote"))
            .aggregate(total=Count("vote"))["total"]
            or 0
        )

    context = {
        "voting_open": voting_open,
        "total_students": total_students,
        "total_positions": total_positions,
        "total_candidates": total_candidates,
        "total_votes": total_votes,
    }

    return render(request, "admin_dashboard/dashboard.html", context)


@login_required
def toggle_voting(request):
    """Toggle voting on/off"""
    if request.method == "POST":
        try:
            election = Election.objects.get()
            election.is_active = not election.is_active
            election.save()

            status = "opened" if election.is_active else "closed"
            messages.success(request, f"Voting has been {status} successfully.")
        except Election.DoesNotExist:
            # Create election if it doesn't exist
            election = Election.objects.create(is_active=True)
            messages.success(request, "Voting has been opened successfully.")

    return redirect("admin_dashboard:dashboard")


@login_required
def student_management(request):
    """Student management page"""
    students = Student.objects.all().order_by("-created_at")

    context = {
        "students": students,
        "total_students": students.count(),
    }

    return render(request, "admin_dashboard/student_management.html", context)


@login_required
def csv_upload(request):
    """Handle CSV upload for student registration"""
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a CSV file.")
            return redirect("admin_dashboard:student_management")

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)

            # Skip header if exists
            next(reader, None)

            created_count = 0
            updated_count = 0

            for row in reader:
                if len(row) >= 4:  # matric, first_name, last_name, level
                    matric, first_name, last_name, level = row[:4]
                    sex = (
                        row[4] if len(row) > 4 else "M"
                    )  # Default to M if not provided

                    student, created = Student.objects.update_or_create(
                        matric=matric,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "level": level,
                            "sex": sex,
                        },
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            messages.success(
                request,
                f"Successfully imported {created_count} new students and updated {updated_count} existing students.",
            )

        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")

    return redirect("admin_dashboard:student_management")


@login_required
def candidate_management(request):
    """Candidate management page"""
    positions = Position.objects.all()
    candidates = Candidate.objects.all().order_by("position", "last_name")

    # Group candidates by position
    positions_with_candidates = []
    for position in positions:
        position_candidates = candidates.filter(position=position)
        positions_with_candidates.append(
            {
                "position": position,
                "candidates": position_candidates,
                "candidate_count": position_candidates.count(),
            }
        )

    context = {
        "positions_with_candidates": positions_with_candidates,
        "candidates": candidates,
    }

    return render(request, "admin_dashboard/candidate_management.html", context)


def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        return redirect("admin_dashboard:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                messages.success(request, "Successfully logged in to admin dashboard.")
                return redirect("admin_dashboard:dashboard")
            else:
                messages.error(
                    request, "Invalid credentials or insufficient privileges."
                )
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "admin_dashboard/login.html", {"form": form})


def admin_logout(request):
    """Admin logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("admin_dashboard:admin_login")


# Position CRUD Views
@login_required
def position_list(request):
    """List all positions"""
    positions = Position.objects.all().order_by("name")
    return render(
        request, "admin_dashboard/position_list.html", {"positions": positions}
    )


@login_required
def position_create(request):
    """Create a new position"""
    if request.method == "POST":
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Position created successfully.")
            return redirect("admin_dashboard:position_list")
    else:
        form = PositionForm()

    return render(
        request,
        "admin_dashboard/position_form.html",
        {"form": form, "title": "Create Position", "button_text": "Create Position"},
    )


@login_required
def position_edit(request, position_id):
    """Edit an existing position"""
    position = get_object_or_404(Position, id=position_id)

    if request.method == "POST":
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, "Position updated successfully.")
            return redirect("admin_dashboard:position_list")
    else:
        form = PositionForm(instance=position)

    return render(
        request,
        "admin_dashboard/position_form.html",
        {"form": form, "title": "Edit Position", "button_text": "Update Position"},
    )


@login_required
def position_delete(request, position_id):
    """Delete a position"""
    position = get_object_or_404(Position, id=position_id)

    if request.method == "POST":
        position.delete()
        messages.success(request, "Position deleted successfully.")
        return redirect("admin_dashboard:position_list")

    return render(
        request, "admin_dashboard/position_confirm_delete.html", {"position": position}
    )


# Candidate CRUD Views
@login_required
def candidate_create(request):
    """Create a new candidate"""
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate created successfully.")
            return redirect("admin_dashboard:candidate_management")
    else:
        form = CandidateForm()

    return render(
        request,
        "admin_dashboard/candidate_form.html",
        {"form": form, "title": "Create Candidate", "button_text": "Create Candidate"},
    )


@login_required
def candidate_edit(request, candidate_id):
    """Edit an existing candidate"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate updated successfully.")
            return redirect("admin_dashboard:candidate_management")
    else:
        form = CandidateForm(instance=candidate)

    return render(
        request,
        "admin_dashboard/candidate_form.html",
        {"form": form, "title": "Edit Candidate", "button_text": "Update Candidate"},
    )


@login_required
def candidate_delete(request, candidate_id):
    """Delete a candidate"""
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        candidate.delete()
        messages.success(request, "Candidate deleted successfully.")
        return redirect("admin_dashboard:candidate_management")

    return render(
        request,
        "admin_dashboard/candidate_confirm_delete.html",
        {"candidate": candidate},
    )


# Student Delete View
@login_required
def student_delete(request, student_id):
    """Delete a student"""
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect("admin_dashboard:student_management")

    return render(
        request, "admin_dashboard/student_confirm_delete.html", {"student": student}
    )


# Student Detail View
@login_required
def student_detail(request, student_id):
    """View student details"""
    student = get_object_or_404(Student, id=student_id)
    return render(request, "admin_dashboard/student_detail.html", {"student": student})


# Department CRUD Views
@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.all().order_by("name")
    return render(
        request, "admin_dashboard/department_list.html", {"departments": departments}
    )


@login_required
def department_create(request):
    """Create a new department"""
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect("admin_dashboard:department_list")
    else:
        form = DepartmentForm()

    return render(
        request,
        "admin_dashboard/department_form.html",
        {
            "form": form,
            "title": "Create Department",
            "button_text": "Create Department",
        },
    )


@login_required
def department_edit(request, department_id):
    """Edit an existing department"""
    department = get_object_or_404(Department, id=department_id)

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect("admin_dashboard:department_list")
    else:
        form = DepartmentForm(instance=department)

    return render(
        request,
        "admin_dashboard/department_form.html",
        {"form": form, "title": "Edit Department", "button_text": "Update Department"},
    )


@login_required
def department_delete(request, department_id):
    """Delete a department"""
    department = get_object_or_404(Department, id=department_id)

    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect("admin_dashboard:department_list")

    return render(
        request,
        "admin_dashboard/department_confirm_delete.html",
        {"department": department},
    )
