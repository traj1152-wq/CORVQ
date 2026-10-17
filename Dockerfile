FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements*.txt /app/backend/
ARG INSTALL_CLOUD=false
ARG INSTALL_AI=false
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    if [ "$INSTALL_CLOUD" = "true" ]; then pip install --no-cache-dir -r backend/requirements-cloud.txt; fi && \
    if [ "$INSTALL_AI" = "true" ]; then pip install --no-cache-dir -r backend/requirements-ai.txt; fi
COPY backend /app/backend
RUN useradd --create-home corvq && chown -R corvq:corvq /app
USER corvq
ENV PORT=8080
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
