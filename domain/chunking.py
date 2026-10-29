from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Chunk:
    movielens_id: int
    chunk_index: int
    text: str

def chunk_plot(movielens_id: int, plot: str, max_chars: int = 800) -> list[Chunk]:
    paragraphs = [ p.strip() for p in plot.split("\n\n") if p.strip() ]
    pieces = [ piece for p in paragraphs for piece in _split_oversized(p, max_chars) ]
    return [ Chunk(movielens_id, i, t) for i, t in enumerate(_pack(pieces, max_chars)) ]


#region Helpers
def _split_oversized(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if len(sentence) <= max_chars:
            pieces.append(sentence)
        else:  # last resort: one sentence is still too long
            pieces.extend(sentence[i:i + max_chars] for i in range(0, len(sentence), max_chars))
    return pieces

def _pack(pieces: list[str], max_chars: int) -> list[str]:
    texts = []
    current = ""
    for piece in pieces:
        candidate = current + " " + piece if current else piece

        if len(candidate) <= max_chars:
            current = candidate
        else:
            texts.append(current)
            current = piece

    if current:
        texts.append(current)

    return texts