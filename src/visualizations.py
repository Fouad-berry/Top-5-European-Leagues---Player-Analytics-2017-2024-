"""
visualizations.py
-----------------
Fonctions de plot réutilisables.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


LEAGUE_COLORS = {
    "Premier League": "#3D195B",
    "La Liga":        "#EE8707",
    "Ligue 1":        "#091C3E",
    "Bundesliga":     "#D3010C",
    "Serie A":        "#008FD7",
}


def set_style():
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 140,
        "savefig.bbox": "tight",
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
    })


def plot_goals_by_league_season(dm_league_season, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    pivot = dm_league_season.pivot(index="SeasonLabel", columns="League", values="total_goals")
    for league in pivot.columns:
        ax.plot(pivot.index, pivot[league], marker="o", linewidth=2.2,
                label=league, color=LEAGUE_COLORS.get(league, "#333"))
    ax.set_title("Total de buts par saison dans chaque ligue")
    ax.set_xlabel("Saison"); ax.set_ylabel("Buts totaux")
    ax.legend(title="Ligue")
    plt.setp(ax.get_xticklabels(), rotation=30)
    return ax


def plot_top_scorers(df, top_n: int = 15, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(11, 7))
    top = df.groupby("Player", observed=True).agg(
        goals=("Goals", "sum")
    ).reset_index().sort_values("goals", ascending=False).head(top_n).sort_values("goals")
    bars = ax.barh(top["Player"], top["goals"],
                   color=sns.color_palette("rocket_r", len(top)), edgecolor="black")
    for bar, val in zip(bars, top["goals"]):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2,
                f"{int(val)}", va="center", fontweight="bold")
    ax.set_title(f"Top {top_n} des buteurs")
    ax.set_xlabel("Buts totaux")
    return ax


def plot_age_by_position(df, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))
    order = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    sns.boxplot(data=df[df["PositionGroup"].isin(order)],
                x="PositionGroup", y="Age", order=order,
                hue="PositionGroup", palette="Set2", legend=False, ax=ax)
    ax.set_title("Distribution de l'âge selon la position")
    ax.set_xlabel("Groupe de position"); ax.set_ylabel("Âge")
    return ax


def plot_xg_vs_goals(df, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 8))
    plot_df = df[(df["QualifiedMinutes"]) & (df["xG"] >= 2)]
    ax.scatter(plot_df["xG"], plot_df["Goals"], alpha=0.25, s=18, color="#2980b9")
    lim = max(plot_df["xG"].max(), plot_df["Goals"].max()) + 2
    ax.plot([0, lim], [0, lim], "r--", label="Buts = xG")
    ax.set_xlabel("xG"); ax.set_ylabel("Buts marqués")
    ax.set_title("xG vs Buts marqués")
    ax.legend()
    return ax


def plot_position_distribution(df, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 7))
    counts = df["PositionGroup"].value_counts()
    colors = sns.color_palette("Set2", len(counts))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
           colors=colors, startangle=90, textprops={"fontweight": "bold"})
    ax.set_title("Répartition des joueurs par position")
    return ax