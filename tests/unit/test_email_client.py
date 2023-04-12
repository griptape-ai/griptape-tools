import json
from griptape.tools import EmailClient


class TestEmailClient:
    def test_send(self):
        value = {
            "to": "foo@bar.com",
            "subject": "test",
            "body": "hello"
        }

        assert "error sending email" in EmailClient(
            host="",
            port=0,
            from_email=""
        ).send(json.dumps(value).encode())
