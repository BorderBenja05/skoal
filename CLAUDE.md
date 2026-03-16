# CLAUDE.md — SKOAL Codebase Guide

## Project Overview

**SKOAL** (Scheduling Kilonovae Algebraic Linear) is a Python CLI tool and library for rapid astronomical observation scheduling following gravitational wave (GW) and gamma-ray burst (GRB) events. It processes FERMI and LIGO/Virgo/KAGRA (LVC) VOEvent notices to generate telescope observation schedules in subsecond time.

- **Author**: Benny Border (borderbenja@gmail.com)
- **License**: MIT with attribution requirement (papers using this software must credit the author)
- **Version**: 0.421
- **Python**: 3.6+

---

## Repository Structure

```
skoal/
├── README.md                    # User documentation
├── LICENSE                      # MIT license
├── setup.py                     # Package config (version, deps, entry point)
├── __init__.py
└── skoal/                       # Main package
    ├── main.py                  # CLI entry point and workflow orchestrator
    ├── GCN_utils.py             # VOEvent parsing and GraceDB access
    ├── lvc_handler.py           # LVC/GW skymap processing
    ├── Fermi_handler.py         # FERMI GBM notice processing
    ├── Multiscope_handler.py    # Multi-telescope schedule splitting
    ├── scheduler_utilities.py  # Observability filtering and target clustering
    ├── faster_fieldfinder.py    # Optimized O(n) field-coordinate mapping
    ├── field_from_coords.py     # Alternative field finder implementation
    ├── tesselation_generator.py # Sky tessellation generation
    ├── moc.py                   # Multi-Order Coverage (MOC) map utilities
    ├── plot_tiles.py            # Visualization utilities
    ├── config_utils.py          # Interactive telescope config generation
    ├── paths.py                 # Path constants (imported everywhere)
    ├── moc_list.pkl             # Pre-computed MOC objects (~7.7 MB binary)
    └── data/
        ├── configs/             # Telescope configuration INI files
        │   ├── default.cfg      # Default settings
        │   ├── RASA11.cfg
        │   ├── ZTF.cfg
        │   ├── Bennyscope.cfg
        │   └── Borderscope.cfg
        ├── tesselations/        # Pre-computed sky tessellations (.tess files)
        ├── skymaps/             # Downloaded GW/FERMI FITS skymap files
        └── test_eventfiles/     # Test VOEvent XML files (FERMI and LVC)
```

---

## Key Modules

### `main.py` — Entry Point
Orchestrates the full scheduling workflow:
1. Parse CLI arguments
2. Identify event type (LVC vs FERMI) from VOEvent
3. Load or interactively create telescope config
4. Generate tessellation if missing
5. Process skymap (LVC) or coordinates (FERMI)
6. Filter targets for observability
7. Split schedule across multiple telescopes
8. Write output files

### `GCN_utils.py` — VOEvent & GraceDB Utilities
- `get_skymap(event_id)` — fetch FITS skymap from GraceDB
- `download_from_url(url, path)` — download FITS files
- `get_ivorn(voevent_path)` — detect notice type (FERMI or LVC)
- `getEvent(voevent_path)` — extract GraceDB event ID from XML
- `getFERMICoordinates(voevent_path)` — parse RA/Dec/error from FERMI notice
- `area(voevent_path, percent)` — calculate sky area of confidence region

### `lvc_handler.py` — LVC Gravitational Wave Processing
- `generate_fields_from_skymap(tess_path, skymap_path, minObsChance)` — maps HEALPix probability to tessellated fields; returns ranked `(field_ids, probabilities)` filtered above `minObsChance` threshold

### `Fermi_handler.py` — FERMI GBM Processing
- `Fermi_handle(ra, dec, error, tess_path)` — finds tessellation fields within the FERMI error circle using BallTree spatial indexing

### `faster_fieldfinder.py` — Core Algorithm
- `field_from_coords(ra_list, dec_list, tess_path, fov_ra, fov_dec)` — the key algorithmic innovation: maps sky coordinates to tessellated field IDs using **algebraic (O(n)) reverse lookup** instead of tree-based searches

### `scheduler_utilities.py` — Observability & Clustering
- `filter_for_visibility(targets, telescope_config, obs_time)` — applies astroplan constraints: airmass, moon separation, altitude (≥10°), twilight
- `separate_targets_into_clusters(targets, n)` — k-means clustering for even sky distribution across N telescopes
- `separate_targets_evenly(targets, n)` — round-robin distribution fallback

### `moc.py` — MOC Coverage Maps
- `observable_area(tess_path, fov_ra, fov_dec)` — compute observable sky coverage as MOC
- `moc_maker(tess_path, fov_ra, fov_dec)` — create MOC from tessellation
- `get_corners(ra, dec, fov_ra, fov_dec)` — field corner coordinates accounting for sky curvature
- Pre-computed MOC objects cached in `moc_list.pkl`

### `tesselation_generator.py`
- `rect_tess_maker(telescope_config)` — generates rectangular sky tessellation for a given FOV, accounting for declination-dependent RA scaling

### `config_utils.py`
- `make_config_file(telescope_name)` — interactively prompts for telescope parameters and writes a new `.cfg` file

