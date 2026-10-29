def build_embedding_text(
    title: str,
    year: int | None,
    genres: str | None,
    overview: str | None,
    tagline: str | None
) -> str | None:
    overview_clean = (overview or "").strip()
    tagline_clean = (tagline or "").strip()

    if not overview_clean and not tagline_clean:
        return None

    heading = f"{title} ({year})." if year is not None else f"{title}."
    parts = [
        heading, 
        f"{genres}." if genres else "", 
        overview_clean, 
        tagline_clean
    ]
    return " ".join(part for part in parts if part)

def build_chunk_embedding_text(
    title: str, 
    year: int | None, 
    chunk_text: str
) -> str:
    heading = f"{title} ({year})." if year is not None else f"{title}."
    return f"{heading} {chunk_text}"