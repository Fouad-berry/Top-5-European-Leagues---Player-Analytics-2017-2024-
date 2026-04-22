# 🔬 Méthodologie

## 1. Exploration (EDA)

- Vérification du format (CSV européen : `;` comme séparateur, `,` comme décimale)
- Inspection des 178 colonnes et identification des métriques prioritaires
- Comptage des valeurs manquantes par colonne (surtout sur les stats avancées qui n'ont de sens que pour certains postes)
- Distribution des buts, âges, minutes

## 2. Nettoyage et feature engineering

Pipeline dans `src/preprocessing.py` :

1. **Renommage** des colonnes principales (30+) pour passer d'un format FBref (`Performance_Gls`, `Expected_xG`…) à un format Python-friendly (`Goals`, `xG`…)
2. **Nettoyage des noms de ligue** : suppression des préfixes `ENG-`, `ESP-`, `FRA-`, `GER-`, `ITA-`
3. **Saison lisible** : `1718` → `2017-18`
4. **Features de position** : `PrimaryPosition` (première pos listée) et `PositionGroup` (GK/DF/MF/FW)
5. **Tranches d'âge** : U21, 21-24, 25-28, 29-32, 33+
6. **Features xG** : `xGDifference = Goals - xG`, version per 90 min, `GoalsPerShot`
7. **Flag de qualification** : `QualifiedMinutes = Minutes >= 450` (5 matchs complets)

## 3. Construction des datamarts

Implémentée dans `src/datamarts.py`. Sept datamarts, un par question métier (voir [`datamarts_spec.md`](datamarts_spec.md)).

## 4. Visualisation

**Python (Matplotlib / Seaborn)** :
- Palette par ligue (violet PL, orange LaLiga, bleu Ligue 1, rouge Bundesliga, bleu clair Serie A)
- Annotations directes sur les graphiques pour éviter la lecture d'axe
- DPI=140 pour rendu propre sur GitHub

**Looker Studio** : dashboard interactif en 5 pages, alimenté par les CSV des datamarts.

## 5. Export vers Looker Studio

Deux options :

**Option légère** : upload direct des CSV depuis `data/exports/`. Le `main_dataset.csv` est une version allégée (~40 colonnes) du dataset complet pour rester sous la limite de Looker (~100 MB).

**Option entrepôt** : charger les données dans BigQuery via `sql/create_tables.sql`, puis brancher Looker sur BigQuery. Avantage : requêtes SQL directes, pas de limite de taille.

## 6. Limitations

- **Transferts en cours de saison** : un joueur transféré apparaît deux fois dans le dataset (une par équipe). Les agrégations par joueur utilisent `groupby('Player').sum()` pour éviter les doubles comptages de stats.
- **Saison 2019-20 Ligue 1** : écourtée (COVID), totaux artificiellement bas
- **Saison 2024-25** : potentiellement incomplète selon la date d'extraction
- **xG non disponible pour les saisons anciennes** dans certaines sources — ici les données couvrent bien 2017-2024 mais xG reste plus fiable à partir de 2017-18
- **Gardiens** : beaucoup de métriques offensives/défensives n'ont pas de sens pour eux (NaN attendu)