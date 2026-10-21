import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.embedding_index import EmbeddingIndex

@pytest.fixture
def index():
    matrix = np.array([
        [1.0, 0.0],
        [0.8, 0.6],
        [0.0, 1.0],
    ], dtype=np.float32)
    return EmbeddingIndex([10, 20, 30], matrix)

def test_most_similar_ranks_by_score(index: EmbeddingIndex):
    results = index.most_similar(10, limit=2)

    assert [r.movielens_id for r in results] == [20, 30]
    assert results[0].score == pytest.approx(0.8)
    assert results[1].score == pytest.approx(0.0)


def test_most_similar_excludes_the_movie_itself(index: EmbeddingIndex):
    results = index.most_similar(10, limit=2)

    assert 10 not in [r.movielens_id for r in results]


def test_most_similar_respects_limit(index: EmbeddingIndex):
    assert len(index.most_similar(10, limit=1)) == 1


def test_has(index: EmbeddingIndex):
    assert index.has(20)
    assert not index.has(99)

