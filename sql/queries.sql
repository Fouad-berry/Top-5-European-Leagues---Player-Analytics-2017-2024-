-- ============================================
-- queries.sql
-- Requêtes analytiques pour Looker Studio et exploration
-- ============================================

-- 1. KPIs globaux
SELECT
    COUNT(*)                          AS total_records,
    COUNT(DISTINCT Player)            AS unique_players,
    COUNT(DISTINCT Team)              AS unique_teams,
    SUM(Goals)                        AS total_goals,
    SUM(Assists)                      AS total_assists,
    ROUND(AVG(Age), 2)                AS avg_age,
    ROUND(AVG(Goals), 2)              AS avg_goals_per_player_season
FROM `top5_football.players`;


-- 2. Meilleurs buteurs toutes saisons confondues
SELECT
    Player,
    COUNT(DISTINCT SeasonLabel) AS seasons_played,
    SUM(Goals)                  AS total_goals,
    SUM(Assists)                AS total_assists,
    ROUND(SUM(xG), 2)           AS total_xG,
    ROUND(SUM(Goals) - SUM(xG), 2) AS xG_overperformance
FROM `top5_football.players`
GROUP BY Player
ORDER BY total_goals DESC
LIMIT 20;


-- 3. Évolution des buts par ligue
SELECT
    League,
    SeasonLabel,
    SUM(Goals)              AS total_goals,
    ROUND(AVG(Goals), 2)    AS avg_goals_per_player,
    COUNT(DISTINCT Player)  AS players
FROM `top5_football.players`
GROUP BY League, SeasonLabel
ORDER BY League, SeasonLabel;


-- 4. Top équipes par ligue (avec ranking)
SELECT *
FROM (
    SELECT
        League, Team,
        SUM(Goals) AS total_goals,
        ROW_NUMBER() OVER (PARTITION BY League ORDER BY SUM(Goals) DESC) AS rank_in_league
    FROM `top5_football.players`
    GROUP BY League, Team
)
WHERE rank_in_league <= 5
ORDER BY League, rank_in_league;


-- 5. Sur-performeurs xG (joueurs qui marquent beaucoup plus que leur xG)
SELECT
    SeasonLabel, League, Team, Player,
    Goals,
    ROUND(xG, 2)             AS xG,
    ROUND(Goals - xG, 2)     AS xG_difference,
    Shots, ShotsOnTarget
FROM `top5_football.players`
WHERE QualifiedMinutes = TRUE
  AND xG >= 5
ORDER BY (Goals - xG) DESC
LIMIT 20;


-- 6. Profil moyen par position
SELECT
    PositionGroup,
    COUNT(*)                                  AS n_records,
    ROUND(AVG(Age), 1)                        AS avg_age,
    ROUND(AVG(Minutes), 0)                    AS avg_minutes,
    ROUND(AVG(Goals), 2)                      AS avg_goals,
    ROUND(AVG(Assists), 2)                    AS avg_assists,
    ROUND(AVG(ProgressivePasses), 1)          AS avg_prg_passes,
    ROUND(AVG(Tackles), 1)                    AS avg_tackles,
    ROUND(AVG(AerialDuelsWonPct), 1)          AS avg_aerial_won_pct
FROM `top5_football.players`
GROUP BY PositionGroup
ORDER BY avg_goals DESC;


-- 7. Jeunes talents prometteurs (U21 avec 10+ buts)
SELECT
    SeasonLabel, League, Team, Player, Age,
    Goals, Assists,
    ROUND(xG, 2) AS xG,
    Minutes
FROM `top5_football.players`
WHERE AgeGroup = 'U21'
  AND Goals >= 10
ORDER BY Goals DESC;


-- 8. Nations les plus représentées
SELECT
    Nation,
    COUNT(DISTINCT Player) AS unique_players,
    SUM(Goals)             AS total_goals,
    SUM(Minutes)           AS total_minutes
FROM `top5_football.players`
WHERE Nation IS NOT NULL
GROUP BY Nation
ORDER BY unique_players DESC
LIMIT 25;