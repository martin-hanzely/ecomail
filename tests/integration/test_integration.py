import os

import pytest

from ecomail.service import EcoMailOptions, EcoMailService


class TestIntegration:

    @pytest.fixture
    def service(self) -> EcoMailService:
        """
        Dummy service with test values.
        """
        api_key = os.getenv("ECOMAIL_API_KEY")
        if api_key is None:
            raise ValueError(f"Missing configuration key: ECOMAIL_API_KEY.")

        options = EcoMailOptions(
            # Debug proxy server provided by EcoMail.
            base_url="http://private-anon-ee165f5762-ecomailappapiv2.apiary-proxy.com/",
            api_key=api_key,
        )
        return EcoMailService(options=options)

    def test_add_new_list(self, service):
        list_id = service.add_new_list(
            name="Test list",
            from_name="My Organisation",
            from_email="organsation@example.com",
        )
        assert isinstance(list_id, int)

    def test_add_new_subscriber_to_list(self, service, subscriber):
        subscriber_id = service.add_new_subscriber_to_list(list_id=1, subscriber=subscriber)
        assert isinstance(subscriber_id, int)

    def test_add_bulk_subscribers_to_list(self, service, subscriber):
        subscribers = [subscriber for _ in range(100)]
        # Does not return anything.
        service.add_bulk_subscribers_to_list(list_id=1, subscribers=subscribers)
