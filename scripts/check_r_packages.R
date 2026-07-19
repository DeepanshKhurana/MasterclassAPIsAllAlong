packages <- c(
  "box",
  "cricketdata",
  "dplyr",
  "glue",
  "logger",
  "memoise",
  "plumber2",
  "purrr",
  "rlang",
  "stringr"
)

results <- vapply(
  packages,
  function(pkg) requireNamespace(pkg, quietly = TRUE),
  logical(1)
)

for (pkg in names(results)) {
  status <- if (results[[pkg]]) "OK" else "FAILED"
  cat(sprintf("[%s] %s\n", status, pkg))
}

if (!all(results)) {
  cat("\nSome r-service packages failed to load.\n")
  quit(status = 1)
}

cat("\nAll r-service packages loaded successfully.\n")
