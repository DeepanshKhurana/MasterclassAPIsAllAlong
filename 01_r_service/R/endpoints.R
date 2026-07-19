box::use(
  glue[
    glue,
  ],
  logger[
    log_error,
    log_info,
  ],
  plumber2[
    api,
    api_get,
    get_serializers,
  ],
  ./analysis[
    build_team_leaderboard,
    build_team_record,
  ],
)

json_serializer <- get_serializers(
  list(
    json = list(
      auto_unbox = TRUE,
      na = "null"
    )
  )
)

decode_path_segment <- function(segment) {
  utils::URLdecode(segment)
}

query_value <- function(query, key, default) {
  value <- query[[key]]
  if (is.null(value)) default else value
}

handle_leaderboard <- function(format, query) {
  tryCatch({
    metric <- query_value(query, "metric", "batting_avg")
    n <- as.integer(query_value(query, "n", "10"))
    leaderboard_tbl <- build_team_leaderboard(format, metric, n)
    log_info(glue("Served leaderboard for {format} ranked by {metric}"))
    list(status = "ok", data = leaderboard_tbl)
  },
  error = function(e) {
    log_error(glue("GET /leaderboard/{format} failed: {e$message}"))
    list(status = "error", message = e$message)
  })
}

handle_team_record <- function(team, query) {
  tryCatch({
    team_name <- decode_path_segment(team)
    format <- query_value(query, "format", "T20")
    record_tbl <- build_team_record(team_name, format)
    log_info(glue("Served team record for {team_name} ({format})"))
    list(status = "ok", data = as.list(record_tbl))
  },
  error = function(e) {
    log_error(glue("GET /teams/{team}/record failed: {e$message}"))
    list(status = "error", message = e$message)
  })
}

handle_health <- function() {
  list(status = "ok")
}

build_api <- function() {
  api(doc_type = "rapidoc") |>
    api_get(
      "/health",
      handle_health,
      serializers = json_serializer
    ) |>
    api_get(
      "/leaderboard/<format:string>",
      handle_leaderboard,
      serializers = json_serializer
    ) |>
    api_get(
      "/teams/<team:string>/record",
      handle_team_record,
      serializers = json_serializer
    )
}
