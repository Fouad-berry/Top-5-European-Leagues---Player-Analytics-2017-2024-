"""
preprocessing.py
----------------
Nettoyage et feature engineering pour le dataset FBref.
"""

import pandas as pd
import numpy as np

# ============================================================
# Renommage des colonnes principales
# ============================================================
RENAME_MAP = {
    "league": "League",
    "season": "Season",
    "team": "Team",
    "player": "Player",
    "nation_": "Nation",
    "pos_": "Position",
    "age_": "Age",
    "born_": "Born",
    "Playing Time_MP": "MatchesPlayed",
    "Playing Time_Starts": "Starts",
    "Playing Time_Min": "Minutes",
    "Playing Time_90s": "Nineties",
    "Performance_Gls": "Goals",
    "Performance_Ast": "Assists",
    "Performance_G+A": "GoalsPlusAssists",
    "Performance_G-PK": "GoalsNonPenalty",
    "Performance_PK": "PenaltiesScored",
    "Performance_PKatt": "PenaltiesAttempted",
    "Performance_CrdY": "YellowCards",
    "Performance_CrdR": "RedCards",
    "Expected_xG": "xG",
    "Expected_npxG": "npxG",
    "Expected_xAG": "xAG",
    "Progression_PrgC": "ProgressiveCarries",
    "Progression_PrgP": "ProgressivePasses",
    "Progression_PrgR": "ProgressivePassesReceived",
    "Per 90 Minutes_Gls": "GoalsPer90",
    "Per 90 Minutes_Ast": "AssistsPer90",
    "Per 90 Minutes_G+A": "GoalsPlusAssistsPer90",
    "Per 90 Minutes_xG": "xGPer90",
    "Per 90 Minutes_xAG": "xAGPer90",
    "Standard_Sh": "Shots",
    "Standard_SoT": "ShotsOnTarget",
    "Standard_SoT%": "ShotsOnTargetPct",
    "Total_Cmp%": "PassCompletionPct",
    "Tackles_Tkl": "Tackles",
    "Tackles_TklW": "TacklesWon",
    "Int_": "Interceptions",
    "Clr_": "Clearances",
    "Take-Ons_Att": "TakeOnsAttempted",
    "Take-Ons_Succ": "TakeOnsSuccessful",
    "Take-Ons_Succ%": "TakeOnsSuccessPct",
    "Aerial Duels_Won": "AerialDuelsWon",
    "Aerial Duels_Won%": "AerialDuelsWonPct",
}

POSITION_GROUP_MAP = {
    "GK": "Goalkeeper",
    "DF": "Defender",
    "MF": "Midfielder",
    "FW": "Forward",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Applique le renommage des colonnes principales."""
    return df.rename(columns=RENAME_MAP)


def clean_league_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enlève les préfixes pays (ENG-, ESP-, FRA-, GER-, ITA-).
    ENG-Premier League -> Premier League
    """
    df = df.copy()
    for prefix in ["ENG-", "ESP-", "FRA-", "GER-", "ITA-"]:
        df["League"] = df["League"].str.replace(prefix, "", regex=False)
    df["League"] = df["League"].str.strip()
    return df


def add_season_label(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme la saison numérique en label lisible : 1718 -> 2017-18."""
    df = df.copy()
    def _label(s):
        s = str(int(s)).zfill(4)
        return f"20{s[:2]}-{s[2:]}"
    df["SeasonLabel"] = df["Season"].apply(_label)
    return df


def add_position_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute PrimaryPosition (première pos listée) et PositionGroup."""
    df = df.copy()
    df["PrimaryPosition"] = df["Position"].str.split(",").str[0]
    df["PositionGroup"] = df["PrimaryPosition"].map(POSITION_GROUP_MAP).fillna("Other")
    return df


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["AgeGroup"] = pd.cut(
        df["Age"], bins=[13, 20, 24, 28, 32, 45],
        labels=["U21", "21-24", "25-28", "29-32", "33+"]
    )
    return df


def add_xg_features(df: pd.DataFrame) -> pd.DataFrame:
    """Indicateurs de finition : écart buts / xG."""
    df = df.copy()
    df["xGDifference"] = df["Goals"] - df["xG"]
    df["xGDifferencePer90"] = np.where(
        df["Nineties"] > 0, df["xGDifference"] / df["Nineties"], np.nan
    )
    df["GoalsPerShot"] = np.where(df["Shots"] > 0, df["Goals"] / df["Shots"], np.nan)
    return df


def add_qualification_flag(df: pd.DataFrame, min_minutes: int = 450) -> pd.DataFrame:
    """
    Flag indiquant si le joueur a assez joué pour que les stats par 90'
    soient fiables. 450 minutes = 5 matchs complets.
    """
    df = df.copy()
    df["QualifiedMinutes"] = df["Minutes"] >= min_minutes
    return df


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline complet appliqué au CSV brut."""
    df = rename_columns(df)
    df = clean_league_names(df)
    df = add_season_label(df)
    df = add_position_features(df)
    df = add_age_group(df)
    df = add_xg_features(df)
    df = add_qualification_flag(df)
    return df