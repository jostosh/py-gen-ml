"""Tests for the LanceDB generator fixtures."""
from __future__ import annotations

from pathlib import Path


def test_unit_lancedb_fixture_emits_models_and_helpers() -> None:
    source = Path(__file__).parent.joinpath('pgml_out_test', 'unit_lancedb.py').read_text()
    assert 'class LanceDBNestedMeta(LanceModel):' in source
    assert 'class LanceDBRecordTest(LanceModel):' in source
    assert 'embedding: Vector(4)' in source
    assert "return 'lance_records'" in source
    assert 'def create_lance_db_record_test_table(' in source
    assert 'db: DBConnection' in source
    assert ') -> LanceTable:' in source
    assert 'from lancedb.db import DBConnection' in source
    assert 'torch.utils.data.DataLoader' in source
