# Download the paths as specified in config.py
from elections import config

from pathlib import Path
from urllib.parse import urlparse
import argparse
import sys
import zipfile
import requests
import yaml

def get_sources(node, prefix=""):
    sources = []
    if isinstance(node, dict):
        if isinstance(node.get("url"), str):
            sources.append((prefix, node["url"]))
        else:
            for k, v in node.items():
                name = f"{prefix}_{k}" if prefix else str(k)
                sources.extend(get_sources(v, name))
    return sources

def target(name, url):
    suffix = Path(urlparse(url).path).suffix
    return config.DATA_RAW / f"{name}{suffix}"

def download(name, url):
    path = target(name, url)

    if path.exists():
        print(f"skip {path.name} (already exists)")
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


def main():
    with open(config.DATA_SOURCES, encoding="utf-8") as sources_file:
        sources = get_sources(yaml.safe_load(sources_file))

    for name, url in sources:
        download(name, url)

if __name__ == "__main__":
    main()