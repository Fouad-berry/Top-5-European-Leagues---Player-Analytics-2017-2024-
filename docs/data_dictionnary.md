# 📖 Data Dictionary

## Dataset source : `top5_players_2017_2024.csv`

- **Origine** : [FBref](https://fbref.com/) (données StatsBomb)
- **Dimensions** : 22 929 lignes × 178 colonnes
- **Format** : CSV européen — séparateur `;`, décimal `,`
- **Unité** : un record = un joueur × une saison × une équipe (un joueur qui change d'équipe en cours de saison apparaît deux fois)

---

## Colonnes principales (après renommage par `src/preprocessing.py`)

### Identification

| Original | Renommé | Description |
|----------|---------|-------------|
| `league` | `League` | Ligue (préfixes pays supprimés : `ENG-Premier League` → `Premier League`) |
| `season` | `Season` | Saison au format entier (`1718`, `1819`, ..., `2425`) |
| — | `SeasonLabel` | Saison lisible (`2017-18`, `2018-19`, …) — **dérivée** |
| `team` | `Team` | Équipe |
| `player` | `Player` | Nom du joueur |
| `nation_` | `Nation` | Code pays FIFA (ex: `FRA`, `ENG`, `ESP`) |
| `pos_` | `Position` | Position(s) séparées par virgule (ex: `DF,MF`) |
| — | `PrimaryPosition` | Première position listée — **dérivée** |
| — | `PositionGroup` | `Goalkeeper`, `Defender`, `Midfielder`, `Forward` — **dérivée** |
| `age_` | `Age` | Âge à la saison en cours |
| — | `AgeGroup` | `U21`, `21-24`, `25-28`, `29-32`, `33+` — **dérivée** |
| `born_` | `Born` | Année de naissance |

### Temps de jeu

| Original | Renommé | Description |
|----------|---------|-------------|
| `Playing Time_MP` | `MatchesPlayed` | Matchs joués |
| `Playing Time_Starts` | `Starts` | Titularisations |
| `Playing Time_Min` | `Minutes` | Minutes totales jouées |
| `Playing Time_90s` | `Nineties` | Nombre de « 90 minutes » équivalents |

### Performance offensive

| Original | Renommé | Description |
|----------|---------|-------------|
| `Performance_Gls` | `Goals` | Buts marqués |
| `Performance_Ast` | `Assists` | Passes décisives |
| `Performance_G+A` | `GoalsPlusAssists` | Buts + passes |
| `Performance_G-PK` | `GoalsNonPenalty` | Buts hors penalty |
| `Performance_PK` | `PenaltiesScored` | Penalties marqués |
| `Performance_PKatt` | `PenaltiesAttempted` | Penalties tentés |

### Expected stats (xG)

| Original | Renommé | Description |
|----------|---------|-------------|
| `Expected_xG` | `xG` | Expected Goals — qualité des occasions |
| `Expected_npxG` | `npxG` | xG hors penalty |
| `Expected_xAG` | `xAG` | Expected Assisted Goals |
| — | `xGDifference` | `Goals - xG` — indicateur de sur/sous-performance **dérivée** |
| — | `xGDifferencePer90` | xGDifference normalisé par 90 min — **dérivée** |

### Tirs

| Original | Renommé | Description |
|----------|---------|-------------|
| `Standard_Sh` | `Shots` | Tirs totaux |
| `Standard_SoT` | `ShotsOnTarget` | Tirs cadrés |
| `Standard_SoT%` | `ShotsOnTargetPct` | % de tirs cadrés |

### Passes & progression

| Original | Renommé | Description |
|----------|---------|-------------|
| `Total_Cmp%` | `PassCompletionPct` | % de passes réussies |
| `Progression_PrgP` | `ProgressivePasses` | Passes progressives |
| `Progression_PrgC` | `ProgressiveCarries` | Conduites progressives |

### Défense

| Original | Renommé | Description |
|----------|---------|-------------|
| `Tackles_Tkl` | `Tackles` | Tacles |
| `Int_` | `Interceptions` | Interceptions |
| `Clr_` | `Clearances` | Dégagements |
| `Aerial Duels_Won` | `AerialDuelsWon` | Duels aériens gagnés |
| `Aerial Duels_Won%` | `AerialDuelsWonPct` | % duels aériens gagnés |

### Dribbles

| Original | Renommé | Description |
|----------|---------|-------------|
| `Take-Ons_Att` | `TakeOnsAttempted` | Dribbles tentés |
| `Take-Ons_Succ` | `TakeOnsSuccessful` | Dribbles réussis |
| `Take-Ons_Succ%` | `TakeOnsSuccessPct` | % de dribbles réussis |

### Flag dérivé

| Variable | Description |
|----------|-------------|
| `QualifiedMinutes` | `True` si `Minutes >= 450` (5 matchs complets). À utiliser pour filtrer les analyses par 90 min (sinon bruit statistique sur les remplaçants occasionnels). |

---

## Les 130+ autres colonnes (non renommées)

Le CSV contient beaucoup de stats avancées non renommées mais toujours accessibles par leur nom original :
- Types de passes (courtes, moyennes, longues, key passes…)
- Corners (in, out, straight)
- GCA / SCA (actions menant à un but / tir)
- Blocks (passes bloquées, tirs bloqués)
- Team success with/without player (+/-, xG+/-, PPM…)
- Touches par zone du terrain

Voir [FBref — Glossaire](https://fbref.com/en/expected-goals-model-explained/) pour la définition détaillée de chaque métrique.

---

## Notes méthodologiques

- **Valeurs manquantes** : ~85 000 cellules vides dans certaines colonnes (surtout celles calculées, qui n'ont de sens que pour les joueurs de champ, pas les gardiens, ou pour les joueurs avec assez de temps de jeu)
- **Joueurs à plusieurs équipes** : un joueur transféré en cours de saison apparaît deux fois (une par équipe). À prendre en compte dans les agrégations par joueur (utiliser `groupby('Player')` avec somme).
- **Saison 2019-20 en Ligue 1** : écourtée à cause du COVID, les totaux sont plus bas. À documenter dans toute comparaison chronologique.
- **Saison 2024-25** : en cours au moment de l'extraction — peut être incomplète.