from django.urls import path
from . import views

app_name = "elections"

from django.urls import path
from . import views

app_name = "elections"

urlpatterns = [
    path("election/", views.vote, name="vote"),
    path("voting/", views.voting_form, name="voting_form"),
    path("submit_vote/", views.submit_vote, name="submit_vote"),
    path("admin/candidates/", views.candidate_list, name="candidate_list"),
    path("admin/candidates/add/", views.add_candidate, name="add_candidate"),
    path(
        "admin/candidates/edit/<int:candidate_id>/",
        views.edit_candidate,
        name="edit_candidate",
    ),
    path(
        "admin/candidates/delete/<int:candidate_id>/",
        views.delete_candidate,
        name="delete_candidate",
    ),
]
