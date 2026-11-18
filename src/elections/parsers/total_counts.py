"""Parser for Totaaltelling (Count, municipality totals)."""
from .common import load_xml
 
from pathlib import Path
 
from .count import LEVEL_TOTAL, parse_count_block, count_election_id
 
 
def parse_total_counts(path: Path) -> dict:
    """Totaaltelling: municipality-wide figures, kept at count_level='municipality'."""
    root = load_xml(path)
    election_id = count_election_id(root)
    for parent in list(root.iter()):             
        for child in list(parent):
            if child.tag == "ReportingUnitVotes":
                parent.remove(child)
    av, cv, st, inv = parse_count_block(root, election_id, LEVEL_TOTAL, None)
    return {"affiliation_votes": av, "candidate_votes": cv, "vote_statistics": st, "investigations": inv}