# fast-llms-txt

Generate an `llms.txt` markdown manifest from your FastAPI OpenAPI schema for AI agents.

Inspired by the [llms.txt specification](https://llmstxt.org/) for LLM-friendly documentation.

## Installation

```bash
uv add fast-llms-txt
```

## Usage

```python
from fastapi import FastAPI
from fast_llms_txt import create_llms_txt_router

app = FastAPI(title="My API", description="A sample API")

@app.get("/users")
def list_users(limit: int = 10):
    """List all users."""
    return []

# Mount the llms.txt endpoint
app.include_router(create_llms_txt_router(app), prefix="/docs")
```

Now `GET /docs/llms.txt` returns:

```markdown
# My API

> A sample API

## Endpoints

- **GET /users** - List all users.
  - `limit` (integer, optional):
  - **Response** (200): Successful Response
```

## API

### `create_llms_txt_router(app, path="/llms.txt")`

Creates a FastAPI router that serves the llms.txt endpoint.

- `app`: Your FastAPI application instance
- `path`: The endpoint path (default: `/llms.txt`)

### `generate_llms_txt(openapi_schema)`

Directly convert an OpenAPI schema dict to llms.txt markdown string.

---

## Appendix: Release Procedure

### Versioning

This project uses [semantic versioning](https://semver.org/):
- **PATCH** (0.1.x): Bug fixes, no API changes
- **MINOR** (0.x.0): New features, backward compatible
- **MAJOR** (x.0.0): Breaking API changes

### Release Steps

Run the release script:
```bash
./scripts/release.sh 0.2.0
```

This will:
1. Update version in `pyproject.toml` and `fast_llms_txt/__init__.py`
2. Show diff and prompt for confirmation
3. Commit and tag
4. Optionally push (triggers PyPI publish via GitHub Actions)

### Infrastructure

- **PyPI**: [pypi.org/project/fast-llms-txt](https://pypi.org/project/fast-llms-txt/)
- **Trusted Publishing**: No tokens required; GitHub Actions authenticates via OIDC
- **Environment**: `release` environment in GitHub repo settings restricts publishing to `v*` tags
