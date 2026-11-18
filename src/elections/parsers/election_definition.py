"""Parser for Verkiezingsdefinitie"""
from .common import load_xml, text, to_int

from pathlib import Path

def parse_election_definition(path: Path) -> dict:
    root = load_xml(path)
    element = root.find(".//Election")
    ident = element.find("ElectionIdentifier") if element is not None else None
    threshold = root.find(".//PreferenceThreshold")
    threshold_value = (threshold.text or "").strip() or threshold.get("Value") if threshold is not None else None
    return {
        "election_id": ident.get("Id") if ident is not None else None,
        "election_name": text(root, ".//ElectionName"),
        "election_category": text(root, ".//ElectionCategory"),
        "election_date": text(root, ".//ElectionDate"),
        "municipality": text(root, ".//ElectionDomain"),
        "number_of_seats": (to_int(text(root, ".//NumberOfSeats"), "NumberOfSeats")
                            if text(root, ".//NumberOfSeats") else None),
        "preference_threshold": threshold_value,
        "voting_method": text(root, ".//VotingMethod"),
        "registered_parties": [n.text.strip() for n in root.iter("RegisteredName") if n.text],
    }   