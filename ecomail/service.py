from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from ecomail.exceptions import ApiConnectionError, ApiRequestError
from ecomail.subscriber import Subscriber


_mapping = dict[str, Any]
"""Type alias for mappings, eg. query and headers."""


@dataclass
class EcoMailOptions:
    """
    Internal options class for EcoMail service.
    """
    base_url: str
    api_key: str


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
        response = self._call_add_new_list(name, from_name, from_email, reply_to)
        json_data: dict[str, Any] = response.json()
        try:
            return json_data["id"]
        except KeyError as exc:
            raise ApiConnectionError("List ID could not be retrieved.") from exc

    def add_new_subscriber_to_list(
        self,
        list_id: int,
        subscriber: Subscriber,
    ) -> int:
        """
        Adds new subscriber to given list. Updates data if subscriber already exists.
        Does not force resubscribe. Returns ID of newly created subscriber.
        """
        response = self._call_add_new_subscriber_to_list(list_id, subscriber)
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

    def _call_add_new_list(
        self,
        name: str,
        from_name: str,
        from_email: str,
        reply_to: str | None = None,
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
            "reply_to": reply_to or from_email,  # Reply to from_email by default.
        }
        return self._call_api(endpoint=endpoint_path, json=data, headers={})

    def _call_add_new_subscriber_to_list(
        self,
        list_id: int,
        subscriber: Subscriber,
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
            # trigger_autoresponders  # (default: false) - Trigger automations after subscribe.
            # trigger_notification  # (default: false) - Send subscribe notifications.
            "skip_confirmation": True, # Skip double opt-in.
        }
        return self._call_api(endpoint=endpoint_path, json=data, headers={})

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
        return self._call_api(endpoint=endpoint_path, json=data, headers={})

    def _call_api(self, endpoint: str, json: _mapping, headers: _mapping) -> requests.Response:
        """
        Generic api call with provided parameters. Parameters override query and header defaults.
        """
        base_url = self._options.base_url
        response = requests.post(
            urljoin(base_url, endpoint),
            json=json,  # Data must be sent as JSON.
            headers={"key": self._options.api_key} | headers,  # Authentication required.
            timeout=60,
        )
        try:
            response.raise_for_status()  # Raise exception if response status is not OK.
        except requests.HTTPError as exc:
            raise ApiConnectionError(f"Cannot connect to endpoint: {endpoint}") from exc
        return response
