from griptape.tools import GoogleCalClient


class TestGoogleCalClient:
    def test_get_upcoming_events(self):
        value = {
            "calendar_id": "primary"
        }
        assert "error retrieving calendar events" in GoogleCalClient(
            service_account_credentials={}
        ).get_upcoming_events({"values": value}).value
