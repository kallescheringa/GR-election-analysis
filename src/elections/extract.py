from elections import config

from pathlib import Path
import zipfile 
import argparse

ZIP_PATH = config.DATA_RAW / "gemeenteraad_2026_eml.zip"
OUT_DIRECTORY = config.DATA_RAW / "lansingerland"
MUNICIPALITY = config.MUNICIPALITY_NAME

def extract(delete: bool = False) -> list[Path]:
    """
    Extract XML files belonging to the configured municipality from the ZIP archive.

    Files whose names contain the municipality name are extracted to
    OUT_DIRECTORY. Returns a list of paths to the extracted files.
    """
    OUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    with zipfile.ZipFile(ZIP_PATH , 'r') as zip_ref:
        for name in zip_ref.namelist():
            if MUNICIPALITY in name.lower() and name.lower().endswith(".xml"):
                print(f"\r[extracting] {name}", end="")
                target = OUT_DIRECTORY / Path(name).name
                target.write_bytes(zip_ref.read(name))
                paths.append(target)
    print()

    print(f"all files containing '{MUNICIPALITY}' extracted.", end="")
    if delete:
        ZIP_PATH.unlink()
        print(f" Original ZIP file deleted: {ZIP_PATH}")
    else:
        print()

    return paths

def main() -> None: 
    parser = argparse.ArgumentParser(description="Parser that checks for flags when extracting")
    parser.add_argument("--delete", action="store_true", help="deletes the original zipfile after successful extraction")
    args = parser.parse_args()

    extract(delete=args.delete)

if __name__ == "__main__":
    main()