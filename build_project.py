"""
build_project.py
----------------
Script maître — génère tous les livrables :
  1. Dataset nettoyé (data/processed/)
  2. 7 datamarts analytiques (data/datamarts/)
  3. Exports Looker Studio (data/exports/)
  4. 10 figures PNG (images/figures/)

Usage :
    python build_project.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# Configuration
# ============================================================
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "top5_players_2017_2024.csv"
PROCESSED = ROOT / "data" / "processed"
DATAMARTS = ROOT / "data" / "datamarts"
EXPORTS = ROOT / "data" / "exports"
FIGURES = ROOT / "images" / "figures"

for d in [PROCESSED, DATAMARTS, EXPORTS, FIGURES]:
    d.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "savefig.bbox": "tight",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

LEAGUE_COLORS = {
    "Premier League": "#3D195B",  # violet PL
    "La Liga":        "#EE8707",  # orange LaLiga
    "Ligue 1":        "#091C3E",  # bleu Ligue 1
    "Bundesliga":     "#D3010C",  # rouge Bundesliga
    "Serie A":        "#008FD7",  # bleu Serie A
}

# ============================================================
# 1. LOAD + CLEAN + FEATURE ENGINEERING
# ============================================================
print("▶ [1/4] Chargement et nettoyage…")
df = pd.read_csv(RAW, sep=";", decimal=",", low_memory=False)

# --- Renommage colonnes : on garde les principales et on les simplifie ---
rename_map = {
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
df = df.rename(columns=rename_map)

# --- Nettoyer les noms de ligue ---
df["League"] = df["League"].str.replace("ENG-", "").str.replace("ESP-", "") \
                           .str.replace("FRA-", "").str.replace("GER-", "") \
                           .str.replace("ITA-", "").str.strip()

# --- Transformer la saison en format lisible : 1718 -> "2017-18" ---
def season_to_label(s):
    s = str(int(s)).zfill(4)
    y1, y2 = s[:2], s[2:]
    # préfixe : 17-24 => 2017-2024, 25 => 2025
    return f"20{y1}-{y2}"
df["SeasonLabel"] = df["Season"].apply(season_to_label)

# --- Position simplifiée : on prend la première position listée ---
df["PrimaryPosition"] = df["Position"].str.split(",").str[0]

# --- Groupe de position ---
pos_group_map = {"GK": "Goalkeeper", "DF": "Defender", "MF": "Midfielder", "FW": "Forward"}
df["PositionGroup"] = df["PrimaryPosition"].map(pos_group_map).fillna("Other")

# --- Tranche d'âge ---
df["AgeGroup"] = pd.cut(df["Age"], bins=[13, 20, 24, 28, 32, 45],
                        labels=["U21", "21-24", "25-28", "29-32", "33+"])

# --- Indicateurs dérivés (seulement si Minutes > 0 et Shots > 0) ---
df["GoalsPerShot"] = np.where(df["Shots"] > 0, df["Goals"] / df["Shots"], np.nan)
df["xGDifference"] = df["Goals"] - df["xG"]  # sur/sous-performance finition
df["xGDifferencePer90"] = np.where(df["Nineties"] > 0,
                                   df["xGDifference"] / df["Nineties"], np.nan)
df["MinutesShare"] = df["Minutes"] / (38 * 90)  # part de minutes sur une saison "parfaite"

# Filtre minimum de 450 min pour les analyses par 90' (5 matchs complets)
df["QualifiedMinutes"] = df["Minutes"] >= 450

df.to_csv(PROCESSED / "top5_players_clean.csv", index=False)
print(f"   ✓ {len(df)} lignes × {df.shape[1]} colonnes — {PROCESSED / 'top5_players_clean.csv'}")

# ============================================================
# 2. DATAMARTS
# ============================================================
print("▶ [2/4] Construction des datamarts…")

# --- DM 1 : KPIs globaux ---
dm_kpi = pd.DataFrame([{
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
dm_kpi.to_csv(DATAMARTS / "dm_global_kpis.csv", index=False)

# --- DM 2 : Stats par ligue × saison ---
dm_league_season = df.groupby(["League", "SeasonLabel"], observed=True).agg(
    players=("Player", "nunique"),
    teams=("Team", "nunique"),
    total_goals=("Goals", "sum"),
    total_assists=("Assists", "sum"),
    total_xG=("xG", "sum"),
    avg_age=("Age", "mean"),
    avg_pass_completion=("PassCompletionPct", "mean"),
).round(2).reset_index()
dm_league_season.to_csv(DATAMARTS / "dm_league_season.csv", index=False)

# --- DM 3 : Top scorers par saison ---
dm_top_scorers = df.sort_values(["SeasonLabel", "Goals"], ascending=[True, False]) \
                    .groupby("SeasonLabel").head(10)[
    ["SeasonLabel", "League", "Team", "Player", "PositionGroup", "Age",
     "Goals", "Assists", "xG", "ShotsOnTarget", "Minutes"]
].reset_index(drop=True)
dm_top_scorers.to_csv(DATAMARTS / "dm_top_scorers_by_season.csv", index=False)

# --- DM 4 : Performance par équipe (toutes saisons confondues) ---
dm_team = df.groupby(["League", "Team"], observed=True).agg(
    seasons_present=("SeasonLabel", "nunique"),
    total_goals=("Goals", "sum"),
    total_assists=("Assists", "sum"),
    total_xG=("xG", "sum"),
    avg_age=("Age", "mean"),
    players_used=("Player", "nunique"),
).round(2).reset_index()
dm_team["goals_per_season"] = (dm_team["total_goals"] / dm_team["seasons_present"]).round(2)
dm_team.to_csv(DATAMARTS / "dm_team_performance.csv", index=False)

# --- DM 5 : Stats par position ---
dm_position = df.groupby("PositionGroup", observed=True).agg(
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
dm_position.to_csv(DATAMARTS / "dm_position_profile.csv", index=False)

# --- DM 6 : xG vs Goals (finishers / sous-performeurs) ---
# On garde uniquement les joueurs avec assez de temps de jeu et de tirs
qualified = df[(df["QualifiedMinutes"]) & (df["xG"] >= 3)].copy()
dm_finishing = qualified[
    ["SeasonLabel", "League", "Team", "Player", "PositionGroup",
     "Goals", "xG", "xGDifference", "Shots", "ShotsOnTarget", "Minutes"]
].sort_values("xGDifference", ascending=False).reset_index(drop=True)
dm_finishing.to_csv(DATAMARTS / "dm_xg_finishing.csv", index=False)

# --- DM 7 : Top nations par minutes jouées ---
dm_nations = df.groupby("Nation", observed=True).agg(
    players=("Player", "nunique"),
    appearances=("Player", "count"),
    total_goals=("Goals", "sum"),
    total_minutes=("Minutes", "sum"),
).reset_index().sort_values("total_minutes", ascending=False).head(25)
dm_nations["goals_per_player"] = (dm_nations["total_goals"] / dm_nations["players"]).round(2)
dm_nations.to_csv(DATAMARTS / "dm_top_nations.csv", index=False)

print(f"   ✓ 7 datamarts générés dans {DATAMARTS}/")

# ============================================================
# 3. EXPORTS LOOKER
# ============================================================
# Le dataset complet est trop gros pour un upload Looker confortable,
# on exporte donc une version allégée (colonnes utiles) + les datamarts.
core_cols = [
    "League", "Season", "SeasonLabel", "Team", "Player", "Nation",
    "PrimaryPosition", "PositionGroup", "Age", "AgeGroup",
    "MatchesPlayed", "Starts", "Minutes", "Nineties",
    "Goals", "Assists", "GoalsPlusAssists", "xG", "xAG",
    "Shots", "ShotsOnTarget", "ShotsOnTargetPct",
    "YellowCards", "RedCards",
    "GoalsPer90", "AssistsPer90", "GoalsPlusAssistsPer90", "xGPer90", "xAGPer90",
    "PassCompletionPct", "ProgressivePasses", "ProgressiveCarries",
    "Tackles", "Interceptions", "Clearances",
    "TakeOnsAttempted", "TakeOnsSuccessful", "TakeOnsSuccessPct",
    "AerialDuelsWon", "AerialDuelsWonPct",
    "xGDifference", "xGDifferencePer90", "QualifiedMinutes",
]
core_cols = [c for c in core_cols if c in df.columns]
df[core_cols].to_csv(EXPORTS / "main_dataset.csv", index=False)
dm_league_season.to_csv(EXPORTS / "by_league_season.csv", index=False)
dm_top_scorers.to_csv(EXPORTS / "top_scorers.csv", index=False)
dm_team.to_csv(EXPORTS / "by_team.csv", index=False)
dm_position.to_csv(EXPORTS / "by_position.csv", index=False)
dm_finishing.to_csv(EXPORTS / "xg_finishing.csv", index=False)
dm_kpi.to_csv(EXPORTS / "global_kpis.csv", index=False)
print(f"   ✓ Exports Looker dans {EXPORTS}/")

# ============================================================
# 4. FIGURES
# ============================================================
print("▶ [3/4] Génération des figures…")

# --- Fig 1 : buts totaux par ligue et saison ---
fig, ax = plt.subplots(figsize=(12, 6))
pivot = dm_league_season.pivot(index="SeasonLabel", columns="League", values="total_goals")
for league in pivot.columns:
    ax.plot(pivot.index, pivot[league], marker="o", linewidth=2.2,
            label=league, color=LEAGUE_COLORS.get(league, "#333"))
ax.set_title("Total de buts par saison dans chaque grande ligue")
ax.set_xlabel("Saison"); ax.set_ylabel("Buts totaux")
ax.legend(title="Ligue", loc="best")
plt.xticks(rotation=30)
plt.savefig(FIGURES / "01_goals_by_league_season.png")
plt.close()

# --- Fig 2 : top 15 buteurs toutes saisons confondues ---
fig, ax = plt.subplots(figsize=(11, 7))
top_scorers_all = df.groupby("Player", observed=True).agg(
    goals=("Goals", "sum"),
    nineties=("Nineties", "sum"),
).reset_index().sort_values("goals", ascending=False).head(15).sort_values("goals")
bars = ax.barh(top_scorers_all["Player"], top_scorers_all["goals"],
               color=sns.color_palette("rocket_r", len(top_scorers_all)), edgecolor="black")
for bar, val in zip(bars, top_scorers_all["goals"]):
    ax.text(val + 2, bar.get_y() + bar.get_height()/2, f"{int(val)}",
            va="center", fontweight="bold")
ax.set_title("Top 15 des buteurs du Top 5 européen (2017-2024)")
ax.set_xlabel("Buts totaux")
plt.savefig(FIGURES / "02_top15_scorers_all_time.png")
plt.close()

# --- Fig 3 : distribution des âges par position ---
fig, ax = plt.subplots(figsize=(10, 6))
order = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
sns.boxplot(data=df[df["PositionGroup"].isin(order)], x="PositionGroup", y="Age",
            order=order, palette="Set2", ax=ax)
ax.set_title("Distribution de l'âge selon la position")
ax.set_xlabel("Groupe de position"); ax.set_ylabel("Âge (années)")
plt.savefig(FIGURES / "03_age_by_position.png")
plt.close()

# --- Fig 4 : xG vs Goals scatter (finition) ---
plot_df = df[(df["QualifiedMinutes"]) & (df["xG"] >= 2)].copy()
fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(plot_df["xG"], plot_df["Goals"], alpha=0.25, s=18, color="#2980b9")
lim = max(plot_df["xG"].max(), plot_df["Goals"].max()) + 2
ax.plot([0, lim], [0, lim], "r--", label="Buts = xG (finition neutre)")
# Annoter les 6 plus grosses sur-performances
top_over = plot_df.nlargest(6, "xGDifference")
for _, r in top_over.iterrows():
    ax.annotate(f"{r['Player']} ({r['SeasonLabel']})",
                xy=(r["xG"], r["Goals"]),
                xytext=(r["xG"] + 1.5, r["Goals"] + 0.8),
                fontsize=8, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="gray", lw=0.6))
ax.set_xlabel("xG (buts attendus)"); ax.set_ylabel("Buts marqués")
ax.set_title("xG vs Buts marqués — qui sur-performe ?")
ax.legend()
plt.savefig(FIGURES / "04_xg_vs_goals.png")
plt.close()

# --- Fig 5 : nombre de joueurs par ligue × saison ---
fig, ax = plt.subplots(figsize=(12, 6))
pivot_players = dm_league_season.pivot(index="SeasonLabel", columns="League", values="players")
pivot_players.plot(kind="bar", ax=ax, edgecolor="black",
                    color=[LEAGUE_COLORS.get(c, "#333") for c in pivot_players.columns])
ax.set_title("Nombre de joueurs uniques par ligue et saison")
ax.set_xlabel("Saison"); ax.set_ylabel("Nombre de joueurs")
ax.legend(title="Ligue")
plt.xticks(rotation=30)
plt.savefig(FIGURES / "05_players_by_league_season.png")
plt.close()

# --- Fig 6 : répartition des positions ---
fig, ax = plt.subplots(figsize=(8, 7))
pos_counts = df["PositionGroup"].value_counts()
colors = sns.color_palette("Set2", len(pos_counts))
wedges, _, autotexts = ax.pie(pos_counts.values, labels=pos_counts.index,
                              autopct="%1.1f%%", colors=colors, startangle=90,
                              textprops={"fontweight": "bold"})
ax.set_title("Répartition des joueurs par position")
plt.savefig(FIGURES / "06_position_distribution.png")
plt.close()

# --- Fig 7 : moyennes par ligue (buts, passes D, xG) ---
fig, ax = plt.subplots(figsize=(11, 6))
league_avg = df.groupby("League", observed=True).agg(
    goals=("Goals", "mean"),
    assists=("Assists", "mean"),
    xG=("xG", "mean"),
).round(2)
league_avg = league_avg.reindex(["Premier League", "La Liga", "Ligue 1", "Bundesliga", "Serie A"])
x = np.arange(len(league_avg))
w = 0.27
ax.bar(x - w, league_avg["goals"], w, label="Buts", color="#e74c3c", edgecolor="black")
ax.bar(x,     league_avg["assists"], w, label="Passes D.", color="#3498db", edgecolor="black")
ax.bar(x + w, league_avg["xG"], w, label="xG", color="#2ecc71", edgecolor="black")
ax.set_xticks(x); ax.set_xticklabels(league_avg.index)
ax.set_title("Moyennes par joueur selon la ligue")
ax.set_ylabel("Moyenne par joueur par saison")
ax.legend()
plt.savefig(FIGURES / "07_averages_by_league.png")
plt.close()

# --- Fig 8 : top 10 équipes par buts totaux ---
fig, ax = plt.subplots(figsize=(11, 7))
top_teams = dm_team.sort_values("total_goals", ascending=False).head(10).sort_values("total_goals")
colors_t = [LEAGUE_COLORS.get(l, "#888") for l in top_teams["League"]]
bars = ax.barh(top_teams["Team"], top_teams["total_goals"],
               color=colors_t, edgecolor="black")
for bar, val, league in zip(bars, top_teams["total_goals"], top_teams["League"]):
    ax.text(val + 15, bar.get_y() + bar.get_height()/2,
            f"{int(val)} ({league})", va="center", fontsize=9, fontweight="bold")
ax.set_title("Top 10 des équipes par buts inscrits (2017-2024)")
ax.set_xlabel("Buts totaux")
plt.savefig(FIGURES / "08_top10_teams_goals.png")
plt.close()

# --- Fig 9 : heatmap ligue × saison (buts moyens par joueur) ---
fig, ax = plt.subplots(figsize=(11, 5))
pivot_avg = df.groupby(["League", "SeasonLabel"], observed=True)["Goals"].mean().unstack()
pivot_avg = pivot_avg.reindex(["Premier League", "La Liga", "Ligue 1", "Bundesliga", "Serie A"])
sns.heatmap(pivot_avg, annot=True, fmt=".2f", cmap="YlOrRd",
            cbar_kws={"label": "Buts moyens / joueur"}, ax=ax, linewidths=0.4)
ax.set_title("Buts moyens par joueur — ligue × saison")
ax.set_xlabel("Saison"); ax.set_ylabel("")
plt.savefig(FIGURES / "09_avg_goals_heatmap.png")
plt.close()

# --- Fig 10 : top 15 nations par joueurs ---
fig, ax = plt.subplots(figsize=(11, 7))
top_n = dm_nations.head(15).sort_values("players")
bars = ax.barh(top_n["Nation"], top_n["players"],
               color=sns.color_palette("viridis", len(top_n)), edgecolor="black")
for bar, val in zip(bars, top_n["players"]):
    ax.text(val + 3, bar.get_y() + bar.get_height()/2,
            f"{int(val)}", va="center", fontweight="bold")
ax.set_title("Top 15 des nations représentées dans le Top 5 européen")
ax.set_xlabel("Nombre de joueurs uniques")
plt.savefig(FIGURES / "10_top15_nations.png")
plt.close()

print(f"   ✓ 10 figures générées dans {FIGURES}/")
print("▶ [4/4] Terminé ✨")