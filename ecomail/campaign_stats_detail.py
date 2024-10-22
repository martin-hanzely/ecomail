from __future__ import annotations

import dataclasses


@dataclasses.dataclass(kw_only=True, frozen=True)
class CampaignStatsDetail:
    """
    Campaign statistics detail data. Requires keyword arguments. Frozen class (values cannot be reassigned).
    """
    subscribers: list[CampaignStatsDetailSubscriber]


@dataclasses.dataclass(kw_only=True, frozen=True)
class CampaignStatsDetailSubscriber:
    """
    Subscriber detail data for campaign statistics. Requires keyword arguments. Frozen class (values cannot be reassigned).
    """
    email: str
    open: int
    send: int
    click: int

    @classmethod
    def from_dict(cls, email: str, data: dict[str, str]) -> CampaignStatsDetailSubscriber:
        """
        Creates CampaignStatsDetailSubscriber object from dict.
        """
        return cls(
            email=email,
            open=int(data["open"]),
            send=int(data["send"]),
            click=int(data["click"]),
        )
