from pathlib import Path
import os



SKOAL_DIR = Path(__file__).parent.absolute()
DATA_DIR = SKOAL_DIR.joinpath("data")

CONFIGS_DIR = DATA_DIR.joinpath("configs")
TESS_DIR = DATA_DIR.joinpath('tesselations')
SKYMAPS_DIR = DATA_DIR.joinpath('skymaps')
TESTS_DIR = DATA_DIR.joinpath('test_eventfiles')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.exists(CONFIGS_DIR):
    os.mkdir(CONFIGS_DIR)
if not os.path.exists(TESS_DIR):
    os.mkdir(TESS_DIR)
if not os.path.exists(SKYMAPS_DIR):
    os.mkdir(SKYMAPS_DIR)



