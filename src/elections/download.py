# Imports the paths as specified in config.py
from elections import config

from pathlib import Path
from urllib.parse import urlparse
import argparse
import sys
import zipfile
import requests
import yaml

def get_sources(node: Any, prefix: str = "") -> list[tuple[str, str]]:
    """ 
    Finds all URLs in the parsed sources YAML.

    Walks the nested dict recursively. Each entry with a "url" key becomes a 
    (name, url) pair, where name joins the parent keys with underscores,
    e.g. gemeenteraad_2026 -> eml gives gemeente_raad_2026_eml
    """

    sources = []
    if isinstance(node, dict):
        if isinstance(node.get("url"), str):
            sources.append((prefix, node["url"]))
        else:
            for k, v in node.items():
                name = f"{prefix}_{k}" if prefix else str(k)
                sources.extend(get_sources(v, name))
    return sources

def target(name: str, url: str) -> Path:
    """
    This function provides the location where the raw data should be stored.
    It uses the DATA_RAW field from /src/elections/config.py
    """

    suffix = Path(urlparse(url).path).suffix
    return config.DATA_RAW / f"{name}{suffix}"

def download(name: str, url: str, force: bool = False) -> Path:
    """
    Downloads one file into data/raw/ and return its path. 
    
    If the file already exists it skips it, unless force is True. 
    Streams to a .part file first and renames it when complete.
    This way an interrupted download does not mess up the data.
    """
    path = target(name, url)

    if path.exists() and not force:
        print(f"skip {path.name} already exists (use --force to redownload)")
        return path

    config.DATA_RAW.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + ".part")
    print(f"download {name}\n{url}")

    with requests.get(url, stream=True, timeout=60, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        with open(part, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r {done / 1e6:7.1f} / {total / 1e6:.1f} MB", end="")
                else:
                    print(f"\r {done / 1e6:7.1f} MB", end="")
    print()

    part.replace(path)
    print(f"[klaar] {path} ({path.stat().st_size / 1e6:.1f} MB)")
    return path


def main() -> None:
    """
    This function does the following:
        1. Gets the sources from the yml file using the get_sources function
        2. For each URL it tries to download it, and passes the --force flag on to the download function
    """
    parser = argparse.ArgumentParser(description="Parse the command used to download the file")
    parser.add_argument("--force", action="store_true", help="redownload the file incase it exists")
    args = parser.parse_args()

    with open(config.DATA_SOURCES, encoding="utf-8") as sources_file:
        sources = get_sources(yaml.safe_load(sources_file))

    for name, url in sources:
        download(name, url, force=args.force)

if __name__ == "__main__":
    main()