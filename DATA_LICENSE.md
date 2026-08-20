# Player archive data license

`data/processed/hitter_seasons.parquet` and `pitcher_seasons.parquet` are adapted from:

- **KBO Player Dataset (1982-2025)** by Kaggle user **netsong**
- Source: https://www.kaggle.com/datasets/netsong/kbo-player-dataset-by-regular-season-1982-2025
- License stated on the dataset page: **CC BY-SA 4.0**
- Changes: selected Hanwha Eagles regular-season rows for 2015-2025, normalized identifiers and columns, converted pitching innings to outs, and recalculated rate statistics.

These two derived parquet files are distributed under **CC BY-SA 4.0**. The dataset author states that the upstream records were collected from STATIZ. This attribution does not imply endorsement by KBO or STATIZ.

The 2026 player season is not included. Known upstream limitations are recorded in `data/processed/player_archive_source.json`.
