from __future__ import annotations

import dataclasses
import datetime
import enum


class CampaignStatus(enum.Enum):
    """
    Enum representing status of campaign.
    """
    DRAFT = 0
    PREPARING = 1
    SENDING = 2
    SENT = 3
    ERRORED = 4
    SCHEDULED = 7


@dataclasses.dataclass(kw_only=True, frozen=True)
class Campaign:
    """
    Campaign data. Requires keyword arguments. Frozen class (values cannot be reassigned).
    """
    id: int
    from_name: str
    from_email: str
    reply_to: str
    title: str
    subject: str
    sent_at: datetime.datetime | None = None
    recipients: int
    status: CampaignStatus

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Campaign:
        """
        Creates Campaign object from dict.
        """
        return cls(
            id=int(data["id"]),
            from_name=data["from_name"],
            from_email=data["from_email"],
            reply_to=data["reply_to"],
            title=data["title"],
            subject=data["subject"],
            sent_at=datetime.datetime.fromisoformat(data["sent_at"]) if data["sent_at"] else None,
            recipients=int(data["recipients"]),
            status=CampaignStatus(int(data["status"])),
        )
