"""
data_loader.py
--------------
Chargement et sauvegarde des données.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATAMARTS_DIR = DATA_DIR / "datamarts"
EXPORTS_DIR = DATA_DIR / "exports"


def load_raw(filename: str = "top5_players_2017_2024.csv") -> pd.DataFrame:
    """
    Charge le dataset brut FBref.
    ⚠️ Format européen : séparateur ; et décimal ,
    """
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Introuvable : {path}")
    return pd.read_csv(path, sep=";", decimal=",", low_memory=False)


def load_processed(filename: str = "top5_players_clean.csv") -> pd.DataFrame:
    """Charge le dataset nettoyé."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Introuvable : {path}. Lance `python build_project.py` d'abord."
        )
    return pd.read_csv(path)


def load_datamart(name: str) -> pd.DataFrame:
    """
    Charge un datamart par son nom court.
    Ex. load_datamart('league_season') -> dm_league_season.csv
    """
    filename = name if name.startswith("dm_") else f"dm_{name}"
    if not filename.endswith(".csv"):
        filename += ".csv"
    path = DATAMARTS_DIR / filename
    if not path.exists():
        available = [p.stem for p in DATAMARTS_DIR.glob("dm_*.csv")]
        raise FileNotFoundError(f"Introuvable : {path}\nDisponibles : {available}")
    return pd.read_csv(path)


def save_processed(df: pd.DataFrame, filename: str = "top5_players_clean.csv") -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / filename
    df.to_csv(path, index=False)
    return path


def save_datamart(df: pd.DataFrame, name: str) -> Path:
    DATAMARTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = name if name.startswith("dm_") else f"dm_{name}"
    if not filename.endswith(".csv"):
        filename += ".csv"
    path = DATAMARTS_DIR / filename
    df.to_csv(path, index=False)
    return path


def save_export(df: pd.DataFrame, filename: str) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / filename
    df.to_csv(path, index=False)
    return path