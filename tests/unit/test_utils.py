import pytest

from ecomail.utils import is_empty_or_whitespace


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ("", True),
        ("    ", True),
        (" \t\r\n", True),
        (None, True),
        ("a", False),
        ("user@example.com", False),
    ]
)
def test_is_empty_or_whitespace(input, expected_output):
    assert is_empty_or_whitespace(input) is expected_output
