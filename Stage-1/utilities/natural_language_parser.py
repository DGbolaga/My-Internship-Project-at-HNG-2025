import re
from fastapi import HTTPException

def parse_natural_language_query(query: str) -> dict:
    """
    Parses a natural language query into structured filters.
    Supported patterns:
        - "all single word palindromic strings"
        - "strings longer than 10 characters"
        - "palindromic strings that contain the first vowel"
        - "strings containing the letter z"
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query = query.lower().strip()
    filters = {}

    # Match palindromic strings
    if re.search(r"\bpalindrom(ic|e)\b", query):
        filters["is_palindrome"] = True

    # Match "single word" or "two words"
    word_count_match = re.search(r"(\b\d+\b|\bsingle\b|\btwo\b|\bthree\b)\s+word", query)
    if word_count_match:
        mapping = {"single": 1, "one": 1, "two": 2, "three": 3}
        word_key = word_count_match.group(1)
        if word_key in mapping:
            filters["word_count"] = mapping[word_key]
        elif word_key.isdigit():
            filters["word_count"] = int(word_key)

    # Match "longer than X characters"
    if match := re.search(r"longer than (\d+)", query):
        filters["min_length"] = int(match.group(1)) + 1

    # Match "shorter than X characters"
    if match := re.search(r"shorter than (\d+)", query):
        filters["max_length"] = int(match.group(1)) - 1

    # Match "exactly X characters"
    if match := re.search(r"exactly (\d+)", query):
        length = int(match.group(1))
        filters["min_length"] = length
        filters["max_length"] = length

    # Match "containing the letter X"
    if match := re.search(r"contain(?:s|ing)?(?: the letter)? ([a-zA-Z])", query):
        filters["contains_character"] = match.group(1).lower()

    # Special case: "first vowel"
    if "first vowel" in query:
        filters["contains_character"] = "a"

    if not filters:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")

    if (
        "min_length" in filters
        and "max_length" in filters
        and filters["min_length"] > filters["max_length"]
    ):
        raise HTTPException(status_code=422, detail="Conflicting filters: min_length > max_length")

    return filters
