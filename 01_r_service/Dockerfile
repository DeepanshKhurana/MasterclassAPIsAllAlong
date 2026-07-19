# Official R image pinned to the version this project was built with
FROM rocker/r-ver:4.5.0

# System libraries R packages need, P3M below only covers some as binaries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-dev libcurl4-openssl-dev libssl-dev libicu-dev libxml2-dev \
    cmake make libuv1-dev zlib1g-dev pandoc libsodium-dev xz-utils \
    libfreetype6-dev libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libfontconfig1-dev libfribidi-dev libharfbuzz-dev rustc cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy renv setup files first so this layer gets cached between builds
COPY .Rprofile .Rprofile
COPY renv.lock renv.lock
COPY renv/activate.R renv/settings.json renv/

# Use Posit Package Manager so packages install as prebuilt binaries, not source
ENV RENV_CONFIG_REPOS_OVERRIDE=https://packagemanager.posit.co/cran/__linux__/noble/latest

# Install the exact pinned package versions from renv.lock
RUN Rscript -e "options(repos = c(P3M = Sys.getenv('RENV_CONFIG_REPOS_OVERRIDE'))); install.packages('renv')" \
    -e "renv::restore()"

# Copy this service's code
COPY 01_r_service ./01_r_service

# Deployment uses its own entrypoint, plumber.R is untouched for the course platform
EXPOSE 10000
ENV PORT=10000

CMD ["Rscript", "01_r_service/docker_entrypoint.R"]
