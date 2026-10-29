import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from domain.chunking import Chunk, chunk_plot
from domain.embedding_text import build_chunk_embedding_text
from domain.evaluation import is_hit

def test_empty_whitespace():
    empty_chunks = chunk_plot(
        movielens_id=1,
        plot="",
        max_chars=800
    )
    whitespace_chunks = chunk_plot(
        movielens_id=2,
        plot="       ",
        max_chars=800
    )

    assert empty_chunks == []
    assert whitespace_chunks == []

def test_short_single_passage_plot():
    chunks = chunk_plot(
        movielens_id=1,
        plot="An American doctor and his wife, a former singing star, witness a murder while vacationing in Morocco",
        max_chars=800
    )
    index = chunks[0].chunk_index
    assert index == 0

def test_short_passages_plot():
    chunks = chunk_plot(
        movielens_id=1,
        plot="An American doctor and his wife\n\n, a former singing star, witness a murder while\n\n vacationing in Morocco",
        max_chars=800
    )
    assert len(chunks) == 1

def test_long_single_passage():
    chunks = chunk_plot(
        movielens_id=1,
        plot="12345678901234567890",
        max_chars=10
    )

    assert len(chunks) == 2
    assert [ c.chunk_index for c in chunks ] == [0, 1]

def test_index_no_gaps():
    chunks = chunk_plot(
        movielens_id=1,
        plot="Lucy Harmon, an American teenager is arriving in the lush Tuscan countryside to be sculpted by a family friend who lives in a beautiful villa. Lucy visited there four years earlier and exchanged a kiss with an Italian boy with whom she hopes to become reacquainted.",
        max_chars=100
    )
    assert [ c.chunk_index for c in chunks ] == list(range(len(chunks)))

def test_short_passages():
    chunks = chunk_plot(
        movielens_id=1,
        plot="aaa\n\nbbbbbbbbbbbb",
        max_chars=10
    )
    chunks_2 = chunk_plot(
        2,
        "aaa bbbccc",
        max_chars=7
    )

    assert [ c.text for c in chunks ] == ["aaa", "bbbbbbbbbb", "bb"]
    assert [ c.text for c in chunks_2 ] == ["aaa bbb", "ccc"]

def test_build_chunk_embedding_text():
    text_1 = build_chunk_embedding_text(
        title="Toy Story",
        year=1995,
        chunk_text="Woody is a cowboy."
    )
    text_2 = build_chunk_embedding_text(
        title="Toy Story",
        year=None,
        chunk_text="Woody is a cowboy."
    )

    assert text_1 == "Toy Story (1995). Woody is a cowboy."
    assert text_2 == "Toy Story. Woody is a cowboy."

def test_is_hit():
    assert is_hit([5, 7, 9], {7}) is True
    assert is_hit([5, 7, 9], {1, 2}) is False