### `paths.py`
- Defines path constants: `SKOAL_DIR`, `DATA_DIR`, `CONFIGS_DIR`, `TESS_DIR`, `SKYMAPS_DIR`, `TESTS_DIR`
- Creates data directories on import — **always imported first in every module**

---

## Configuration System

Telescope configs use INI format via `configparser`. Example:

```ini
[telescope]
name = RASA11
lat = 45.0
lon = -93.1
elevation = 1000
rafov = 3.2
decfov = 2.1
tileScale = 0.98

[defaults]
minObsChance = 0.90
horizon = 10
default_output_path = SKOAL_schedules
```

Key settings:
- `tileScale` — fraction of FOV used for tile overlap avoidance (default 0.98)
- `minObsChance` — cumulative probability threshold for LVC skymaps (default 0.90)
- `horizon` — minimum altitude in degrees (default 10)

If a telescope config doesn't exist, `main.py` calls `config_utils.make_config_file()` interactively.

---

## Development Workflows

### Installation (development)
```bash
pip install -e .
```

### Running
```bash
# From a GraceDB event ID
skoal -t RASA11 -e S240609c

# From a local VOEvent file
skoal -t RASA11 -voe skoal/data/test_eventfiles/gcn.classic.voevent.LVC_INITIAL_7486.xml

# Multi-telescope scheduling (split across 7 scopes)
skoal -t RASA11 -e S240609c -multiscopes 7

# Custom output path
skoal -t RASA11 -e S240609c -o ./my_schedules

# Skip observability filtering (output all targets)
skoal -t RASA11 -e S240609c -alltargets
```

### Manual Testing
No automated test suite. Test using bundled data:
```bash
# Test with FERMI notice
skoal -t RASA11 -voe skoal/data/test_eventfiles/gcn.classic.voevent.FERMI_GBM_POS_TEST_4581.xml

# Test with LVC notice
skoal -t RASA11 -voe skoal/data/test_eventfiles/gcn.classic.voevent.LVC_INITIAL_7486.xml
```

---

## Code Conventions

### Naming
- **Functions**: mixed — snake_case for most (`field_from_coords`, `get_skymap`), camelCase for some older functions (`getFERMICoordinates`, `getEvent`)
- **Constants**: UPPERCASE (`SKOAL_DIR`, `DATA_DIR`)
- **Variables**: snake_case (`field_ids`, `sky_coordinates`, `rafov`)

### Imports
Standard order:
1. Standard library (`os`, `sys`, `pathlib`, `xml`)
2. Astronomy (`astropy`, `astroplan`, `ligo.gracedb`, `mocpy`, `healpy`)
3. Scientific (`numpy as np`, `scipy`, `sklearn`)
4. Local (`from skoal.paths import *`, then other skoal modules)

### Array Operations
Heavy use of NumPy vectorized operations — avoid Python loops over sky coordinates.

### Coordinate Handling
- Sky coordinates use `astropy.coordinates.SkyCoord`
- Angles use `astropy.units` (`u.deg`, `u.rad`)
- HEALPix operations use `astropy_healpix`
- Spatial BallTree searches use `sklearn.neighbors.BallTree` with haversine metric

### Output Format
Schedule files are plain-text tables written via `Multiscope_handler.save_table_to_file()`. Each row: `field_id  RA  Dec  probability`.

---

## Key Data Formats

| Format | Purpose | Notes |
|--------|---------|-------|
| `.cfg` | Telescope config | INI format, `configparser` |
| `.tess` | Sky tessellation | Text: `field_id RA Dec` per line |
| `.fits` / `.fits,1` | GW skymaps | HEALPix multi-order FITS |
| `.xml` (VOEvent) | GCN notices | FERMI or LVC event XML |
| `.pkl` | Pre-computed MOC | Binary pickle of MOC objects |

---

## Dependencies

Core:
- `astropy`, `astropy-healpix`, `astroplan` — astronomy
- `ligo-gracedb>=2.10.0` — GW event database
- `mocpy` — Multi-Order Coverage maps
- `numpy`, `scipy`, `scikit-learn` — numerical/ML
- `lxml`, `requests`, `urllib3>=2.1.0` — data I/O

Optional (visualization only):
- `matplotlib`, `healpy` — used in `plot_tiles.py`

---

## Important Notes for AI Assistants

1. **No test suite**: There is no pytest or unittest framework. Validate changes manually using test event files in `skoal/data/test_eventfiles/`.

2. **`paths.py` must be imported first**: Every module imports `from skoal.paths import *`. This creates required data directories on import. Do not remove or defer this import.

3. **`moc_list.pkl` is binary**: Do not attempt to read or modify this file as text. It is a pre-computed cache of MOC objects.

4. **Algorithm sensitivity**: `faster_fieldfinder.py` implements the core O(n) algebraic lookup that makes the tool fast. Changes here can break performance guarantees.

5. **Mixed naming conventions**: The codebase has inconsistent snake_case vs camelCase. Match the existing style in whichever file you are editing.

6. **No CI/CD**: There is no automated testing pipeline. Changes are manually verified.

7. **Tessellation files**: `.tess` files in `skoal/data/tesselations/` are auto-generated on first run for a telescope. Do not delete them without regenerating.

8. **Attribution**: The MIT license has a custom clause — any paper using this code or its algorithms must credit Benjamin Border. Do not remove this from LICENSE.
