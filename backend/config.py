import os

BASENAME = os.environ.get("REFLEX_BASENAME", "REFLEX")
SAFE_MODE = bool(os.environ.get("REFLEX_SAFE_MODE", "0") == "1")
ML_API = os.environ.get("REFLEX_ML_API", "http://localhost:8000/ml/score")
