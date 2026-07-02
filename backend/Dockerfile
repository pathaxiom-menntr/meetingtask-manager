# ============================================================
#  Backend — Production Dockerfile
#  Target: Azure Container Apps / Azure Container Instances
#
#  Strategy: two-stage build
#    Stage 1 (builder) — installs dependencies into a venv
#    Stage 2 (runtime) — copies only the venv + app code
#
#  Result: slim ~250 MB image with no build tools at runtime
# ============================================================

# ── Stage 1: builder ─────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install OS build deps needed to compile some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only requirements first — maximises Docker layer cache
COPY requirements.prod.txt .

# Create an isolated virtual-env so we can copy it cleanly in stage 2
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.prod.txt


# ── Stage 2: runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="Meeting Task Manager — Backend"
LABEL org.opencontainers.image.description="FastAPI backend for Meeting Task Manager"

# Runtime OS deps only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Security: run as non-root ─────────────────────────────────
RUN groupadd --gid 1001 appgroup \
 && useradd  --uid 1001 --gid appgroup --shell /bin/sh --create-home appuser

WORKDIR /app

# Copy the virtual-env from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY --chown=appuser:appgroup . .

# Copy and make the entrypoint executable
RUN chmod +x /app/entrypoint.sh

# ── Runtime configuration ─────────────────────────────────────
# These are defaults; override them via Azure Container App
# environment variables — never bake secrets into the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=2 \
    LOG_LEVEL=info

# Azure Container Apps routes external traffic to this port
EXPOSE 8000

# ── Health check ──────────────────────────────────────────────
# Azure uses this to decide when the container is ready for traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
