FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# ---------------------------
# Install system dependencies
# ---------------------------
# RUN apt-get update && apt-get install -y \
#     postgresql-client \
#     build-essential \
#     libpq-dev \
#     gcc \
#     curl \
#     bash \
#     && rm -rf /var/lib/apt/lists/*


# ---------------------------
# Copy uv project files
# ---------------------------
COPY r.txt .

# ---------------------------
# Install uv and create virtualenv
# ---------------------------
# RUN pip install --upgrade pip
# RUN pip install -r r.txt
RUN pip install -r r.txt


# ---------------------------
# Copy scripts and app code
# ---------------------------
COPY --chown=root:root --chmod=755 scripts /app/scripts

COPY .env /app/.env
COPY . .
RUN chmod -R +x /app/scripts

