"""Shared XML helpers used by all parsefiles"""

from typing import Any
from pathlib import Path
import xml.etree.ElementTree as ET


def _local(name: Any) -> Any:
    """Splits the namespace from the element"""
    return name.rsplit("}", 1)[-1] if isinstance(name, str) else name


def load_xml(path: Path) -> ET.Element:
    """
    Parses the file and returns the document element (with the EML element removed).
    Namespaces are stripped from tags to improve readibility and lookupibility. 
    Original file is never changed.
    """
    root = ET.parse(path).getroot()
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        element.tag = _local(element.tag)
        attrs = {_local(k): v for k, v in element.attrib.items()}
        element.attrib.clear()
        element.attrib.update(attrs)
    if root.tag == "EML" and len(root):
        for child in root:
            if child.tag not in {
                "TransactionId", 
                "IssueDate", 
                "CreationDateTime", 
                "ManagingAuthority", 
                "CanonicalizationMethod"
            }:
                return child
    return root

def text(element, path):
    """
    Extract and return the text of a XML child element.

    Returns:
        str | None: The text if the element exists and contains non-whitespace text. Else None.
    """
    found = element.find(path)

    if found is None or found.text is None:
        return None

    return found.text.strip()

def to_int(value, context):
    try:
        return int(str(value).strip())
    except:
        raise ValueError(f"Expected Integer for {context}, got {value!r}")

def to_bool(value):
    return str(value).strip().lower() in ("yes", "true", "1", "ja")

def iter_selection(block):
    """Yield (kind, affiliation_id, candidate_id, selection_element) in
    document order.
 
    In EML-NL a candidate Selection normally carries no affiliation id: it
    belongs to the most recent affiliation Selection before it. An explicit
    AffiliationIdentifier on the Selection takes precedence if present."""
    current_affiliation = None
    for sel in block.iter("Selection"): 
        affiliation = sel.find("AffiliationIdentifier")
        if affiliation is not None:
            current_affiliation = affiliation.get("Id")
        candidate = sel.find("Candidate")
        if candidate is None:
            yield "affiliation", current_affiliation, None, sel
        else:
            c_id = candidate.find("CandidateIdentifier").get("Id")
            yield "candidate", current_affiliation, (c_id if c_id is not None else None), sel