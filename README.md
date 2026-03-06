# API Mapping Studio

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Small public-safe Python project for comparing two OpenAPI specs and generating field-level mapping suggestions.

## Features

- Parses source and target OpenAPI files
- Extracts nested request and response fields
- Suggests likely mappings using field-name similarity, type alignment, and shared path context
- Produces a JSON report that can be inspected or stored

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m mapping_workbench.cli \
  --source examples/source_api.yaml \
  --target examples/target_api.yaml \
  --output reports/mapping_report.json
```

## Run Tests

```bash
PYTHONPATH=src python3 -m pytest -q
```

## Demo

This repo is intended as a small portfolio-ready code sample rather than a hosted product. The fastest way to evaluate it is to run the CLI against the included example specs and inspect the generated JSON report.

## Project Layout

- `src/mapping_workbench`: mapping logic and CLI
- `examples/`: neutral sample OpenAPI documents
- `tests/`: unit tests for mapping behavior

## Safety

- Uses only dummy example data
- Contains no credentials or external service dependencies
- Ignores generated reports and local environment files
