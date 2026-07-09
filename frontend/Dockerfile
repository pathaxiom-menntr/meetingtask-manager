# ============================================================
#  Frontend — Production Dockerfile
#  Target: Azure Container Apps / Azure Container Instances
#
#  Strategy: three-stage build
#    Stage 1 (deps)     — installs node_modules
#    Stage 2 (builder)  — compiles the Next.js app
#    Stage 3 (runner)   — ships only the standalone output
#
#  next.config.ts must have  output: "standalone"
#  Result: slim ~200 MB image (no node_modules in runtime)
# ============================================================

# ── Stage 1: install dependencies ────────────────────────────
FROM node:20-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci


# ── Stage 2: build the Next.js app ───────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* vars are baked in at build time.
# Set your backend URL here or pass --build-arg from your CI pipeline.
ARG NEXT_PUBLIC_API_URL=https://your-backend.azurecontainerapps.io
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build


# ── Stage 3: minimal runtime ─────────────────────────────────
FROM node:20-alpine AS runner

LABEL org.opencontainers.image.title="Meeting Task Manager — Frontend"
LABEL org.opencontainers.image.description="Next.js frontend for Meeting Task Manager"

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# ── Security: run as non-root ─────────────────────────────────
RUN addgroup --gid 1001 --system appgroup \
 && adduser  --uid 1001 --system --ingroup appgroup appuser

# Only copy what Next.js standalone needs at runtime
COPY --from=builder --chown=appuser:appgroup /app/public            ./public
COPY --from=builder --chown=appuser:appgroup /app/.next/standalone  ./
COPY --from=builder --chown=appuser:appgroup /app/.next/static      ./.next/static

EXPOSE 3000

# ── Health check ──────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

USER appuser

# next.js standalone entry point
CMD ["node", "server.js"]
