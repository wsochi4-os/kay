---
name: python-dev
description: >
  Python development skill for Kutti. Use this for any Python development task
  including scripting, web development, data analysis, and automation.
triggers:
  - python
  - py
  - django
  - flask
  - fastapi
  - pandas
  - numpy
  - pytest
  - pip
priority: high
---

# Python Development

You are working on Python development tasks. Follow Python best practices and modern conventions.

## Language Features

### Python Version
- Target Python 3.10+ for new projects
- Use type hints (PEP 484)
- Use dataclasses for data containers
- Use pattern matching (Python 3.10+)

### Type Hints
```python
from typing import Optional, List, Dict, Any

def greet(name: str, times: int = 1) -> str:
    return name * times

class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
```

## Project Structure

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── __init__.py
│   ├── test_module1.py
│   └── test_module2.py
├── docs/
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Modern Python Tools

### pyproject.toml
Use `pyproject.toml` instead of `setup.py`:
```toml
[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
]
```

### Poetry
For dependency management:
```bash
# Install
poetry install

# Add dependency
poetry add requests

# Add dev dependency
poetry add pytest --group dev

# Run tests
poetry run pytest
```

## Web Frameworks

### FastAPI (Recommended)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Flask
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"data": "value"})

@app.route("/api/data", methods=["POST"])
def post_data():
    data = request.get_json()
    return jsonify({"received": data})
```

## Testing

### pytest
```python
# test_module.py
import pytest
from my_module import my_function

def test_my_function():
    result = my_function(2, 3)
    assert result == 5

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

Run tests:
```bash
pytest
pytest -v  # verbose
pytest tests/test_module.py  # specific file
pytest -k "test_my"  # filter by name
```

## Code Quality

### Formatting
- Use **Black** for code formatting
- Use **isort** for import sorting
- Use **flake8** or **ruff** for linting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
ruff check src/ tests/
```

### Configuration
```pyproject.toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I", "B", "C4", "UP"]
```

## Async/Await

```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    data = await fetch_data("https://api.example.com/data")
    print(data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Data Science

### Pandas
```python
import pandas as pd

# Read CSV
df = pd.read_csv("data.csv")

# Basic operations
print(df.head())
print(df.describe())
print(df.groupby("category").mean())

# Filter
df_filtered = df[df["column"] > 10]

# Apply function
df["new_column"] = df["existing_column"].apply(lambda x: x * 2)
```

### NumPy
```python
import numpy as np

# Create array
arr = np.array([1, 2, 3, 4, 5])

# Operations
mean = np.mean(arr)
std = np.std(arr)
dot_product = np.dot(arr, arr)

# Random
random_array = np.random.rand(10)
```

## Virtual Environments

```bash
# Create
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Deactivate
deactivate

# Install packages
pip install package-name

# Freeze requirements
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

## Common Patterns

### Context Managers
```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield
    finally:
        print(f"Elapsed: {time.time() - start:.2f}s")

with timer():
    # Code to time
    pass
```

### Decorators
```python
from functools import wraps
from typing import Callable, Any

def retry(max_attempts: int = 3):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
        return wrapper
    return decorator

@retry(max_attempts=3)
def unreliable_function():
    # Might fail
    pass
```

### Generators
```python
def fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
```

## Error Handling

```python
try:
    # Code that might raise
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except IOError as e:
    print(f"IO error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise if unexpected
else:
    print("Success!")
finally:
    print("Cleanup")
```

## Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```
