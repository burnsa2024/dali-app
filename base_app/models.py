import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    area = models.CharField(max_length=200, blank=True, help_text="City or neighborhood the shelter is in.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class VolunteerProfile(models.Model):
    """Links a login to the shelter where that volunteer works. Created by coordinators in the admin."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="volunteer")
    shelter = models.ForeignKey(Shelter, on_delete=models.PROTECT, related_name="volunteers")

    def __str__(self):
        return f"{self.user} at {self.shelter}"


class PersonRecord(models.Model):
    """One person registered as safe at a shelter.

    Deliberately not collected: ID numbers, exact date of birth, full address,
    immigration status, medical information, and photos.
    """

    MINOR_AGE = 18

    class Visibility(models.TextChoices):
        ASK_FIRST = "ask_first", "Ask them before sharing anything"
        HIDDEN = "hidden", "Don't show them in any search"

    class Gender(models.TextChoices):
        WOMAN = "woman", "Woman"
        MAN = "man", "Man"
        OTHER = "other", "Another gender"
        UNSAID = "unsaid", "Prefer not to say"

    class Source(models.TextChoices):
        IN_PERSON = "in_person", "In person"
        PAPER = "paper", "From a paper form"
        IMPORT = "import", "Imported from another system"

    class Status(models.TextChoices):
        PRESENT = "present", "At this shelter"
        CHECKED_OUT = "checked_out", "Left the shelter"
        TRANSFERRED = "transferred", "Moved to another shelter"

    # Required
    name = models.CharField(max_length=150)
    approximate_age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(120)])

    # Matching details (all optional)
    other_names = models.CharField(max_length=300, blank=True)
    home_area = models.CharField(max_length=200, blank=True)
    location_at_evacuation = models.CharField(max_length=200, blank=True)
    looking_for = models.TextField(blank=True)
    languages = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True)

    # Companions and contact (never shown to searchers)
    accompanied_by = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    # Privacy
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.ASK_FIRST)
    name_is_alias = models.BooleanField(default=False)
    unaccompanied_minor = models.BooleanField(default=False, editable=False)

    # Bookkeeping
    shelter = models.ForeignKey(Shelter, on_delete=models.PROTECT, related_name="people")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    forwarding_note = models.CharField(max_length=300, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.IN_PERSON)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="people_entered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["shelter", "status"])]

    def __str__(self):
        return f"{self.name} (~{self.approximate_age})"

    @property
    def is_minor(self):
        return self.approximate_age is not None and self.approximate_age < self.MINOR_AGE

    def save(self, *args, **kwargs):
        # Recomputed on every save so the flag can't drift out of sync with age or companions.
        self.unaccompanied_minor = self.is_minor and not self.accompanied_by.strip()
        super().save(*args, **kwargs)


CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O or 1/I, which are easy to mix up when read aloud


def generate_reference_code():
    raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


class SearchRequest(models.Model):
    """Someone looking for a person. Searchers are never shown results directly."""

    class Status(models.TextChoices):
        OPEN = "open", "Still searching"
        RESOLVED = "resolved", "Reunited"
        CLOSED = "closed", "Closed"

    reference_code = models.CharField(max_length=9, unique=True, editable=False)

    # The person being sought
    sought_name = models.CharField(max_length=150)
    sought_other_names = models.CharField(max_length=300, blank=True)
    sought_age = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(120)])
    sought_home_area = models.CharField(max_length=200, blank=True)
    sought_location_at_evacuation = models.CharField(max_length=200, blank=True)
    details = models.TextField(blank=True)

    # The searcher, and how to reach them
    searcher_name = models.CharField(max_length=150)
    searcher_relationship = models.CharField(max_length=100, blank=True)
    searcher_shelter = models.ForeignKey(
        Shelter, on_delete=models.SET_NULL, null=True, blank=True, related_name="searches_from",
        limit_choices_to={"is_active": True},
    )
    searcher_phone = models.CharField(max_length=30, blank=True)
    searcher_email = models.EmailField(blank=True)

    # Bookkeeping
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="searches_entered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference_code}: {self.searcher_name} looking for {self.sought_name}"

    @property
    def has_contact_method(self):
        return bool(self.searcher_shelter_id or self.searcher_phone or self.searcher_email)

    def save(self, *args, **kwargs):
        if not self.reference_code:
            code = generate_reference_code()
            while SearchRequest.objects.filter(reference_code=code).exists():
                code = generate_reference_code()
            self.reference_code = code
        super().save(*args, **kwargs)


class Match(models.Model):
    """A possible match between a search and a registered person, waiting for human review and consent."""

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Waiting for a volunteer to ask"
        NEEDS_COORDINATOR = "needs_coordinator", "Needs coordinator review (minor)"
        ASKED = "asked", "Asked, waiting for an answer"
        ACCEPTED = "accepted", "Wants to connect"
        DECLINED = "declined", "Declined"
        REJECTED = "rejected", "Not the right person"

    search = models.ForeignKey(SearchRequest, on_delete=models.CASCADE, related_name="matches")
    person = models.ForeignKey(PersonRecord, on_delete=models.CASCADE, related_name="matches")
    score = models.FloatField()
    reasons = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-score"]
        constraints = [models.UniqueConstraint(fields=["search", "person"], name="unique_match_per_search_person")]

    def __str__(self):
        return f"{self.search.reference_code} -> {self.person} ({self.score:.2f})"