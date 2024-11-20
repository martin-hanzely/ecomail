from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from ecomail.campaign import Campaign
from ecomail.campaign_stats_detail import CampaignStatsDetail, CampaignStatsDetailSubscriber
from ecomail.exceptions import ApiConnectionError, ApiRequestError
from ecomail.subscriber import Subscriber


DEFAULT_TIMEOUT = 60  # 60s.


_mapping = dict[str, Any]
"""Type alias for mappings, eg. query and headers."""


@dataclass
class EcoMailOptions:
    """
    Internal options class for EcoMail service.
    """
    base_url: str
    api_key: str
    default_timeout: int = DEFAULT_TIMEOUT


class EcoMailService:
    """
    Connection service for EcoMail API.
    Docs: https://ecomailappapiv2.docs.apiary.io/#
    API is rate-limited 1000 calls for an API key per minute.
    Other request will be throttled with 429 return code and a Retry-After header.
    """
    _options: EcoMailOptions

    def __init__(self, options: EcoMailOptions) -> None:
        self._options = options

    def add_new_list(
        self,
        name: str,
        from_name: str,
        from_email: str,
        reply_to: str | None = None,
    ) -> int:
        """
        Creates new list of subscribers. Returns ID of newly created list.
        """
        response = self._call_add_new_list(
            name=name,
            from_name=from_name,
            from_email=from_email,
            reply_to=reply_to or from_email,  # Reply to from_email by default.
        )
        json_data: dict[str, Any] = response.json()
        try:
            return json_data["id"]
        except KeyError as exc:
            raise ApiConnectionError("List ID could not be retrieved.") from exc

    def add_new_subscriber_to_list(
        self,
        list_id: int,
        subscriber: Subscriber,
        trigger_autoresponders: bool = False,
    ) -> int:
        """
        Adds new subscriber to given list. Updates data if subscriber already exists.
        Does not force resubscribe. Returns ID of newly created subscriber.
        """
        response = self._call_add_new_subscriber_to_list(
            list_id=list_id,
            subscriber=subscriber,
            trigger_autoresponders=trigger_autoresponders
        )
        json_data: dict[str, Any] = response.json()
        try:
            return json_data["id"]
        except KeyError as exc:
            raise ApiConnectionError("Subscriber ID could not be retrieved.") from exc

    def add_bulk_subscribers_to_list(
        self,
        list_id: int,
        subscribers: list[Subscriber],
    ) -> None:
        """
        Adds new subscribers in bulk to given list. Updates existing subscribers.
        Bulk endpoint is limited to 3000 subscribers, subscribers over 3000 will be ignored.
        """
        if len(subscribers) > 3000:
            raise ApiRequestError("Bulk endpoint is limited to 3000 subscribers.")

        # Response status code is checked. Returns job ID. No need to pass anything to client.
        _ = self._call_add_bulk_subscribers_to_list(list_id, subscribers)

    def get_campaigns_list(self) -> list[Campaign]:
        """
        Returns list of campaigns.
        """
        response = self._call_get_campaigns_list_page()
        json_data: list[dict[str, Any]] = response.json()
        return [Campaign.from_dict(_c) for _c in json_data]

    def get_campaigns_stats_detail(self, campaign_id: int) -> CampaignStatsDetail:
        """
        Returns detailed statistics of campaign.
        """
        page = 1
        stats = CampaignStatsDetail(subscribers=[])
        while True:
            response = self._call_get_campaigns_stats_detail_page(campaign_id, page)
            json_data: dict[str, Any] = response.json()
            stats.subscribers.extend([
                CampaignStatsDetailSubscriber.from_dict(email=_e, data=_d)
                for _e, _d in json_data["subscribers"].items()
            ])

            if (total := json_data.get("total")) is not None and len(stats.subscribers) >= total:
                break
            if not json_data.get("next_page_url"):
                break
            page += 1
        return stats

    def get_subscriber_details(self, list_id: int, subscriber_email: str) -> Subscriber:
        """
        Returns details of subscriber from given list.
        """
        response = self._call_get_subscriber_details(list_id, subscriber_email)
        json_data: dict[str, Any] = response.json()
        return Subscriber.from_dict(json_data["subscriber"])

    def update_subscriber(self, list_id: int, subscriber_email: str, data: dict[str, Any]) -> None:
        """
        Updates subscriber data in given list.
        """
        _ = self._call_update_subscriber(list_id, subscriber_email, data)

    # region Private methods to call API endpoints.
    def _call_add_new_list(
        self,
        name: str,
        from_name: str,
        from_email: str,
        reply_to: str,
    ) -> requests.Response:
        """
        Calls "Lists/List Collections/Add new list" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/lists/list-collections/add-new-list
        """
        endpoint_path = "lists"
        data = {
            "name": name,
            "from_name": from_name,
            "from_email": from_email,
            "reply_to": reply_to,
        }
        return self._call_post(endpoint=endpoint_path, json=data)

    def _call_add_new_subscriber_to_list(
        self,
        list_id: int,
        subscriber: Subscriber,
        trigger_autoresponders: bool,
    ) -> requests.Response:
        """
        Calls "Lists/List subscribe/Add new subscriber to list" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/lists/list-subscribe/add-new-subscriber-to-list
        """
        endpoint_path = f"lists/{list_id}/subscribe"
        data = {
            "subscriber_data": subscriber.as_dict(),
            "update_existing": True,
            "resubscribe": False,
            # Trigger automations after subscribe.
            "trigger_autoresponders": trigger_autoresponders,
            # Skip double opt-in.
            "skip_confirmation": True,
            # trigger_notification  # (default: false) - Send subscribe notifications.
        }
        return self._call_post(endpoint=endpoint_path, json=data)

    def _call_add_bulk_subscribers_to_list(
        self,
        list_id: int,
        subscribers: list[Subscriber],
    ) -> requests.Response:
        """
        Calls "Lists/List subscribe bulk/Add bulk subscribers to list" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/lists/list-subscribe-bulk/add-bulk-subscribers-to-list
        """
        endpoint_path = f"lists/{list_id}/subscribe-bulk"
        data = {
            "subscriber_data": [_s.as_dict() for _s in subscribers],
            "update_existing": True,
        }
        return self._call_post(endpoint=endpoint_path, json=data)

    def _call_get_campaigns_list_page(self) -> requests.Response:
        """
        Calls "Campaigns/List campaigns/List campaigns" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/campaigns/campaigns-collection/list-all-campaigns
        """
        endpoint_path = "campaigns"
        return self._call_get(endpoint=endpoint_path, query={})

    def _call_get_campaigns_stats_detail_page(self, campaign_id: int, page: int) -> requests.Response:
        """
        Calls "Campaigns/Campaign stats/Get campaign stats" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/campaigns/get-campaign-stats-detail/get-campaign-stats-detail
        """
        endpoint_path = f"campaigns/{campaign_id}/stats-detail"
        return self._call_get(endpoint=endpoint_path, query={"page": page})

    def _call_get_subscriber_details(self, list_id: int, subscriber_email: str) -> requests.Response:
        """
        Calls "Lists/List subscribers/Get subscriber" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/lists/list-subscribe/get-subscriber
        """
        endpoint_path = f"lists/{list_id}/subscriber/{subscriber_email}"
        return self._call_get(endpoint=endpoint_path, query={})

    def _call_update_subscriber(self, list_id: int, subscriber_email: str, data: dict[str, Any]) -> requests.Response:
        """
        Calls "Lists/List subscribers/Update subscriber" api endpoint.
        https://ecomailappapiv2.docs.apiary.io/#reference/lists/list-subscribe/update-subscriber
        """
        endpoint_path = f"lists/{list_id}/update-subscriber"
        _d = {"email": subscriber_email, "subscriber_data": data}
        return self._call_put(endpoint=endpoint_path, json=_d)
    # endregion

    # region Generic API call methods.
    def _call_get(self, endpoint: str, query: _mapping) -> requests.Response:
        """
        Generic GET api call with provided parameters.
        Parameters override query and header defaults.
        """
        base_url = self._options.base_url
        response = requests.get(
            urljoin(base_url, endpoint),
            params=query,
            headers={"key": self._options.api_key},  # Authentication required.
            timeout=self._options.default_timeout,
        )
        try:
            response.raise_for_status()  # Raise exception if response status is not OK.
        except requests.HTTPError as exc:
            raise ApiConnectionError(response.text) from exc
        return response

    def _call_post(self, endpoint: str, json: _mapping) -> requests.Response:
        """
        Generic POST api call with provided parameters.
        Parameters override query and header defaults.
        """
        base_url = self._options.base_url
        response = requests.post(
            urljoin(base_url, endpoint),
            json=json,  # Data must be sent as JSON.
            headers={"key": self._options.api_key},  # Authentication required.
            timeout=self._options.default_timeout,
        )
        try:
            response.raise_for_status()  # Raise exception if response status is not OK.
        except requests.HTTPError as exc:
            raise ApiConnectionError(response.text) from exc
        return response

    def _call_put(self, endpoint: str, json: _mapping) -> requests.Response:
        """
        Generic PUT api call with provided parameters.
        Parameters override query and header defaults.
        """
        base_url = self._options.base_url
        response = requests.put(
            urljoin(base_url, endpoint),
            json=json,  # Data must be sent
            headers={"key": self._options.api_key},  # Authentication required.
            timeout=self._options.default_timeout,
        )
        try:
            response.raise_for_status()  # Raise exception if response status is not OK.
        except requests.HTTPError as exc:
            raise ApiConnectionError(response.text) from exc
        return response
    # endregion
