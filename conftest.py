import pathlib
import sys

# Ensure the repo root is importable so `loop_verify` and `bench` resolve under pytest.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
