# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    postgresql-client \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# Ensure venv is used
ENV PATH="/opt/venv/bin:$PATH"



# Copy app code
COPY . .
# Explicitly copy Alembic config and migrations directory again to guarantee presence
COPY alembic.ini ./
COPY migrations ./migrations

# Build-time check: fail if alembic.ini is missing
RUN test -f /app/alembic.ini || (echo 'FATAL: alembic.ini missing after COPY' && exit 1)

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

# Ensure script.py.mako is present after all other COPYs
COPY migrations/script.py.mako ./migrations/script.py.mako

ENTRYPOINT ["python3", "/entrypoint.py"]

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
