# Database issues emulation Django

Database issues emulation Django

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy goodvibes

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Deployment

The following details how to deploy this application.

## PostgreSQL index demo

This project includes a small `shop` app to demonstrate redundant and unused PostgreSQL indexes.

Quick start:

1. Ensure your `DATABASE_URL` points to PostgreSQL.
2. Apply migrations:

       uv run python manage.py migrate

3. Reset index stats (optional, recommended):

       uv run python manage.py reset_index_stats

4. Seed demo data (adjust scale as needed):

       uv run python manage.py seed_demo_data --scale 1

5. Run biased workload to leave some indexes unused:

       uv run python manage.py simulate_load --seconds 120

6. Report index usage and sizes:

       uv run python manage.py report_indexes

Notes:
- Designed for PostgreSQL (uses partial, functional, and INCLUDE indexes, and pg_stat_* views).
- The workload favors a subset of access paths so others remain unused (idx_scan = 0).
