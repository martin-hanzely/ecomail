from typing import Any

import pytest

from ecomail.exceptions import ApiConnectionError, ApiRequestError
from ecomail.service import EcoMailOptions, EcoMailService
from ecomail.subscriber import Subscriber


class MockResponse:
    """
    Mock response with empty JSON data.
    """
    def json(self, *args, **kwargs) -> dict[str, Any]:
        return {}


class TestEcoMailService:

    @pytest.fixture
    def service(self) -> EcoMailService:
        """
        Dummy service with test values.
        """
        options = EcoMailOptions(
            # Mock server provided by EcoMail.
            base_url="https://private-anon-ca420aae4b-ecomailappapiv2.apiary-mock.com/",
            # Dummy key.
            api_key="123_mock_key",
        )
        return EcoMailService(options=options)

    @pytest.fixture
    def subscriber(self) -> Subscriber:
        """
        Dummy subscriber.
        """
        return Subscriber(name="John", surname="Doe", email="user@example.com", phone="123")

    def test_add_new_list(self, service):
        list_id = service.add_new_list(
            name="Test list",
            from_name="My Organisation",
            from_email="organsation@example.com",
        )
        assert isinstance(list_id, int)

    def test_add_new_list__invalid_response(self, monkeypatch, service):
        monkeypatch.setattr(service, "_call_api", lambda *args, **kwargs: MockResponse())
        with pytest.raises(ApiConnectionError):
            _ = service.add_new_list(
                name="Test list",
                from_name="My Organisation",
                from_email="organsation@example.com",
            )

    def test_add_new_subscriber_to_list(self, service, subscriber):
        subscriber_id = service.add_new_subscriber_to_list(list_id=123, subscriber=subscriber)
        assert isinstance(subscriber_id, int)

    def test_add_new_subscriber_to_list__invalid_response(self, monkeypatch, service, subscriber):
        monkeypatch.setattr(service, "_call_api", lambda *args, **kwargs: MockResponse())
        with pytest.raises(ApiConnectionError):
             _ = service.add_new_subscriber_to_list(list_id=123, subscriber=subscriber)

    def test_add_bulk_subscribers_to_list(self, service, subscriber):
        subscribers = [subscriber for _ in range(100)]
        # Does not return anything.
        service.add_bulk_subscribers_to_list(list_id=123, subscribers=subscribers)

    def test_add_bulk_subscribers_to_list__too_many_subscribers(self, service, subscriber):
        subscribers = [subscriber for _ in range(3001)]
        with pytest.raises(ApiRequestError):
            service.add_bulk_subscribers_to_list(list_id=123, subscribers=subscribers)
