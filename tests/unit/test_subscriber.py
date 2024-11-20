import pytest

from ecomail.exceptions import SubscriberError
from ecomail.subscriber import Subscriber


class TestSubscriber:

    def test___post_init___fails(self):
        with pytest.raises(SubscriberError):
            _ = Subscriber(name="John", surname="Doe", email="")

    def test_as_dict__all_fields(self):
        subscriber = Subscriber(name="John", surname="Doe", email="user@example.com", phone="123", country="CZ", tags=["tag1", "tag2"])
        _d = subscriber.as_dict()
        assert _d["name"] == "John"
        assert _d["surname"] == "Doe"
        assert _d["email"] == "user@example.com"
        assert _d["phone"] == "123"
        assert _d["country"] == "CZ"
        assert _d["tags"] == ["tag1", "tag2"]

    def test_as_dict__without_phone(self):
        subscriber = Subscriber(name="John", surname="Doe", email="user@example.com")
        _d = subscriber.as_dict()
        assert _d["name"] == "John"
        assert _d["surname"] == "Doe"
        assert _d["email"] == "user@example.com"
        assert "phone" not in _d

    def test_from_dict__all_fields(self):
        _d = {
            "name": "John",
            "surname": "Doe",
            "email": "user@example.com",
            "phone": "123",
            "country": "CZ",
            "tags": ["tag1", "tag2"],
        }
        subscriber = Subscriber.from_dict(_d)
        assert subscriber.name == "John"
        assert subscriber.surname == "Doe"
        assert subscriber.email == "user@example.com"
        assert subscriber.phone == "123"
        assert subscriber.country == "CZ"
        assert subscriber.tags == ["tag1", "tag2"]
