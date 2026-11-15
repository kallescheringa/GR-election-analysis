from pathlib import Path

# Project Root
ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
DATA_PROCESSED = DATA / "processed"
DATA_SOURCES = DATA / "sources.yml"

# Here you should add the names of the municipality which files you want to download
MUNICIPALITY_NAME = "Lansingerland"