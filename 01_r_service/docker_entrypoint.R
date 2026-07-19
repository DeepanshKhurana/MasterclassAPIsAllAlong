# Used only by the Dockerfile, plumber.R is untouched and still used by the course platform
box::use(
  plumber2[
    api_run,
  ],
  ./R/endpoints[
    build_api,
  ],
)

port <- as.integer(Sys.getenv("PORT", "10000"))

cat(sprintf("plumber2 on port %d\n", port))

build_api() |>
  api_run(
    host = "0.0.0.0",
    port = port,
    block = TRUE
  )
