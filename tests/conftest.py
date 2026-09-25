import sys
from pathlib import Path

MODELES = Path(__file__).resolve().parents[1] / "recherche" / "modeles"
sys.path.insert(0, str(MODELES))
sys.path.insert(0, str(MODELES / "macro"))
