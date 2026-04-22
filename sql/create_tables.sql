-- ============================================
-- create_tables.sql
-- Schéma BigQuery pour héberger le dataset FBref
-- et ses datamarts (option entrepôt pour Looker).
-- ============================================

CREATE SCHEMA IF NOT EXISTS `top5_football`;

-- ============================================
-- Table principale : un record par joueur × saison × équipe
-- (colonnes principales seulement — le dataset brut a 178 colonnes)
-- ============================================
CREATE OR REPLACE TABLE `top5_football.players` (
    League                STRING    NOT NULL,
    Season                INT64     NOT NULL,
    SeasonLabel           STRING    NOT NULL,
    Team                  STRING    NOT NULL,
    Player                STRING    NOT NULL,
    Nation                STRING,
    Position              STRING,
    PrimaryPosition       STRING,
    PositionGroup         STRING,
    Age                   FLOAT64,
    AgeGroup              STRING,
    Born                  INT64,

    -- Temps de jeu
    MatchesPlayed         INT64,
    Starts                INT64,
    Minutes               INT64,
    Nineties              FLOAT64,

    -- Performance
    Goals                 INT64,
    Assists               INT64,
    GoalsPlusAssists      INT64,
    GoalsNonPenalty       INT64,
    PenaltiesScored       INT64,
    PenaltiesAttempted    INT64,
    YellowCards           INT64,
    RedCards              INT64,

    -- Expected stats
    xG                    FLOAT64,
    npxG                  FLOAT64,
    xAG                   FLOAT64,
    xGDifference          FLOAT64,
    xGDifferencePer90     FLOAT64,

    -- Tirs & finition
    Shots                 INT64,
    ShotsOnTarget         INT64,
    ShotsOnTargetPct      FLOAT64,

    -- Per 90
    GoalsPer90            FLOAT64,
    AssistsPer90          FLOAT64,
    GoalsPlusAssistsPer90 FLOAT64,
    xGPer90               FLOAT64,
    xAGPer90              FLOAT64,

    -- Passes & progression
    PassCompletionPct     FLOAT64,
    ProgressivePasses     INT64,
    ProgressiveCarries    INT64,

    -- Défense
    Tackles               INT64,
    Interceptions         INT64,
    Clearances            INT64,

    -- Dribbles
    TakeOnsAttempted      INT64,
    TakeOnsSuccessful     INT64,
    TakeOnsSuccessPct     FLOAT64,

    -- Duels aériens
    AerialDuelsWon        INT64,
    AerialDuelsWonPct     FLOAT64,

    QualifiedMinutes      BOOL
)
PARTITION BY RANGE_BUCKET(Season, GENERATE_ARRAY(1718, 2425, 101))
CLUSTER BY League, Team, Player;


-- ============================================
-- Datamarts
-- ============================================

CREATE OR REPLACE TABLE `top5_football.dm_global_kpis` (
    total_records                   INT64,
    unique_players                  INT64,
    unique_teams                    INT64,
    unique_nations                  INT64,
    seasons_covered                 INT64,
    leagues_covered                 INT64,
    total_goals                     INT64,
    total_assists                   INT64,
    total_minutes                   INT64,
    avg_age                         FLOAT64,
    avg_goals_per_player_season     FLOAT64,
    avg_xG_per_player_season        FLOAT64
);

CREATE OR REPLACE TABLE `top5_football.dm_league_season` (
    League              STRING,
    SeasonLabel         STRING,
    players             INT64,
    teams               INT64,
    total_goals         INT64,
    total_assists       INT64,
    total_xG            FLOAT64,
    avg_age             FLOAT64,
    avg_pass_completion FLOAT64
);

CREATE OR REPLACE TABLE `top5_football.dm_team_performance` (
    League           STRING,
    Team             STRING,
    seasons_present  INT64,
    total_goals      INT64,
    total_assists    INT64,
    total_xG         FLOAT64,
    avg_age          FLOAT64,
    players_used     INT64,
    goals_per_season FLOAT64
);

CREATE OR REPLACE TABLE `top5_football.dm_position_profile` (
    PositionGroup          STRING,
    n_records              INT64,
    avg_age                FLOAT64,
    avg_minutes            FLOAT64,
    avg_goals              FLOAT64,
    avg_assists            FLOAT64,
    avg_xG                 FLOAT64,
    avg_progressive_passes FLOAT64,
    avg_tackles            FLOAT64,
    avg_interceptions      FLOAT64,
    avg_aerial_won_pct     FLOAT64
);