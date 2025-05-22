# The builder image, used to build the virtual environment
FROM python:3.10-buster AS builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy all project files needed for installation
COPY pyproject.toml poetry.lock README.md ./
COPY poe_tg ./poe_tg

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-buster AS runtime

# Create non-root user
RUN groupadd -r botuser && useradd -r -g botuser botuser

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app/poe_tg ./poe_tg

# Change ownership of application files
RUN chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Add health check
HEALTHCHECK CMD python -c "import sys; sys.exit(0)"

# Use exec form of ENTRYPOINT for proper signal handling
ENTRYPOINT ["python", "-m", "poe_tg.main"]