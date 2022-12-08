import pytest
from ecomail.subscriber import Subscriber


@pytest.fixture
def subscriber() -> Subscriber:
    """
    Dummy subscriber.
    """
    return Subscriber(
        name="John",
        surname="Doe",
        email="user@example.com",
        phone="123",
        country="SK",
    )
