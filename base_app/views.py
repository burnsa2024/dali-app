from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import PersonRecordForm, SearchRequestForm
from .matching import find_matches_for_person, find_matches_for_search
from .models import SearchRequest, VolunteerProfile

def static_view(request, template):
    return render(request, template)

@login_required
def register(request):
    try:
        profile = request.user.volunteer
    except VolunteerProfile.DoesNotExist:
        raise PermissionDenied("Only shelter volunteers can register people.")

    if request.method == "POST":
        form = PersonRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.shelter = profile.shelter
            record.entered_by = request.user
            record.save()
            # Check whether anyone was already searching for this person.
            find_matches_for_person(record)

            message = f"Saved {record.name}, about {record.approximate_age}, at {profile.shelter}."
            if record.unaccompanied_minor:
                message += " They're flagged as an unaccompanied minor for a coordinator to review."
            messages.success(request, message)
            # Redirect to a blank form so a refresh can't submit the same person twice.
            return redirect("register_page")
    else:
        form = PersonRecordForm()

    return render(request, "register.html", {"form": form, "shelter": profile.shelter})


def search(request):
    """Public: anyone can file a search. Results are never shown on screen."""
    if request.method == "POST":
        form = SearchRequestForm(request.POST)
        if form.is_valid():
            search_request = form.save(commit=False)
            if request.user.is_authenticated:
                search_request.entered_by = request.user
            search_request.save()
            find_matches_for_search(search_request)
            # Kept in the session (not the URL) so the code isn't left in browser history on a shared device.
            request.session["last_search_code"] = search_request.reference_code
            return redirect("search_submitted_page")
    else:
        initial = {}
        profile = getattr(request.user, "volunteer", None) if request.user.is_authenticated else None
        if profile is not None:
            # A volunteer filing on someone's behalf is usually at their own shelter.
            initial["searcher_shelter"] = profile.shelter
        form = SearchRequestForm(initial=initial)

    return render(request, "search.html", {"form": form})


def search_submitted(request):
    code = request.session.get("last_search_code")
    search_request = SearchRequest.objects.filter(reference_code=code).first() if code else None
    if search_request is None:
        return redirect("search_page")
    return render(request, "submitted.html", {"search": search_request})