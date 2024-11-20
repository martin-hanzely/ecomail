import datetime
from typing import Any

import pytest

from ecomail.campaign import CampaignStatus
from ecomail.exceptions import ApiConnectionError, ApiRequestError
from ecomail.service import EcoMailOptions, EcoMailService
from tests.conftest import subscriber


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

    def test_get_campaigns_list(self, monkeypatch, service):
        class CampaignsListMockResponse(MockResponse):
            """
            Mock response with list of campaigns.
            """
            _val = [
                {
                    "id": 1,
                    "from_name": "From name",
                    "from_email": "from@foo.cz",
                    "reply_to": "reply@bar.cz",
                    "title": "My first campaign",
                    "subject": "First hello",
                    "ga": "ga_tracking_code",
                    "sent_at": "2014-09-08 22:04:03",
                    "changed_at": "2014-09-08 22:04:04",
                    "recipients": 1,
                    "inserted": "2014-09-08 14:41:31",
                    "status": 3,
                    "scheduled_at": None,
                    "template_id": 62,
                    "archive_url": "https://foo.ecomailapp.cz/campaigns/render/1",
                    "attachments": "N;"
                },
            ]

        monkeypatch.setattr(
            service,
            "_call_get_campaigns_list_page",
            lambda *args, **kwargs: CampaignsListMockResponse(),
        )

        campaigns = service.get_campaigns_list()

        assert isinstance(campaigns, list)
        assert len(campaigns) == 1

        campaign = campaigns[0]
        assert campaign.id == 1
        assert campaign.from_name == "From name"
        assert campaign.from_email == "from@foo.cz"
        assert campaign.reply_to == "reply@bar.cz"
        assert campaign.title == "My first campaign"
        assert campaign.subject == "First hello"
        assert campaign.sent_at == datetime.datetime(2014, 9, 8, 22, 4, 3)
        assert campaign.recipients == 1
        assert campaign.status == CampaignStatus.SENT

    def test_get_campaigns_stats_detail(self, monkeypatch, service):
        class CampaignsStatsDetailMockResponse(MockResponse):
            """
            Mock response with detailed statistics of campaign.
            """
            _val = {
                "next_page_url": None,
                "total": 2,
                "per_page": 100,
                "subscribers": {
                    "foo@bar.com": {
                        "open": 2,
                        "send": 1,
                        "unsub": 0,
                        "soft_bounce": 0,
                        "click": 1,
                        "hard_bounce": 0,
                        "out_of_band": 0,
                        "spam": 0,
                        "spam_complaint": 0
                    },
                    "foo2@bar.com": {
                        "open": 4,
                        "send": 1,
                        "unsub": 0,
                        "soft_bounce": 0,
                        "click": 2,
                        "hard_bounce": 0,
                        "out_of_band": 0,
                        "spam": 0,
                        "spam_complaint": 0
                    }
                }
            }

        monkeypatch.setattr(
            service,
            "_call_get_campaigns_stats_detail_page",
            lambda *args, **kwargs: CampaignsStatsDetailMockResponse(),
        )

        stats = service.get_campaigns_stats_detail(campaign_id=123)

        assert len(stats.subscribers) == 2

        subscriber1 = stats.subscribers[0]
        assert subscriber1.email == "foo@bar.com"
        assert subscriber1.open == 2
        assert subscriber1.send == 1
        assert subscriber1.click == 1

        subscriber2 = stats.subscribers[1]
        assert subscriber2.email == "foo2@bar.com"
        assert subscriber2.open == 4
        assert subscriber2.send == 1
        assert subscriber2.click == 2

    def test_get_subscriber_details(self, monkeypatch, service):
        class SubscriberDetailMockResponse(MockResponse):
            """
            Mock response with subscriber details.
            """
            _val = {
                "subscriber": {
                    "id": 1,
                    "name": "Jan",
                    "surname": "Novak",
                    "email": "user@example.com",
                    "phone": "123456789",
                    "tags": ["tag1", "tag2"],
                }
            }

        monkeypatch.setattr(
            service,
            "_call_get_subscriber_details",
            lambda *args, **kwargs: SubscriberDetailMockResponse(),
        )

        subscriber = service.get_subscriber_details(subscriber_email="user@example.com", list_id=123)

        assert subscriber.name == "Jan"
        assert subscriber.surname == "Novak"
        assert subscriber.email == "user@example.com"
        assert subscriber.phone == "123456789"
        assert subscriber.tags == ["tag1", "tag2"]

    def test_get_subscriber_details__not_found(self, monkeypatch, service):
        monkeypatch.setattr(service, "_call_api", lambda *args, **kwargs: MockResponse())
        with pytest.raises(ApiRequestError):
            _ = service.get_subscriber_details(subscriber_email="user@example.com", list_id=123)
