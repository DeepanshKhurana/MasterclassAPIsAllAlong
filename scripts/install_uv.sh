#!/bin/bash
# Install uv — a fast Python package manager (https://github.com/astral-sh/uv)
# uv replaces pip + venv + pip-tools in a single binary.
set -euo pipefail
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
# Make uv available for subsequent RUN steps in the Dockerfile.
# The build pipeline should add this to PATH in the generated Dockerfile.
export PATH="/root/.local/bin:$PATH"
echo 'export PATH="/root/.local/bin:$PATH"' >> /etc/environment
# Copy to a system-wide location so non-root session users can access it
# (/root/.local/bin is unreachable for them because /root is mode 750).
cp /root/.local/bin/uv /usr/local/bin/uv
uv --version
echo "uv installed successfully."