box::use(
  plumber2[
    api_run,
  ],
  ./R/endpoints[
    build_api,
  ],
)

svc <- 0L
uid <- if (.Platform$OS.type == "unix") as.integer(system2("id", "-u", stdout = TRUE)) else 0L
port <- 10000L + (uid %% 6000L) * 3L + svc

cat(sprintf("plumber2 on port %d\n", port))
cat(sprintf("Docs: http://127.0.0.1:%d/__docs__\n", port))

build_api() |>
  api_run(
    host = "0.0.0.0",
    port = port,
    block = TRUE
  )
