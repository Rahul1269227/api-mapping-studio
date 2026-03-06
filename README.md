# Dummy API Mapping Studio

Safe sample project for comparing two OpenAPI specs and generating field-level mapping suggestions without any organization-specific data.

## What It Does

- Loads two OpenAPI files
- Extracts request and response schema fields
- Suggests likely field mappings using name similarity and shared context
- Outputs a JSON report

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m mapping_workbench.cli \
  --source examples/source_api.yaml \
  --target examples/target_api.yaml
```

## Notes

- Only dummy sample APIs are included
- No credentials are required
- Generated reports are ignored by git
