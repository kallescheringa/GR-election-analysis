"""Parser for the Telling (count, per polling station)"""
from .common import load_xml

from pathlib import Path
from .count import LEVEL_UNIT, parse_count_block, count_election_id

def parse_polling_station_counts(path: Path) -> dict:
    """Telling: one block of results per polling station."""
    root = load_xml(path)
    election_id = count_election_id(root)
    out = {"reporting_units": [], "affiliation_votes": [], "candidate_votes": [],
           "vote_statistics": [], "investigations": []}

    for unit in root.iter("ReportingUnitVotes"):
        ident = unit.find("ReportingUnitIdentifier")
        unit_id = ident.get("Id") if ident is not None else None
        out["reporting_units"].append({
            "election_id": election_id, "reporting_unit_id": unit_id,
            "name": (ident.text or "").strip() or None if ident is not None else None,
        })
        affiliation_votes, candidate_votes, stats, investigations = parse_count_block(unit, election_id, LEVEL_UNIT, unit_id)
        out["affiliation_votes"] += affiliation_votes
        out["candidate_votes"] += candidate_votes
        out["vote_statistics"] += stats
        out["investigations"] += investigations

    return out