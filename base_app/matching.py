"""Proposes possible matches between searches and registered people.

Matches are only suggestions. A volunteer reviews each one, and the person who was
found decides whether the searcher is told anything at all.

This uses Python's difflib so it works on any database, which is fine at demo scale.
For a real deployment, PostgreSQL trigram search (django.contrib.postgres) would do
the first round of filtering inside the database instead of in Python.
"""

import difflib
import re
import unicodedata

from .models import Match, PersonRecord, SearchRequest

MATCH_THRESHOLD = 0.45
MAX_MATCHES_PER_SEARCH = 5
AGE_PREFILTER_YEARS = 12
STRONG_NAME_SIMILARITY = 0.85
STOPWORDS = {"the", "and", "near", "of", "at", "in", "on", "by", "st", "street", "ave", "avenue", "rd", "road"}


def _normalize(text):
    """Lowercase, strip accents (Nguyễn -> nguyen), and drop punctuation."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split())


def _name_variants(*texts):
    """Every name a person might go by. Other-names fields are split on commas, semicolons, and slashes."""
    variants = []
    for text in texts:
        for part in re.split(r"[,;/\n]", text or ""):
            normalized = _normalize(part)
            if normalized:
                variants.append(normalized)
    return variants


def _name_similarity(names_a, names_b):
    """Best similarity between any pair of names. First names alone count, but slightly less than full names."""
    best = 0.0
    for a in names_a:
        for b in names_b:
            full = difflib.SequenceMatcher(None, a, b).ratio()
            first = difflib.SequenceMatcher(None, a.split()[0], b.split()[0]).ratio()
            best = max(best, full, 0.85 * first)
    return best


def _place_overlap(text_a, text_b):
    words_a = {w for w in _normalize(text_a).split() if len(w) > 1 and w not in STOPWORDS}
    words_b = {w for w in _normalize(text_b).split() if len(w) > 1 and w not in STOPWORDS}
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / min(len(words_a), len(words_b))


def _age_closeness(age_a, age_b):
    if age_a is None or age_b is None:
        return 0.0
    gap = abs(age_a - age_b)
    if gap <= 3:
        return 1.0
    if gap <= 7:
        return 0.6
    if gap <= AGE_PREFILTER_YEARS:
        return 0.2
    return 0.0


def _is_looking_for_searcher(person, search):
    """True if the registered person said they're looking for someone with the searcher's name."""
    wanted = [line.split(",")[0] for line in person.looking_for.splitlines()]
    return _name_similarity(_name_variants(*wanted), _name_variants(search.searcher_name)) >= STRONG_NAME_SIMILARITY


def score(search, person):
    """Return (score from 0 to 1, list of plain-language reasons for the volunteer reviewing it)."""
    reasons = []
    total = 0.0

    # An alias tells us little, so lean on the other details instead.
    name_weight = 0.25 if person.name_is_alias else 0.5
    name_sim = _name_similarity(
        _name_variants(search.sought_name, search.sought_other_names),
        _name_variants(person.name, person.other_names),
    )
    total += name_weight * name_sim
    if name_sim >= STRONG_NAME_SIMILARITY:
        reasons.append("Name is very similar")
    elif name_sim >= 0.6:
        reasons.append("Name is somewhat similar")

    age = _age_closeness(search.sought_age, person.approximate_age)
    total += 0.15 * age
    if age >= 0.6:
        reasons.append(f"Age is close (searcher said {search.sought_age}, record says {person.approximate_age})")

    home = _place_overlap(search.sought_home_area, person.home_area)
    total += 0.15 * home
    if home:
        reasons.append("Same home area")

    evacuated_from = _place_overlap(search.sought_location_at_evacuation, person.location_at_evacuation)
    total += 0.2 * evacuated_from
    if evacuated_from:
        reasons.append("Same place when the evacuation began")

    if _is_looking_for_searcher(person, search):
        total += 0.25
        reasons.append(f"This person said they're looking for someone named {search.searcher_name}")

    return min(total, 1.0), reasons


def _save_match(search, person, match_score, reasons):
    status = Match.Status.NEEDS_COORDINATOR if person.unaccompanied_minor else Match.Status.PROPOSED
    Match.objects.get_or_create(
        search=search, person=person, defaults={"score": match_score, "reasons": reasons, "status": status}
    )


def find_matches_for_search(search):
    """Run when a new search is filed. Checks everyone who hasn't asked to be hidden."""
    candidates = PersonRecord.objects.exclude(visibility=PersonRecord.Visibility.HIDDEN)
    if search.sought_age is not None:
        candidates = candidates.filter(
            approximate_age__gte=max(0, search.sought_age - AGE_PREFILTER_YEARS),
            approximate_age__lte=search.sought_age + AGE_PREFILTER_YEARS,
        )

    scored = []
    for person in candidates.iterator():
        match_score, reasons = score(search, person)
        if match_score >= MATCH_THRESHOLD:
            scored.append((match_score, person, reasons))

    scored.sort(key=lambda item: item[0], reverse=True)
    for match_score, person, reasons in scored[:MAX_MATCHES_PER_SEARCH]:
        _save_match(search, person, match_score, reasons)


def find_matches_for_person(person):
    """Run when someone new is registered, so earlier searches can still find them."""
    if person.visibility == PersonRecord.Visibility.HIDDEN:
        return
    for search in SearchRequest.objects.filter(status=SearchRequest.Status.OPEN).iterator():
        match_score, reasons = score(search, person)
        if match_score >= MATCH_THRESHOLD:
            _save_match(search, person, match_score, reasons)