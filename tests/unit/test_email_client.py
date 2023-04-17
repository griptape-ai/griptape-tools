import json
from griptape.tools import EmailClient


class TestEmailClient:
    def test_retrieve(self):
        value = {
            "label": "label_test",
            "key": "key_test",
            "search_criteria": "search_test"
        }

        assert "error retrieving email" in EmailClient(
            imap_url="",
            imap_user="",
            imap_password=""
        ).retrieve(json.dumps(value).encode())

    def test_send(self):
        value = {
            "to": "foo@bar.com",
            "subject": "test",
            "body": "hello"
        }

        assert "error sending email" in EmailClient(
            smtp_host="",
            smtp_port=0,
            smtp_from_email=""
        ).send(json.dumps(value).encode())
