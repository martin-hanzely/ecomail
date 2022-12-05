def is_empty_or_whitespace(string: str | None) -> bool:
    """
    Checks if provided string is None, empty or whitespace.
    """
    return (string is None) or string.isspace() or (len(string) == 0)
