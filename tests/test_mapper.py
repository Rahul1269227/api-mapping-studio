from pathlib import Path

from mapping_workbench.mapper import format_report, load_openapi_spec, suggest_mappings


BASE_DIR = Path(__file__).resolve().parents[1]


def test_mapping_report_contains_expected_fields() -> None:
    source = BASE_DIR / "examples" / "source_api.yaml"
    target = BASE_DIR / "examples" / "target_api.yaml"

    report_text = format_report(source, target)

    assert "createCustomer" in report_text
    assert "phoneNumber" in report_text
    assert "mobileNumber" in report_text


def test_mapping_suggestions_return_non_empty_matches() -> None:
    source = load_openapi_spec(BASE_DIR / "examples" / "source_api.yaml")
    target = load_openapi_spec(BASE_DIR / "examples" / "target_api.yaml")

    report = suggest_mappings(source, target)

    assert "createCustomer" in report
    assert report["createCustomer"]
    assert any(item["target_field"] == "mobileNumber" for item in report["createCustomer"])
