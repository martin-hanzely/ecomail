from ecomail.campaign_stats_detail import CampaignStatsDetailSubscriber


class TestCampaignStatsDetailSubscriber:

    def test_from_dict(self):
        _d = {
            "open": 2,
            "send": 1,
            "unsub": 0,
            "soft_bounce": 0,
            "click": 0,
            "hard_bounce": 0,
            "out_of_band": 0,
            "spam": 0,
            "spam_complaint": 0,
            "mail_name": None
        }

        subscriber = CampaignStatsDetailSubscriber.from_dict("email@example.com", _d)

        assert subscriber.email == "email@example.com"
        assert subscriber.open == 2
        assert subscriber.send == 1
        assert subscriber.click == 0
