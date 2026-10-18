from django.shortcuts import render

def static_view(request, template):
    return render(request, template)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import PersonRecordForm


@login_required
def register(request):
    profile = getattr(request.user, "volunteer", None)
    if profile is None:
        raise PermissionDenied("Only shelter volunteers can register people.")

    if request.method == "POST":
        form = PersonRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.shelter = profile.shelter
            record.entered_by = request.user
            record.save()

            message = f"Saved {record.name}, about {record.approximate_age}, at {profile.shelter}."
            if record.unaccompanied_minor:
                message += " They're flagged as an unaccompanied minor for a coordinator to review."
            messages.success(request, message)
            # Redirect to a blank form so a refresh can't submit the same person twice.
            return redirect("register_page")
    else:
        form = PersonRecordForm()

    return render(request, "register.html", {"form": form, "shelter": profile.shelter})