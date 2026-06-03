# Base image: official Python, slim variant (small, Debian-based).
# Pin version so builds are reproducible.
FROM python:3.11-slim

# Where commands run inside the container. Created if absent.
WORKDIR /app

# Copy only package metadata first (not whole repo yet).
# Why first: Docker caches layers. Deps rarely change, so this
# layer is reused across builds unless pyproject.toml changes.
COPY pyproject.toml README.md ./

# Copy source needed for the package install to resolve.
COPY src/ ./src/

# Install the package + deps. --no-cache-dir keeps image small.
RUN pip install --no-cache-dir .

# Run as non-root user (security: container breakout harder).
RUN useradd --create-home appuser
USER appuser

# What runs when container starts. Your console script.
CMD ["slangify"]
