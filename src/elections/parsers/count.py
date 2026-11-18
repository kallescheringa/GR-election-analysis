"""Parsing of one block of count data (a polling station, or the whole
municipality). Shared by the Telling and Totaaltelling parsers."""
from .common import to_int, iter_selection

import json

STAT_TAGS = ("cast", "TotalCounted", "RejectedVote", "UncountedVotes")
LEVEL_UNIT = "polling_station"
LEVEL_TOTAL = "municipality"

def parse_count_block(block, election_id, level, unit_id):
    affiliation_votes, candidate_votes, stats, investigations = [], [], [], [] 
    for kind, affiliation_id, candidate_id, sel in iter_selection(block):
        vv = sel.find("ValidVotes")
        if vv is None:
            continue
        votes = to_int(vv.text, f"ValidVotes (unit={unit_id}, affiliation={affiliation_id}, candidate={candidate_id})")
        row = {"election_id": election_id, "count_level": level,
               "reporting_unit_id": unit_id, "affiliation_id": affiliation_id, "valid_votes": votes}
        if kind == "affiliation":
            affiliation_votes.append(row)
        else:
            row["candidate_id"] = candidate_id
            candidate_votes.append(row)
    for element in block.iter():
        if element.tag in STAT_TAGS:
            stats.append({
                "election_id": election_id, "count_level": level, "reporting_unit_id": unit_id,
                "stat_type": element.tag,
                "reason_code": element.get("ReasonCode"),
                "category": element.get("Category"),
                "value": to_int(element.text, f"{element.tag} (unit={unit_id})"),
            })
        elif element.tag == "ReportingUnitInvestigations":
            for child in element.iter():
                if child is element and not element.attrib and not (element.text or "").strip():
                    continue
                investigations.append({
                    "election_id": election_id, "reporting_unit_id": unit_id,
                    "element": child.tag,
                    "attributes": json.dumps(child.attrib, ensure_ascii=False),
                    "text": (child.text or "").strip() or None,
                })
    return affiliation_votes, candidate_votes, stats, investigations

def count_election_id(root):
    ident = root.find(".//Election/ElectionIdentifier")
    return ident.get("Id") if ident is not None else None