FROM node:22-slim AS client
WORKDIR /client
RUN corepack enable && corepack prepare pnpm@10 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
ARG VITE_FIREBASE_API_KEY
ENV VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY}
RUN pnpm build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements*.txt /app/backend/
ARG INSTALL_CLOUD=false
ARG INSTALL_AI=false
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    if [ "$INSTALL_CLOUD" = "true" ]; then pip install --no-cache-dir -r backend/requirements-cloud.txt; fi && \
    if [ "$INSTALL_AI" = "true" ]; then pip install --no-cache-dir -r backend/requirements-ai.txt; fi
COPY backend /app/backend
COPY --from=client /client/dist /app/frontend/dist
RUN useradd --create-home corvq && chown -R corvq:corvq /app
USER corvq
ENV PORT=8080
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
