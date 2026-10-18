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
        MALE = "male", "Male"
        FEMALE = "female", "Female"
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