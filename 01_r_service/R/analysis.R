box::use(
  dplyr[
    arrange,
    bind_rows,
    desc,
    filter,
    mutate,
    n,
    rename,
    row_number,
    slice_head,
    summarise,
    transmute,
  ],
  glue[
    glue,
  ],
  logger[
    log_error,
  ],
  purrr[
    map,
  ],
  rlang[
    `:=`,
  ],
  ./data[
    fetch_team_batting,
  ],
)

LEADERBOARD_TEAMS <- c(
  "India",
  "Australia",
  "England",
  "Pakistan",
  "New Zealand",
  "South Africa",
  "Afghanistan",
  "Sri Lanka"
)

METRIC_COLUMNS <- c(
  batting_avg = "average_batting_average",
  runs = "total_runs",
  strike_rate = "average_strike_rate"
)

finite_mean <- function(x) {
  finite_values <- x[is.finite(x)]
  if (length(finite_values) == 0) {
    NA_real_
  } else {
    mean(finite_values)
  }
}

summarise_team_batting <- function(squad_tbl) {
  squad_tbl |>
    summarise(
      players = n(),
      matches_played = sum(Matches, na.rm = TRUE),
      total_runs = sum(Runs, na.rm = TRUE),
      average_batting_average = finite_mean(Average),
      average_strike_rate = finite_mean(StrikeRate)
    )
}

build_team_record <- function(team, format = "T20") {
  squad_tbl <- fetch_team_batting(team, format)
  if (nrow(squad_tbl) == 0) {
    stop(glue("No batting data found for {team} in {format}"))
  }
  summarise_team_batting(squad_tbl) |>
    mutate(
      team = team,
      format = format,
      note = "Derived squad batting snapshot — not an official win/loss record."
    )
}

build_team_leaderboard <- function(format, metric, n) {
  if (!metric %in% names(METRIC_COLUMNS)) {
    stop(glue("Unsupported metric: {metric}"))
  }

  metric_col <- unname(METRIC_COLUMNS[[metric]])

  raw_tbl <- LEADERBOARD_TEAMS |>
    map(function(team) {
      tryCatch({
        squad_tbl <- fetch_team_batting(team, format)
        summarise_team_batting(squad_tbl) |>
          mutate(name = team)
      },
      error = function(e) {
        log_error(glue("Failed to fetch {team} for leaderboard: {e$message}"))
        NULL
      })
    }) |>
    bind_rows()

  raw_tbl$metric_value <- raw_tbl[[metric_col]]

  ranked_tbl <- raw_tbl |>
    filter(is.finite(metric_value)) |>
    arrange(desc(metric_value))

  ranked_tbl |>
    slice_head(n = n) |>
    transmute(
      rank = row_number(),
      name,
      metric_value
    ) |>
    rename(!!metric := metric_value)
}
