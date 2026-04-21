"""
datamarts.py
------------
Construction des 7 datamarts analytiques.
"""

import pandas as pd


def build_global_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """KPIs globaux — 1 seule ligne — pour les scorecards Looker."""
    return pd.DataFrame([{
        "total_records": len(df),
        "unique_players": df["Player"].nunique(),
        "unique_teams": df["Team"].nunique(),
        "unique_nations": df["Nation"].nunique(),
        "seasons_covered": df["SeasonLabel"].nunique(),
        "leagues_covered": df["League"].nunique(),
        "total_goals": int(df["Goals"].sum()),
        "total_assists": int(df["Assists"].sum()),
        "total_minutes": int(df["Minutes"].sum()),
        "avg_age": round(df["Age"].mean(), 2),
        "avg_goals_per_player_season": round(df["Goals"].mean(), 2),
        "avg_xG_per_player_season": round(df["xG"].mean(), 2),
    }])


def build_league_season(df: pd.DataFrame) -> pd.DataFrame:
    """Stats agrégées par ligue × saison."""
    return df.groupby(["League", "SeasonLabel"], observed=True).agg(
        players=("Player", "nunique"),
        teams=("Team", "nunique"),
        total_goals=("Goals", "sum"),
        total_assists=("Assists", "sum"),
        total_xG=("xG", "sum"),
        avg_age=("Age", "mean"),
        avg_pass_completion=("PassCompletionPct", "mean"),
    ).round(2).reset_index()


def build_top_scorers_by_season(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top N buteurs par saison."""
    return (
        df.sort_values(["SeasonLabel", "Goals"], ascending=[True, False])
          .groupby("SeasonLabel").head(top_n)
          [["SeasonLabel", "League", "Team", "Player", "PositionGroup", "Age",
            "Goals", "Assists", "xG", "ShotsOnTarget", "Minutes"]]
          .reset_index(drop=True)
    )


def build_team_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Performance agrégée par équipe (toutes saisons confondues)."""
    out = df.groupby(["League", "Team"], observed=True).agg(
        seasons_present=("SeasonLabel", "nunique"),
        total_goals=("Goals", "sum"),
        total_assists=("Assists", "sum"),
        total_xG=("xG", "sum"),
        avg_age=("Age", "mean"),
        players_used=("Player", "nunique"),
    ).round(2).reset_index()
    out["goals_per_season"] = (out["total_goals"] / out["seasons_present"]).round(2)
    return out


def build_position_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Profil statistique moyen par groupe de position."""
    return df.groupby("PositionGroup", observed=True).agg(
        n_records=("Player", "count"),
        avg_age=("Age", "mean"),
        avg_minutes=("Minutes", "mean"),
        avg_goals=("Goals", "mean"),
        avg_assists=("Assists", "mean"),
        avg_xG=("xG", "mean"),
        avg_progressive_passes=("ProgressivePasses", "mean"),
        avg_tackles=("Tackles", "mean"),
        avg_interceptions=("Interceptions", "mean"),
        avg_aerial_won_pct=("AerialDuelsWonPct", "mean"),
    ).round(2).reset_index()


def build_xg_finishing(df: pd.DataFrame, min_xg: float = 3.0) -> pd.DataFrame:
    """Joueurs qui sur/sous-performent leur xG (finition)."""
    qualified = df[(df["QualifiedMinutes"]) & (df["xG"] >= min_xg)]
    return qualified[
        ["SeasonLabel", "League", "Team", "Player", "PositionGroup",
         "Goals", "xG", "xGDifference", "Shots", "ShotsOnTarget", "Minutes"]
    ].sort_values("xGDifference", ascending=False).reset_index(drop=True)


def build_top_nations(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    """Top N nations par minutes totales jouées."""
    out = df.groupby("Nation", observed=True).agg(
        players=("Player", "nunique"),
        appearances=("Player", "count"),
        total_goals=("Goals", "sum"),
        total_minutes=("Minutes", "sum"),
    ).reset_index().sort_values("total_minutes", ascending=False).head(top_n)
    out["goals_per_player"] = (out["total_goals"] / out["players"]).round(2)
    return out


def build_all(df: pd.DataFrame) -> dict:
    """Construit les 7 datamarts d'un coup."""
    return {
        "global_kpis": build_global_kpis(df),
        "league_season": build_league_season(df),
        "top_scorers_by_season": build_top_scorers_by_season(df),
        "team_performance": build_team_performance(df),
        "position_profile": build_position_profile(df),
        "xg_finishing": build_xg_finishing(df),
        "top_nations": build_top_nations(df),
    }