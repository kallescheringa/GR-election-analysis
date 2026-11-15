# GR-election-analysis

This repository provides tools to load and analyse Dutch municipal council election results (*gemeenteraadsverkiezingen*).

## Downloading the data

The raw election data is not stored in this repository. The download script fetches it from the sources defined in `data/sources.yml` and saves it to `data/raw/`.

### Data source

The 2026 municipal council election results are published by the Kiesraad (the Dutch Electoral Council) as open data on [data.overheid.nl](https://data.overheid.nl/dataset/verkiezingsuitslagen-gemeenteraad-2026) under the CC0 license.

This project uses the EML files, which contain election definitions, candidate lists and polling-station-level results.

Note that the dataset is marked as preliminary, and that the Kiesraad does not provide support for the EML format.

### Configuring sources

Sources are defined in `data/sources.yml`. Each entry containing a `url` key is downloaded. Nested keys are joined with underscores to determine the output filename:

```yaml
gemeenteraad_2026:
  eml:
    url: http://data.overheid.nl/sites/default/files/dataset/09cf04e7-11ac-4b53-a2cc-baccf95e82fd/resources/GR2026_2026_07_03T10.45.zip
```

This entry is saved as `data/raw/gemeenteraad_2026_eml.zip`. The file extension is taken from the URL.

To add another data source, add another entry containing a `url` key.

### Running the download

From the project root, with the virtual environment activated, run:

**PowerShell (Windows):**

```powershell
$env:PYTHONPATH = "src"
python -m elections.download
```

**macOS / Linux:**

```bash
PYTHONPATH=src python -m elections.download
```

Download progress is displayed in MB. Files that already exist are skipped, so the command can safely be run multiple times.

To download the files again, use the `--force` flag:

```bash
python -m elections.download --force
```

## Extracting municipality election data

The downloaded ZIP archive contains election data for all municipalities. The extraction script selects the XML files belonging to the municipality configured in `config.py`.

From the project root, run:

```bash
python -m elections.extract
```

The extracted XML files are saved in `data/raw/lansingerland/`.

## Notes

- `data/raw/` is listed in `.gitignore`, so downloaded and extracted data files are not committed to the repository.
- The original ZIP archive contains data for all municipalities. Only files belonging to the configured municipality are extracted for subsequent analysis.
- The dataset is preliminary and may be updated by the Kiesraad.