# 🧱 Spécification des datamarts

Chaque datamart est une table agrégée qui répond à une question métier précise, prête à être branchée dans Looker Studio.

---

## 1. `dm_global_kpis.csv`

**Grain** : 1 seule ligne
**Usage** : scorecards en haut du dashboard

| Colonne | Description |
|---------|-------------|
| `total_records` | Nombre de (joueur × saison × équipe) |
| `unique_players` | Joueurs uniques |
| `unique_teams` | Équipes uniques |
| `unique_nations` | Nationalités représentées |
| `seasons_covered` | Nombre de saisons |
| `leagues_covered` | Nombre de ligues |
| `total_goals` | Buts totaux dans tout le dataset |
| `total_assists` | Passes décisives totales |
| `total_minutes` | Minutes jouées (cumul) |
| `avg_age` | Âge moyen |
| `avg_goals_per_player_season` | Buts moyens par joueur·saison |
| `avg_xG_per_player_season` | xG moyen par joueur·saison |

---

## 2. `dm_league_season.csv`

**Grain** : ligue × saison (5 × 8 = 40 lignes)
**Question** : "Comment chaque ligue évolue saison après saison ?"
**Usage** : graphiques linéaires, heatmaps temporelles

Colonnes : `League`, `SeasonLabel`, `players`, `teams`, `total_goals`, `total_assists`, `total_xG`, `avg_age`, `avg_pass_completion`.

---

## 3. `dm_top_scorers_by_season.csv`

**Grain** : top 10 buteurs × saison
**Question** : "Qui a gagné le soulier d'or dans chaque ligue ?"
**Usage** : tables filtrables par saison, slicers

Colonnes : `SeasonLabel`, `League`, `Team`, `Player`, `PositionGroup`, `Age`, `Goals`, `Assists`, `xG`, `ShotsOnTarget`, `Minutes`.

Tri : par saison puis buts décroissants.

---

## 4. `dm_team_performance.csv`

**Grain** : ligue × équipe (~149 lignes)
**Question** : "Quels clubs marquent le plus sur la période ?"
**Usage** : comparatifs par club, top N

Colonnes : `League`, `Team`, `seasons_present`, `total_goals`, `total_assists`, `total_xG`, `avg_age`, `players_used`, `goals_per_season`.

Note : `seasons_present` varie car tous les clubs ne sont pas en ligue 1 toutes les saisons (promotions/relégations).

---

## 5. `dm_position_profile.csv`

**Grain** : groupe de position (4-5 lignes : Goalkeeper, Defender, Midfielder, Forward, Other)
**Question** : "À quoi ressemble le joueur type à chaque poste ?"
**Usage** : radar charts, profils types

Colonnes : `PositionGroup`, `n_records`, `avg_age`, `avg_minutes`, `avg_goals`, `avg_assists`, `avg_xG`, `avg_progressive_passes`, `avg_tackles`, `avg_interceptions`, `avg_aerial_won_pct`.

---

## 6. `dm_xg_finishing.csv`

**Grain** : joueur × saison (filtré : `QualifiedMinutes=True` et `xG >= 3`)
**Question** : "Qui sur-performe vs son xG ? Qui est un finisseur clinique ?"
**Usage** : table de sur/sous-performeurs, scatter `xG` vs `Goals`

Colonnes : `SeasonLabel`, `League`, `Team`, `Player`, `PositionGroup`, `Goals`, `xG`, `xGDifference`, `Shots`, `ShotsOnTarget`, `Minutes`.

Tri : par `xGDifference` décroissant (les meilleurs finisseurs en tête).

---

## 7. `dm_top_nations.csv`

**Grain** : nation (top 25 par minutes)
**Question** : "Quelles nationalités dominent le Top 5 européen ?"
**Usage** : map visuelle, bar chart

Colonnes : `Nation`, `players`, `appearances`, `total_goals`, `total_minutes`, `goals_per_player`.

---

## Règles de construction

- Tous les arrondis à **2 décimales**
- Les % sont en base 100 (pas 0.XX)
- Chaque agrégation inclut un `count` (`players`, `n_records`, etc.) pour permettre de pondérer côté Looker
- Les datamarts sont recalculés depuis zéro à chaque exécution de `build_project.py`
- Source unique : `data/processed/top5_players_clean.csv`