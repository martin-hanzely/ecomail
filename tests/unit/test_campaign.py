import datetime

from ecomail.campaign import Campaign, CampaignStatus


class TestCampaign:

    def test_from_dict(self):
        _d = {
            "id": 52,
            "from_name": "Example from name",
            "from_email": "sender@example.com",
            "reply_to": "replyto@example.com",
            "title": "Example title",
            "subject": "Example subject",
            "ga": None,
            "sent_at": "2024-10-01 17:02:21",
            "changed_at": "2024-10-01 17:02:28",
            "recipients": 401,
            "inserted": None,
            "status": 3,
            "scheduled_at": None,
            "template_id": 110,
            "archive_url": "https://example.com/archive/52",
            "attachments": None,
            "recepient_lists": [18]
        }

        campaign = Campaign.from_dict(_d)

        assert campaign.id == 52
        assert campaign.from_name == "Example from name"
        assert campaign.from_email == "sender@example.com"
        assert campaign.reply_to == "replyto@example.com"
        assert campaign.title == "Example title"
        assert campaign.subject == "Example subject"
        assert campaign.sent_at == datetime.datetime(2024, 10, 1, 17, 2, 21)
        assert campaign.recipients == 401
        assert campaign.status == CampaignStatus.SENT
