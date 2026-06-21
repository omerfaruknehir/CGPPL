# Testing

Run the implemented CGPPL test suite locally with:

```bash
python -m pip install -e .[dev]
pytest
```

A GitHub Actions workflow in `.github/workflows/tests.yml` runs the same pytest command on pushes to `main` and on pull requests.
