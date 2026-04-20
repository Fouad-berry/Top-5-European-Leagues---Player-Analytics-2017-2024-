# ⚽ Top 5 European Leagues — Player Analytics (2017-2024)

> Analyse des performances de **7 136 joueurs** dans les cinq grands championnats européens (Premier League, La Liga, Serie A, Bundesliga, Ligue 1) sur **8 saisons** (2017-18 à 2024-25).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458.svg)
![Looker Studio](https://img.shields.io/badge/Looker%20Studio-Dashboard-4285F4.svg)
![Football](https://img.shields.io/badge/Data-FBref-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Objectif du projet

Construire un pipeline data complet autour des stats FBref (178 variables par joueur·saison) : nettoyage, datamarts analytiques, visualisations et dashboard Looker Studio interactif.

**Questions métier :**
- Quels sont les **meilleurs buteurs** du Top 5 européen toutes saisons confondues ?
- Quelles **ligues** marquent le plus ? Comment ça évolue dans le temps ?
- Quels joueurs **sur-performent** par rapport à leurs xG (efficacité de finition) ?
- Quel est le **profil type** par position (âge, passes, duels aériens…) ?
- Quelles **nations** dominent le Top 5 européen ?

---

## 📊 Aperçu des résultats

### Total de buts par ligue et par saison

![Goals by league and season](images/figures/01_goals_by_league_season.png)

> La **Premier League** bat son record en **2023-24 (1 197 buts)**. On voit nettement la saison écourtée de la **Ligue 1 en 2019-20** (arrêt COVID).

### Top 15 buteurs toutes saisons

![Top 15 scorers](images/figures/02_top15_scorers_all_time.png)

> **Lewandowski (230 buts)** en tête, suivi de **Mbappé (206)** et **Harry Kane (197)**.

### xG vs Buts marqués — qui sur-performe ?

![xG vs Goals](images/figures/04_xg_vs_goals.png)

> La saison **2020-21 de Lewandowski** (41 buts pour ~31 xG) reste un sommet d'efficacité. **Kevin De Bruyne** sur-performe aussi régulièrement avec des xG modestes.

### Heatmap — buts moyens par joueur

![Heatmap](images/figures/09_avg_goals_heatmap.png)

📁 **10 figures générées** dans [`images/figures/`](images/figures/).

---

## 📁 Structure du projet

```
top5-football-analysis/
│
├── data/
│   ├── raw/
│   │   └── top5_players_2017_2024.csv        # Dataset brut FBref (22 929 × 178)
│   ├── processed/
│   │   └── top5_players_clean.csv            # Dataset nettoyé + features dérivées
│   ├── datamarts/                            # 🧱 7 tables analytiques
│   │   ├── dm_global_kpis.csv
│   │   ├── dm_league_season.csv
│   │   ├── dm_top_scorers_by_season.csv
│   │   ├── dm_team_performance.csv
│   │   ├── dm_position_profile.csv
│   │   ├── dm_xg_finishing.csv
│   │   └── dm_top_nations.csv
│   └── exports/                              # Exports prêts pour Looker Studio
│
├── notebooks/
│   ├── 01_exploration.ipynb                  # EDA
│   ├── 02_cleaning.ipynb                     # Nettoyage + feature engineering
│   ├── 03_datamarts.ipynb                    # Construction des datamarts
│   └── 04_visualizations.ipynb               # Figures
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py                        # Chargement des données
│   ├── preprocessing.py                      # Cleaning + features
│   ├── datamarts.py                          # Construction des 7 datamarts
│   ├── visualizations.py                     # Fonctions de plot
│   └── utils.py
│
├── sql/
│   ├── create_tables.sql                     # Schéma BigQuery
│   └── queries.sql                           # Requêtes analytiques
│
├── dashboards/
│   └── looker_studio_guide.md                # Guide de connexion + structure
│
├── docs/
│   ├── data_dictionary.md                    # Description des 178 variables
│   ├── datamarts_spec.md                     # Spécification des datamarts
│   └── methodology.md
│
├── images/figures/                           # 10 visualisations PNG pré-générées
│
├── build_project.py                          # ⭐ Script maître : regénère tout
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

---

## 📊 Description du dataset

Source : **[FBref](https://fbref.com/)** (via StatsBomb).

- **22 929 lignes** (joueur × saison × équipe)
- **178 colonnes** de stats : buts, passes, xG, xAG, passes progressives, duels aériens, tacles, etc.
- **5 ligues** : Premier League, La Liga, Serie A, Bundesliga, Ligue 1
- **8 saisons** : 2017-18 → 2024-25
- **7 136 joueurs uniques**, **149 équipes**, **140 nations** représentées

📄 Détail complet des variables : [`docs/data_dictionary.md`](docs/data_dictionary.md).

⚠️ **Format CSV européen** : séparateur `;`, décimal `,`. Le script `build_project.py` gère ça automatiquement.

---

## 🧱 Les 7 datamarts

| Datamart | Grain | Cas d'usage |
|----------|-------|-------------|
| `dm_global_kpis` | 1 ligne | Scorecards du dashboard |
| `dm_league_season` | ligue × saison | Évolution temporelle par championnat |
| `dm_top_scorers_by_season` | top 10 × saison | Classement des meilleurs buteurs saison par saison |
| `dm_team_performance` | ligue × équipe | Performance agrégée des clubs |
| `dm_position_profile` | position | Profil type par poste (GK, DF, MF, FW) |
| `dm_xg_finishing` | joueur × saison (filtré) | Qui sur-performe son xG ? |
| `dm_top_nations` | nation | Top 25 nations par minutes jouées |

📄 Spécification complète : [`docs/datamarts_spec.md`](docs/datamarts_spec.md).

---

## 🚀 Installation & utilisation

### 1. Cloner le repo

```bash
git clone https://github.com/<ton-username>/top5-football-analysis.git
cd top5-football-analysis
```

### 2. Environnement virtuel + dépendances

```bash
python -m venv venv
source venv/bin/activate       # Linux / Mac
# venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Générer tous les livrables en une commande

```bash
python build_project.py
```

Ce script :
1. Charge le CSV brut (format européen `;` / `,`)
2. Renomme les colonnes principales (plus propres pour l'analyse)
3. Nettoie les noms de ligue (`ENG-Premier League` → `Premier League`) et de saison (`1718` → `2017-18`)
4. Calcule les features : `PositionGroup`, `AgeGroup`, `xGDifference`, `QualifiedMinutes`, etc.
5. Construit les **7 datamarts**
6. Régénère les **10 figures PNG**

### 4. Explorer avec les notebooks

```bash
jupyter notebook notebooks/
```

---

## 🔎 Workflow

```
Raw CSV (22 929 × 178)
     │
     ▼
[1] Chargement + renommage colonnes
     │  • Séparateur ; décimal , → Python friendly
     │  • ENG-Premier League → Premier League
     │  • 1718 → 2017-18
     ▼
[2] Feature engineering
     │  • PositionGroup, AgeGroup
     │  • xGDifference (finition)
     │  • QualifiedMinutes (filtre 450 min)
     ▼
[3] 7 datamarts analytiques
     │
     ▼
[4] 10 figures PNG + exports Looker
     │
     ▼
[5] Dashboard Looker Studio interactif
```

---

## 📈 Dashboard Looker Studio

Structure recommandée en **5 pages** :

1. **Overview** — KPIs globaux + évolution des buts par ligue
2. **Players** — Top buteurs, xG, sur/sous-performeurs
3. **Teams** — Performance par club et par ligue
4. **Positions** — Profils type (GK, DF, MF, FW)
5. **Nations** — Répartition par nationalité

📄 Guide complet : [`dashboards/looker_studio_guide.md`](dashboards/looker_studio_guide.md).

---

## 📌 Principaux insights

- **Robert Lewandowski** est le meilleur buteur du Top 5 sur la période (230 buts)
- La **Premier League** produit en moyenne plus de buts que les autres ligues, surtout depuis 2023
- La saison **2020-21 de Lewandowski (41 buts)** est l'une des plus grosses sur-performances xG de la dernière décennie
- L'**âge moyen des gardiens** est significativement plus élevé que celui des attaquants
- Les **Français, Espagnols et Brésiliens** sont les trois nationalités les plus représentées
- La **Ligue 1 2019-20** (arrêt COVID précoce) est une anomalie statistique à prendre en compte

---

## 🛠️ Stack technique

- **Python 3.10+** · Pandas · NumPy
- **Matplotlib** · Seaborn pour les figures
- **Jupyter** pour l'exploration
- **Looker Studio** pour le dashboard final
- **BigQuery** (optionnel) pour héberger les données en mode entrepôt
- **Git / GitHub** pour le versioning

---

## 📝 Licence

MIT — voir [`LICENSE`](LICENSE). Les données FBref restent la propriété de leurs auteurs.

---

## 👤 Auteur

**[Fouad MOUTAIROU]**
- Portfolio : https://portfolio-fouad.netlify.app

---

## 🙏 Crédits

- Données : [**FBref**](https://fbref.com/) / [**StatsBomb**](https://statsbomb.com/)
- Projet à des fins éducatives et analytiques