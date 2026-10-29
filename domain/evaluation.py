# For unit testing: if the chunk embeddings return expected passages

def is_hit(retrieved_ids: list[int], expected_ids: set[int]) -> bool:
    return any(movielens_id in expected_ids for movielens_id in retrieved_ids)