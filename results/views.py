from django.shortcuts import render
from elections.models import Position, Candidate, Vote, Election
from django.db.models import Count


def results_page(request):
    # Get election status
    try:
        election = Election.objects.get()
        voting_open = election.is_active
    except Election.DoesNotExist:
        voting_open = False

    positions = Position.objects.all()
    results = []
    has_votes = False

    for position in positions:
        candidates = Candidate.objects.filter(position=position).annotate(
            vote_count=Count("vote")
        )
        winner = candidates.order_by("-vote_count").first()

        # Check if any candidate has votes
        position_votes = sum(candidate.vote_count for candidate in candidates)
        if position_votes > 0:
            has_votes = True

        # Calculate percentages for each candidate
        candidates_with_percentages = []
        for candidate in candidates:
            percentage = 0
            if position_votes > 0:
                percentage = (candidate.vote_count / position_votes) * 100
            candidates_with_percentages.append(
                {
                    "candidate": candidate,
                    "vote_count": candidate.vote_count,
                    "percentage": percentage,
                }
            )

        results.append(
            {
                "position": position,
                "candidates": candidates_with_percentages,
                "winner": winner,
                "total_votes": position_votes,
            }
        )

    context = {
        "results": results,
        "voting_open": voting_open,
        "has_votes": has_votes,
        "show_results": not voting_open and has_votes,
    }

    return render(request, "results/results_page.html", context)
