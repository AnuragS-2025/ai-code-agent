# ==========================================
# STAGE 1: Build the React Frontend
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend dependency manifests
COPY frontend/package*.json ./
# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./
# Build the production assets
RUN npm run build

# ==========================================
# STAGE 2: Build the Python Backend & Runner
# ==========================================
FROM python:3.12-slim AS backend-runner
WORKDIR /app

# Install system dependencies required by static analysis tools or git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first to leverage Docker layer caching
COPY requirements.txt requirements-ci.txt ./

# Install backend dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-ci.txt

# Copy all application directories and files
COPY analyzers/ ./analyzers/
COPY api/ ./api/
COPY config/ ./config/
COPY context_engine/ ./context_engine/
COPY feedback/ ./feedback/
COPY git_automation/ ./git_automation/
COPY llm/ ./llm/
COPY parsers/ ./parsers/
COPY patch_engine/ ./patch_engine/
COPY project_index/ ./project_index/
COPY test_generator/ ./test_generator/
COPY validation/ ./validation/
COPY utils/ ./utils/
COPY pipeline.py app.py ./

# Create placeholder directories expected by the runtime setup
RUN mkdir -p logs uploads

# Copy built frontend assets from STAGE 1 over to the runner stage 
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose FastAPI default port
EXPOSE 8000

# Command to run the backend application server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]