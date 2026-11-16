"""
Inspect the structure and contents of election XML files.

This module recursively examines XML files in the configured
municipality directory. It counts occurrences of each XML tag
at each depth and prints one example of its attributes and text.
"""

from elections import config

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from typing import Any

DATA_DIRECTORY = config.DATA_RAW / "lansingerland"


def local_name(tag: str) -> str:
    """
    Return an XML tag without its namespace.

    Args:
        tag: The full XML tag, potentially including a namespace.

    Returns:
        The tag name without its namespace.
    """

    return tag.split("}", 1)[-1] if "}" in tag else tag


def inspect_file(file_path: Path) -> None:
    """
    Inspect an XML file and print a summary of its structure.

    Recursively counts occurrences of each tag at each depth
    and stores the first encountered element as an example.

    Args:
        file_path: Path to the XML file to inspect.
    """
    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    tree = ET.parse(file_path)
    root = tree.getroot()

    counts = Counter()
    examples = {}

    def collect(element: Any, depth: int = 0) -> None:
        """
        Recursively collect tag counts and example elements.

        Args:
            element: The current XML element.
            depth: The element's depth in the XML tree.
        """
        name = local_name(element.tag)
        counts[(depth, name)] += 1
        examples.setdefault((depth, name), element)

        for child in element:
            collect(child, depth + 1)

    collect(root)

    for (depth, name), count in sorted(counts.items()):
        element = examples[(depth, name)]

        attributes = element.attrib
        text = (element.text or "").strip()

        if len(text) > 60:
            text = text[:60] + "..."

        print(
            f"{'  ' * depth}{name}"
            f" [{count}x]"
            f" attributes={attributes}"
            f" text={text!r}"
        )


def main() -> None:
    """Inspects all the XML files in the selected data directory"""
    for file_path in sorted(DATA_DIRECTORY.glob("*.xml")):
        inspect_file(file_path)


if __name__ == "__main__":
    main()
