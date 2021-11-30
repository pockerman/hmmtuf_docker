from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

DEFAULT_ERROR_EXPLANATION = "No error occurred"
INFO = "INFO:"
ERROR = "ERROR:"
DEBUG = "DEBUG:"
WARNING = "WARNING:"
OK = True
DUMMY_ID = -1
INVALID_STR = 'INVALID'
ENABLE_SPADE = True
SPADE_PATH = "%s/SPADE/" % BASE_DIR