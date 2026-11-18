from elections import config
from .parsers import (
    load_xml, 
    parse_election_definition,
    parse_candidate_lists,
    parse_polling_station_counts,
    parse_total_counts,
    parse_results
)

from pathlib import Path
from typing import Any

import xml.etree.ElementTree as ET
import json 
import csv

IN_DIRECTORY = config.DATA_RAW / "lansingerland"
OUT_DIRECTORY = config.DATA_PROCESSED / "lansingerland"

# --------------------------------------------------------------------------- #
# Discovery and procession                                                    #
# --------------------------------------------------------------------------- #

def discover_files(raw_directory: Path) -> dict[str, Path]:
    """Classify files by their document element"""
    found = {}
    for path in sorted(raw_directory.glob("*.xml")) + sorted(raw_directory.glob("*.eml")):
        tag = load_xml(path).tag

        if tag == "ElectionEvent":
            key = "definition"
        elif tag == "CandidateList":
            key = "candidates"
        elif tag == "Count" and "totaal" in path.name.lower():
            key = "totals"
        elif tag == "Count":
            key = "polling_stations"
        elif tag == "Result":
            key = "results"
        else:
            continue

        if key in found:
            raise RuntimeError(f"[error] two files found for '{key}': {found[key].name} and {path.name}")
        found[key] = path

    missing_keys = {"definition", "candidates", "totals", "polling_stations", "results"} - found.keys()
    if missing_keys:
        raise FileNotFoundError(f"Following file(s) not found: {missing_keys}")

    return found

def process(raw_directory: Path) -> dict:
    files = discover_files(raw_directory)
    election_defintion = parse_election_definition(files["definition"])
    candidate_election_id, affiliations, candidates = parse_candidate_lists(files["candidates"]) 
    polling_station = parse_polling_station_counts(files["polling_stations"])
    total = parse_total_counts(files["totals"])
    results = parse_results(files["results"])

    return {
        "files": {k: v.name for k, v in files.items()},
        "elections": [election_defintion],
        "affiliations": affiliations,
        "candidates": candidates,
        "reporting_units": polling_station["reporting_units"],
        "affiliation_votes": polling_station["affiliation_votes"] + total["affiliation_votes"],
        "candidate_votes": polling_station["candidate_votes"] + total["candidate_votes"],
        "vote_statistics": polling_station["vote_statistics"] + total["vote_statistics"],
        "reporting_unit_investigations": polling_station["investigations"] + total["investigations"],
        "election_results": results
    }

# --------------------------------------------------------------------------- #
# Output                                                                      #
# --------------------------------------------------------------------------- #

def write_output(data: dict, out_directory: Path) -> bool:
    """
    Write processed election data to separate CSV files.

    Creates the output directory if it does not already exist.
    Iterates over the provided data tables, skipping the source file
    metadata and any empty tables. List values are converted to JSON
    strings to make them compatible with CSV format.

    Each remaining table is written to a separate CSV file named
    after its dictionary key. Column headers are determined from
    the keys present across all rows.

    Args:
        data: Dictionary containing the processed election data,
            where each key represents a table name and its value
            is a list of dictionaries representing the rows.
        out_directory: Directory in which the CSV files are stored.

    Returns:
        bool: True if the output files were written successfully.
    """
    try:
        out_directory.mkdir(parents=True, exist_ok=True)
        for table, rows in data.items():
            if table == "files" or not rows:
                continue
            rows = [{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows]
            fields = list(dict.fromkeys(k for r in rows for k in r))
            with open(out_directory / f"{table}.csv", "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
        return True
    except Exception as e:
        print(f"[error] failed to write output: {e}")
        return False

def main() -> None:
    data = process(IN_DIRECTORY)
    success = write_output(data, OUT_DIRECTORY)
    if not success:
        raise RuntimeError(f"Failed to write the data to {OUT_DIRECTORY}")

if __name__ == "__main__":
    main()