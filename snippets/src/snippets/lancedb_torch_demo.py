"""Insert dummy LanceDB rows and load them with LanceDB's PyTorch integration."""
from __future__ import annotations

import tempfile
from pathlib import Path

import lancedb
import pyarrow as pa
import torch
from torch.utils.data import DataLoader

from pgml_out.lancedb_demo_lancedb import (
    EmbeddingSample,
    SampleMeta,
    create_embedding_sample_table,
)


def collate_samples(batch: pa.Table) -> dict:
    """Convert an Arrow batch from LanceDB into tensors for training.

    LanceDB tables implement PyTorch's Dataset contract and yield Arrow batches
    via ``__getitems__``. For purely numeric scalar tables you can pass
    ``lancedb.util.tbl_to_tensor`` as ``collate_fn`` instead; this helper keeps
    string / vector / nested columns usable for our demo schema.
    See https://docs.lancedb.com/training/torch
    """
    return {
        'id': batch.column('id').to_pylist(),
        'embedding': torch.tensor(batch.column('embedding').to_pylist(), dtype=torch.float32),
        'label': [meta['label'] for meta in batch.column('meta').to_pylist()],
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = lancedb.connect(str(Path(tmp) / 'demo.lancedb'))
        table = create_embedding_sample_table(db, mode='overwrite')

        rows = [
            EmbeddingSample(
                id=f'sample-{i}',
                embedding=[float(i)] * 8,
                meta=SampleMeta(label='even' if i % 2 == 0 else 'odd', split_id=i % 3),
            ) for i in range(6)
        ]
        table.add(rows)

        # Pass the LanceDB table straight to DataLoader — no custom Dataset class.
        loader = DataLoader(table, batch_size=2, shuffle=False, collate_fn=collate_samples)
        batches = list(loader)
        assert len(batches) == 3
        first = batches[0]
        assert first['id'] == ['sample-0', 'sample-1']
        assert first['embedding'].shape == (2, 8)
        assert first['label'] == ['even', 'odd']

        print(f'loaded {sum(len(batch["id"]) for batch in batches)} rows across {len(batches)} batches')
        for batch_idx, batch in enumerate(batches):
            print(
                f'batch {batch_idx}: ids={list(batch["id"])} '
                f'embedding_shape={tuple(batch["embedding"].shape)}'
            )


if __name__ == '__main__':
    main()
