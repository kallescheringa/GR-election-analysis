
"""Parser for Resultaat (Result)."""
from .common import load_xml, text, to_int, to_bool, iter_selection
 
from pathlib import Path
from .count import count_election_id
 
 
def parse_results(path: Path) -> list[dict]:
    root = load_xml(path)
    election_id = count_election_id(root)
    rows = []
    for kind, aff_id, cand_id, sel in iter_selection(root):
        elected, ranking = text(sel, "Elected"), text(sel, "Ranking")
        rows.append({
            "election_id": election_id, "affiliation_id": aff_id, "candidate_id": cand_id,
            "elected": to_bool(elected) if elected is not None else None,
            "ranking": to_int(ranking, f"Ranking (aff={aff_id}, cand={cand_id})") if ranking else None,
        })
    return rows
 