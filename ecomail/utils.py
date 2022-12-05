def is_empty_or_whitespace(string: str) -> bool:
    """
    Checks if provided string is empty or whitespace.
    """
    return string.isspace() or (len(string) == 0)
