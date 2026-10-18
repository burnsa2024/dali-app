from django import forms

from .models import PersonRecord, SearchRequest

# (section title, short intro, field names). Drives both the form's fields and the template layout.
INTAKE_SECTIONS = [
    ("About them", "", ["name", "approximate_age"]),
    (
        "Helps family find them",
        "Fill in whatever they know. Every detail makes a match more likely.",
        ["other_names", "home_area", "location_at_evacuation", "looking_for", "languages", "gender"],
    ),
    (
        "Who they're with and how to reach them",
        "Contact details are only shared if they agree to a match.",
        ["accompanied_by", "phone", "email"],
    ),
    ("Privacy and record details", "", ["visibility", "name_is_alias", "source"]),
]


class PersonRecordForm(forms.ModelForm):
    """Intake form for shelter volunteers. The view sets shelter and entered_by."""

    class Meta:
        model = PersonRecord
        fields = [name for _, _, names in INTAKE_SECTIONS for name in names]
        labels = {
            "name": "Name",
            "approximate_age": "Approximate age",
            "other_names": "Other names or spellings",
            "home_area": "Home neighborhood or street",
            "location_at_evacuation": "Where were they when the evacuation began?",
            "looking_for": "Who are they looking for?",
            "languages": "Languages spoken",
            "gender": "Gender",
            "accompanied_by": "Who did they arrive with?",
            "phone": "Phone number, if they have one",
            "email": "Email, if they have one",
            "visibility": "If someone searches for them",
            "name_is_alias": "This is not their usual name",
            "source": "How is this being entered?",
        }
        help_texts = {
            "name": "The name they want to use. A nickname is fine, and a surname isn't needed.",
            "approximate_age": "A best guess is fine.",
            "other_names": "Nicknames, maiden names, or other ways to spell their name.",
            "home_area": "The area only, not the full address. For example: Eastside, near Oak St.",
            "location_at_evacuation": "For example: Jefferson Elementary, Bayview Nursing Home, or at home.",
            "looking_for": "One person per line: name, relationship, rough age. For example: Carlos, son, about 35.",
            "accompanied_by": "Leave blank if they arrived alone.",
            "phone": "Never shown to people searching.",
            "email": "Never shown to people searching.",
            "visibility": "Either way, nobody is told where they are without their permission.",
            "name_is_alias": "Check this if they'd rather not give their real name. Matching will rely more on other details.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocapitalize": "words", "spellcheck": "false"}),
            "approximate_age": forms.NumberInput(attrs={"min": 0, "max": 120, "inputmode": "numeric"}),
            "other_names": forms.TextInput(attrs={"autocapitalize": "words", "spellcheck": "false"}),
            "looking_for": forms.Textarea(attrs={"rows": 3, "spellcheck": "false"}),
            "phone": forms.TextInput(attrs={"type": "tel", "inputmode": "tel"}),
            "visibility": forms.RadioSelect,
            "source": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Distinguish "not asked" from the person actively choosing not to say.
        self.fields["gender"].choices = [("", "Not given")] + list(PersonRecord.Gender.choices)

    def sections(self):
        """Bound fields grouped for the template: [(title, intro, [bound_field, ...]), ...]."""
        return [(title, intro, [self[name] for name in names]) for title, intro, names in INTAKE_SECTIONS]

    def clean_name(self):
        # Collapse stray whitespace so "Rosa  M" and "Rosa M" are stored the same way.
        return " ".join(self.cleaned_data["name"].split())

    def clean_other_names(self):
        return " ".join(self.cleaned_data["other_names"].split())


SEARCH_SECTIONS = [
    (
        "Who are you looking for?",
        "Only their name is required. Every other detail helps us tell apart people with similar names.",
        ["sought_name", "sought_other_names", "sought_age", "sought_home_area", "sought_location_at_evacuation", "details"],
    ),
    ("About you", "", ["searcher_name", "searcher_relationship"]),
    (
        "How can we reach you?",
        "Many people have lost their phones, so any one of these is enough. You'll also get a code to check back with.",
        ["searcher_shelter", "searcher_phone", "searcher_email"],
    ),
]


class SearchRequestForm(forms.ModelForm):
    """Public search form. Used by family members directly, or by a volunteer on their behalf."""

    class Meta:
        model = SearchRequest
        fields = [name for _, _, names in SEARCH_SECTIONS for name in names]
        labels = {
            "sought_name": "Their name",
            "sought_other_names": "Other names or spellings",
            "sought_age": "Their approximate age",
            "sought_home_area": "Their home neighborhood or street",
            "sought_location_at_evacuation": "Where were they when the evacuation began?",
            "details": "Anything else that might help?",
            "searcher_name": "Your name",
            "searcher_relationship": "How do you know them?",
            "searcher_shelter": "Are you staying at a shelter?",
            "searcher_phone": "Your phone number",
            "searcher_email": "Your email",
        }
        help_texts = {
            "sought_name": "Whatever you call them. A first name or nickname is fine.",
            "sought_other_names": "Nicknames, maiden names, or other ways their name might be written.",
            "sought_age": "A best guess is fine. Leave blank if you're not sure.",
            "sought_home_area": "Where they lived before the evacuation. For example: Eastside, near Oak St.",
            "sought_location_at_evacuation": "For example: Jefferson Elementary, Bayview Nursing Home, or at work.",
            "details": "Languages they speak, who they might be with, or anything that sets them apart.",
            "searcher_name": "The name they would know you by.",
            "searcher_relationship": "For example: daughter, husband, neighbor.",
            "searcher_shelter": "If you are, a volunteer there can pass on any news.",
            "searcher_phone": "Only if you have a working phone.",
            "searcher_email": "Only if you can check email.",
        }
        widgets = {
            "sought_name": forms.TextInput(attrs={"autocapitalize": "words", "spellcheck": "false"}),
            "sought_other_names": forms.TextInput(attrs={"autocapitalize": "words", "spellcheck": "false"}),
            "sought_age": forms.NumberInput(attrs={"min": 0, "max": 120, "inputmode": "numeric"}),
            "details": forms.Textarea(attrs={"rows": 3}),
            "searcher_name": forms.TextInput(attrs={"autocapitalize": "words", "spellcheck": "false"}),
            "searcher_phone": forms.TextInput(attrs={"type": "tel", "inputmode": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["searcher_shelter"].empty_label = "No, I'm not at a shelter"

    def sections(self):
        return [(title, intro, [self[name] for name in names]) for title, intro, names in SEARCH_SECTIONS]

    def clean_sought_name(self):
        return " ".join(self.cleaned_data["sought_name"].split())

    def clean_searcher_name(self):
        return " ".join(self.cleaned_data["searcher_name"].split())