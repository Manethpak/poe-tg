# Database Management

This directory contains database models, schemas, and migration tools for the Poe Telegram bot.

## Alembic Commands

### Initialize Alembic (first time only)
```bash
poetry run alembic init alembic
```

### Create a new migration
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Apply specific number of migrations
poetry run alembic upgrade +1
```

### Rollback migrations
```bash
# Rollback one migration
poetry run alembic downgrade -1

# Rollback to specific revision
poetry run alembic downgrade <revision_id>
```

### Check migration status
```bash
# Show current migration
poetry run alembic current

# Show migration history
poetry run alembic history

# Show pending migrations
poetry run alembic show <revision_id>
```

### Common workflow
1. Update models in `models.py`
2. Generate migration: `poetry run alembic revision --autogenerate -m "Add new feature"`
3. Review generated migration file
4. Apply migration: `poetry run alembic upgrade head`

## Files
- `models.py` - SQLAlchemy model definitions
- `schemas.py` - Pydantic schemas for API
- `database.py` - Database connection and utility functions