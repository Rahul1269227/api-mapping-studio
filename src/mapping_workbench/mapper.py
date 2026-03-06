from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml


@dataclass(frozen=True)
class FieldDescriptor:
    path: str
    field_type: str
    required: bool


def load_openapi_spec(path: str | Path) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def extract_schema_fields(spec: Dict) -> Dict[str, List[FieldDescriptor]]:
    operations: Dict[str, List[FieldDescriptor]] = {}
    components = spec.get("components", {}).get("schemas", {})

    for endpoint, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            operation_id = operation.get("operationId", f"{method}_{endpoint}")
            collected: List[FieldDescriptor] = []

            request_body = operation.get("requestBody", {}).get("content", {})
            json_schema = request_body.get("application/json", {}).get("schema")
            if json_schema:
                collected.extend(_walk_schema(_resolve_schema(json_schema, components), components))

            for response in operation.get("responses", {}).values():
                response_schema = (
                    response.get("content", {})
                    .get("application/json", {})
                    .get("schema")
                )
                if response_schema:
                    collected.extend(_walk_schema(_resolve_schema(response_schema, components), components))

            operations[operation_id] = _dedupe_fields(collected)

    return operations


def suggest_mappings(source_spec: Dict, target_spec: Dict) -> Dict[str, List[Dict[str, object]]]:
    source_ops = extract_schema_fields(source_spec)
    target_ops = extract_schema_fields(target_spec)
    report: Dict[str, List[Dict[str, object]]] = {}

    for source_operation, source_fields in source_ops.items():
        mappings: List[Dict[str, object]] = []
        target_field_pool = list(_iter_fields(target_ops))

        for source_field in source_fields:
            best_match, score = _best_match(source_field, target_field_pool)
            if best_match and score >= 0.55:
                mappings.append(
                    {
                        "source_field": source_field.path,
                        "target_field": best_match.path,
                        "source_type": source_field.field_type,
                        "target_type": best_match.field_type,
                        "confidence": round(score, 3),
                    }
                )

        report[source_operation] = sorted(
            mappings,
            key=lambda item: item["confidence"],
            reverse=True,
        )

    return report


def format_report(source_path: str | Path, target_path: str | Path) -> str:
    source_spec = load_openapi_spec(source_path)
    target_spec = load_openapi_spec(target_path)
    report = {
        "source": str(source_path),
        "target": str(target_path),
        "mappings": suggest_mappings(source_spec, target_spec),
    }
    return json.dumps(report, indent=2)


def _iter_fields(operations: Dict[str, List[FieldDescriptor]]) -> Iterable[FieldDescriptor]:
    for fields in operations.values():
        yield from fields


def _best_match(
    source_field: FieldDescriptor,
    target_fields: Iterable[FieldDescriptor],
) -> Tuple[FieldDescriptor | None, float]:
    best_score = 0.0
    best_field: FieldDescriptor | None = None

    for target_field in target_fields:
        score = _score_fields(source_field, target_field)
        if score > best_score:
            best_score = score
            best_field = target_field

    return best_field, best_score


def _score_fields(source_field: FieldDescriptor, target_field: FieldDescriptor) -> float:
    source_name = source_field.path.split(".")[-1]
    target_name = target_field.path.split(".")[-1]
    name_score = SequenceMatcher(None, source_name.lower(), target_name.lower()).ratio()
    type_bonus = 0.15 if source_field.field_type == target_field.field_type else 0.0
    context_bonus = 0.1 if _shared_context(source_field.path, target_field.path) else 0.0
    return min(1.0, name_score + type_bonus + context_bonus)


def _shared_context(left: str, right: str) -> bool:
    return bool(set(left.split(".")[:-1]) & set(right.split(".")[:-1]))


def _resolve_schema(schema: Dict, components: Dict) -> Dict:
    if "$ref" not in schema:
        return schema
    ref_name = schema["$ref"].split("/")[-1]
    return components.get(ref_name, {})


def _walk_schema(schema: Dict, components: Dict, prefix: str = "") -> List[FieldDescriptor]:
    fields: List[FieldDescriptor] = []
    required = set(schema.get("required", []))

    for name, definition in schema.get("properties", {}).items():
        field_path = f"{prefix}.{name}" if prefix else name
        resolved = _resolve_schema(definition, components)
        field_type = resolved.get("type", definition.get("type", "object"))
        fields.append(FieldDescriptor(field_path, field_type, name in required))

        if resolved.get("type") == "object" or resolved.get("properties"):
            fields.extend(_walk_schema(resolved, components, field_path))

        if resolved.get("type") == "array" and "items" in resolved:
            item_schema = _resolve_schema(resolved["items"], components)
            if item_schema.get("type") == "object" or item_schema.get("properties"):
                fields.extend(_walk_schema(item_schema, components, f"{field_path}[]"))

    return fields


def _dedupe_fields(fields: List[FieldDescriptor]) -> List[FieldDescriptor]:
    unique: Dict[Tuple[str, str, bool], FieldDescriptor] = {}
    for field in fields:
        unique[(field.path, field.field_type, field.required)] = field
    return list(unique.values())
