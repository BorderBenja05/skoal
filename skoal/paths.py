from pathlib import Path


SKOLL_DIR = Path(__file__).parent.absolute()
DATA_DIR = SKOLL_DIR.joinpath("data")

CONFIGS_DIR = DATA_DIR.joinpath("configs")
TESS_DIR = DATA_DIR.joinpath('tesselations')
SKYMAPS_DIR = DATA_DIR.joinpath('skymaps')
TESTS_DIR = DATA_DIR.joinpath('test_eventfiles')


