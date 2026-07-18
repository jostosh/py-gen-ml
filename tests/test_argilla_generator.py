"""Source-level asserts for the Argilla generator fixture."""
from __future__ import annotations

from pathlib import Path


def test_unit_argilla_fixture_emits_settings_and_records() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_argilla.py').read_text()
    assert 'class ReviewExampleTest(BaseModel):' in source
    assert 'def build_review_example_test_settings(' in source
    assert 'rg.TextField' in source
    assert 'rg.LabelQuestion' in source
    assert 'def to_review_example_test_record(' in source
    assert 'def from_review_example_test_record(' in source
    assert 'record_metadata' in source


def test_unit_proto_annotates_argilla_slots() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'option (pgml.argilla)' in source
    assert 'slot: FIELD' in source
    assert 'slot: QUESTION' in source
    assert 'slot: METADATA' in source


def test_docs_flywheel_argilla_fixture_exists() -> None:
    path = (Path(__file__).resolve().parents[1] / 'docs' / 'snippets' / 'src' / 'pgml_out' / 'flywheel_demo_argilla.py')
    assert path.is_file()
    assert 'def build_review_example_settings(' in path.read_text()
