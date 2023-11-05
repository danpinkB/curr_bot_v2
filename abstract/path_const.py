import os
import pathlib

CWD = pathlib.Path(os.getcwd())
ROOT = (pathlib.Path(os.path.dirname(__file__)) / '..').resolve()
TMP_DIR = (ROOT / '.tmp').resolve()
VAR_DIR = (ROOT / '.var').resolve()

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(VAR_DIR, exist_ok=True)
