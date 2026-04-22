# 📊 Guide Looker Studio

## 🔗 Lien du dashboard

> **[👉 Ouvrir le dashboard](https://lookerstudio.google.com/)** *(à remplacer par ton lien publié)*

---

## 🚀 Connexion des données

### Option A — Upload CSV direct (recommandé)

1. [lookerstudio.google.com](https://lookerstudio.google.com/) → **Créer** → **Source de données**
2. Connecteur **File Upload**
3. Uploader ces fichiers depuis `data/exports/` :
   - `main_dataset.csv` (version allégée du dataset complet, ~40 colonnes)
   - `by_league_season.csv` (évolution par ligue et saison)
   - `top_scorers.csv` (top 10 buteurs par saison)
   - `by_team.csv` (performance agrégée des clubs)
   - `by_position.csv` (profils par position)
   - `xg_finishing.csv` (sur/sous-performeurs xG)
   - `global_kpis.csv` (scorecards)
4. Pour chaque source : **Créer un rapport**

### Option B — BigQuery (pour grandes équipes ou mises à jour fréquentes)

1. Exécuter `sql/create_tables.sql` dans BigQuery
2. Charger les CSV via `bq load` ou l'UI
3. Dans Looker Studio : **Ajouter une source** → **BigQuery**
4. Utiliser les requêtes de `sql/queries.sql` comme sources personnalisées

---

## 🎨 Structure recommandée en 5 pages

### 📄 Page 1 — Overview

Source : `global_kpis.csv` + `main_dataset.csv`

- **6 scorecards** : total players, total goals, total assists, seasons covered, unique nations, avg age
- **Line chart** : total de buts par saison × ligue
- **Donut chart** : répartition des joueurs par position
- **Table** : KPIs par ligue

### 📄 Page 2 — Players

Source : `main_dataset.csv` + `xg_finishing.csv`

- **Bar chart horizontal** : top 20 buteurs (somme sur toutes les saisons)
- **Bar chart horizontal** : top 20 passeurs
- **Scatter plot** : xG (X) vs Goals (Y), dot size = Minutes, color = PositionGroup
- **Table** : top 20 sur-performeurs xG (depuis `xg_finishing.csv`)
- **Filtres** : saison, ligue, position, âge

### 📄 Page 3 — Teams

Source : `by_team.csv`

- **Treemap** : équipes par ligue, taille = total_goals
- **Bar chart** : top 15 équipes par `goals_per_season`
- **Table complète** : tous les clubs avec tri interactif
- **Filtre** : ligue

### 📄 Page 4 — Positions

Source : `by_position.csv` + `main_dataset.csv`

- **Bar chart** : buts moyens par position
- **Box plot** : distribution de l'âge par position
- **Radar chart** (via Community Visualizations) : profil statistique type par position
- **Table** : toutes les stats moyennes par position

### 📄 Page 5 — Nations

Source : `main_dataset.csv`

- **Geo map** : nombre de joueurs par pays (utiliser code pays FIFA)
- **Bar chart** : top 20 nations par joueurs uniques
- **Bar chart** : top 20 nations par buts
- **Table** : stats par nation

---

## 🎛️ Filtres interactifs (haut de page)

- **Saison** (`SeasonLabel` — dropdown multiple)
- **Ligue** (`League` — boutons 5 options)
- **Position** (`PositionGroup` — boutons)
- **Tranche d'âge** (`AgeGroup`)
- **Équipe** (`Team` — recherche)
- **Minutes minimales** (slider, défaut = 450 pour `QualifiedMinutes`)

---

## 💡 Astuces

### Palette par ligue

Utilise des couleurs officielles pour cohérence :
- Premier League : `#3D195B` (violet)
- La Liga : `#EE8707` (orange)
- Ligue 1 : `#091C3E` (bleu marine)
- Bundesliga : `#D3010C` (rouge)
- Serie A : `#008FD7` (bleu)

### Champs calculés utiles

Dans Looker, ajoute :
- `GoalsPerMatch = Goals / MatchesPlayed`
- `IsStarter = IF(Starts > MatchesPlayed / 2, "Titulaire", "Remplaçant")`
- `xGOverperformance = Goals - xG`

### Jointures

Tu peux créer une **source jointe** dans Looker pour associer :
- `main_dataset.csv` (grain joueur·saison) avec
- `by_league_season.csv` (KPIs de la ligue cette saison-là)

---

## 📸 Captures d'écran

Place tes captures dans `images/` et référence-les ici :

```markdown
![Overview](../images/dashboard_01_overview.png)
![Players](../images/dashboard_02_players.png)
![Teams](../images/dashboard_03_teams.png)
![Positions](../images/dashboard_04_positions.png)
![Nations](../images/dashboard_05_nations.png)
```