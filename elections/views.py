from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from voters.models import Student
from .models import Position, Candidate, Vote, Election
from django.db import transaction
from django.contrib.auth.decorators import user_passes_test
from .forms import CandidateForm


def is_admin(user):
    return user.is_superuser


def vote(request):
    try:
        election = Election.objects.get()
        if not election.is_active:
            messages.error(request, "The election is not currently active.")
            return redirect("voters:landing_page")
    except Election.DoesNotExist:
        messages.error(request, "The election is not currently active.")
        return redirect("voters:landing_page")

    if request.method == "POST":
        matric = request.POST.get("matric")
        email = request.POST.get("email")
        try:
            student = Student.objects.get(
                matric=matric.upper().strip(),
                email=email.lower().strip()
            )
            if student.has_voted:
                messages.error(request, "You have already voted.")
                return redirect("voters:landing_page")
            return render(
                request,
                "voters/student_details.html",
                {"student": student, "from_election": True},
            )
        except Student.DoesNotExist:
            messages.error(request, "Student details not found.")
            return redirect("voters:landing_page")

    return render(request, "elections/voter_login.html")


def voting_form(request):
    """This view handles the actual voting form"""
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        try:
            student = Student.objects.get(id=student_id)
            if student.has_voted:
                messages.error(request, "You have already voted.")
                return redirect("voters:landing_page")

            positions = Position.objects.prefetch_related("candidates").all()
            return render(
                request,
                "elections/voting_form.html",
                {"student": student, "positions": positions},
            )

        except Student.DoesNotExist:
            messages.error(request, "Invalid student.")
            return redirect("elections:vote")

    # If not POST, redirect to vote page
    return redirect("elections:vote")


def submit_vote(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        try:
            student = Student.objects.get(id=student_id)
            if student.has_voted:
                messages.error(request, "You have already submitted your vote.")
                return redirect("voters:landing_page")

            with transaction.atomic():
                positions = Position.objects.all()
                for position in positions:
                    candidate_id = request.POST.get(f"position_{position.id}")
                    if candidate_id:
                        candidate = Candidate.objects.get(id=candidate_id)
                        Vote.objects.create(
                            student=student, position=position, candidate=candidate
                        )

                student.has_voted = True
                student.save()

            messages.success(request, "Your vote has been cast successfully.")
            return redirect("voters:landing_page")

        except Student.DoesNotExist:
            messages.error(request, "Invalid student.")
            return redirect("voters:landing_page")
        except Candidate.DoesNotExist:
            messages.error(request, "Invalid candidate selected.")
            return redirect("elections:vote")

    return redirect("elections:vote")


@user_passes_test(is_admin)
def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, "elections/candidate_list.html", {"candidates": candidates})


@user_passes_test(is_admin)
def add_candidate(request):
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added successfully.")
            return redirect("elections:candidate_list")
    else:
        form = CandidateForm()
    return render(request, "elections/candidate_form.html", {"form": form})


@user_passes_test(is_admin)
def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate updated successfully.")
            return redirect("elections:candidate_list")
    else:
        form = CandidateForm(instance=candidate)
    return render(request, "elections/candidate_form.html", {"form": form})


@user_passes_test(is_admin)
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    messages.success(request, "Candidate deleted successfully.")
    return redirect("elections:candidate_list")
