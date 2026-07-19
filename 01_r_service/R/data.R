box::use(
  cricketdata[
    fetch_cricinfo,
  ],
  glue[
    glue,
  ],
  logger[
    log_info,
  ],
  memoise[
    memoise,
  ],
)

fetch_cricinfo_cached <- memoise(function(matchtype, activity, country) {
  country_label <- if (is.null(country)) "all countries" else country
  log_info(
    glue("Fetching {activity} {matchtype} career data for {country_label}")
  )
  fetch_cricinfo(
    matchtype = matchtype,
    activity = activity,
    type = "career",
    country = country
  )
})

fetch_team_batting <- function(team, format = "T20") {
  fetch_cricinfo_cached(
    matchtype = format,
    activity = "batting",
    country = team
  )
}
