"""Source-level asserts for the PydanticAI generator fixture."""
from __future__ import annotations

from pathlib import Path


def test_unit_pydantic_ai_fixture_emits_full_partial_and_synthesize() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_pydantic_ai.py').read_text()
    assert 'class ReviewExampleTest(BaseModel):' in source
    assert 'class ReviewExampleTestPartial(BaseModel):' in source
    assert 'Field(description=' in source or 'Field(default=None, description=' in source
    assert 'def synthesize_review_example_test(' in source
    assert 'def _review_example_test_gap_model(' in source
    assert 'NativeOutput' in source
    assert 'description=' in source
    assert 'create_model' in source


def test_unit_proto_annotates_pydantic_ai() -> None:
    source = Path(__file__).parent.joinpath('protos', 'unit.proto').read_text()
    assert 'option (pgml.pydantic_ai)' in source


def test_docs_flywheel_pydantic_ai_fixture_exists() -> None:
    path = (
        Path(__file__).resolve().parents[1] / 'docs' / 'snippets' / 'src' / 'pgml_out' / 'flywheel_demo_pydantic_ai.py'
    )
    assert path.is_file()
    assert 'def synthesize_review_example(' in path.read_text()
