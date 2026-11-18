"""Parser for Kandidatenlijsten"""
from .common import load_xml, text

from pathlib import Path
from collections import Counter

def _full_name(person, initials):
    """Returns the full name of a candidate given the person and initials"""
    if person is None:
        return None
    parts = [text(person, "FirstName"), text(person, "NamePrefix"), text(person, "LastName")]
    return " ".join(p for p in parts if p) or None

def parse_candidate_lists(path: Path) -> dict:
    """return (election_id, affiliations, candidates)"""
    root = load_xml(path)
    element = root.find(".//Election")
    ident = element.find("ElectionIdentifier") if element is not None else None
    election_id = ident.get("Id") if ident is not None else None
    affiliations, candidates = [], []

    for affiliation in root.iter("Affiliation"):
        affiliation_ident = affiliation.find("AffiliationIdentifier")
        affiliation_id = affiliation_ident.get("Id") if affiliation_ident is not None else None
        affiliations.append({
            "election_id": election_id,
            "affiliation_id": affiliation_id,
            "registered_name": text(affiliation, "RegisteredName") 
                or (affiliation_ident.findtext("RegisteredName") if affiliation_ident is not None else None),
            "type": text(affiliation, "Type")
        })
        for candidate in affiliation.findall("Candidate"):
            c_id = candidate.find("CandidateIdentifier")
            person = candidate.find(".//PersonName")
            initials = None
            if person is not None:
                for nl in person.iter("NameLine"):
                    if nl.get("NameType") == "Initials":
                        initials = (nl.text or "").strip() or None
            candidates.append({
                "election_id": election_id,
                "affiliation_id": affiliation_id,
                "candidate_id": c_id.get("Id") if c_id is not None else None,
                "full_name": _full_name(person, initials),
                "initials": initials,
                "first_name": text(person, "FirstName"),
                "name_prefix": text(person, "NamePrefix"),
                "last_name": text(person, "LastName"),
                "gender": text(candidate, "Gender"),
                "locality": text(candidate, ".//LocalityName"),
            })
    return election_id, affiliations, candidates
