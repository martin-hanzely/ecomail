from typing import Any

import pytest

from ecomail.exceptions import ApiConnectionError, ApiRequestError
from ecomail.service import EcoMailOptions, EcoMailService


class MockResponse:
    """
    Mock response with empty JSON data.
    """
    _val = {}

    # noinspection PyUnusedLocal
    def json(self, *args, **kwargs) -> dict[str, Any]:
        return self._val


class TestEcoMailService:

    @pytest.fixture
    def service(self) -> EcoMailService:
        """
        Dummy service with test values.
        """
        options = EcoMailOptions(
            # Mock server provided by EcoMail.
            base_url="https://example.com",
            # Dummy key.
            api_key="123_mock_key",
        )
        return EcoMailService(options=options)

    def test_add_new_list(self, monkeypatch, service):
        class NewListMockResponse(MockResponse):
            """
            Mock response with list ID.
            """
            _val = {
                "name": "New list name",
                "id": 123
            }

        monkeypatch.setattr(
            service,
            "_call_add_new_list",
            lambda *args, **kwargs: NewListMockResponse(),  # TODO: Use real response!
        )

        list_id = service.add_new_list(
            name="Test list",
            from_name="My Organisation",
            from_email="organsation@example.com",
        )

        assert isinstance(list_id, int)
        assert list_id == 123

    def test_add_new_list__invalid_response(self, monkeypatch, service):
        monkeypatch.setattr(service, "_call_api", lambda *args, **kwargs: MockResponse())
        with pytest.raises(ApiConnectionError):
            _ = service.add_new_list(
                name="Test list",
                from_name="My Organisation",
                from_email="organsation@example.com",
            )

    def test_add_new_subscriber_to_list(self, monkeypatch, service, subscriber):
        class NewSubscriberMockResponse(MockResponse):
            """
            Mock response with subscriber ID.
            """
            _val = {
                "id": 123,
                "name": "Jan",
                "surname": "Novak",
                "email": "jan@example.com",
                "gender": None,
                "bounce_soft": 0,
                "bounced_hard": 0,
                "bounce_message": None,
                "inserted_at": "2024-10-21 01:00:00",
                "already_subscribed": True
            }

        monkeypatch.setattr(
            service,
            "_call_add_new_subscriber_to_list",
            lambda *args, **kwargs: NewSubscriberMockResponse(),
        )

        subscriber_id = service.add_new_subscriber_to_list(list_id=123, subscriber=subscriber)

        assert isinstance(subscriber_id, int)
        assert subscriber_id == 123

    def test_add_new_subscriber_to_list__invalid_response(self, monkeypatch, service, subscriber):
        monkeypatch.setattr(service, "_call_api", lambda *args, **kwargs: MockResponse())
        with pytest.raises(ApiConnectionError):
            _ = service.add_new_subscriber_to_list(list_id=123, subscriber=subscriber)

    def test_add_bulk_subscribers_to_list(self, monkeypatch, service, subscriber):
        class NewSubscribersBulkMockResponse(MockResponse):
            """
            Mock response with empty JSON data.
            """
            _val = {
                "inserts": 2
            }

        monkeypatch.setattr(
            service,
            "_call_add_bulk_subscribers_to_list",
            lambda *args, **kwargs: NewSubscribersBulkMockResponse(),
        )

        subscribers = [subscriber for _ in range(100)]
        # Does not return anything.
        service.add_bulk_subscribers_to_list(list_id=123, subscribers=subscribers)

    def test_add_bulk_subscribers_to_list__too_many_subscribers(self, monkeypatch, service, subscriber):
        # noinspection PyUnusedLocal
        def raise_error(*args, **kwargs):
            raise ApiRequestError("Too many subscribers")

        monkeypatch.setattr(
            service,
            "_call_api",
            lambda *args, **kwargs: raise_error(),
        )

        subscribers = [subscriber for _ in range(3001)]
        with pytest.raises(ApiRequestError):
            service.add_bulk_subscribers_to_list(list_id=123, subscribers=subscribers)
