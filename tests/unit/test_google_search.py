from griptape.tools import GoogleSearch


class TestGoogleSearch:
    def test_search(self):
        assert isinstance(GoogleSearch().search(b"foo bar"), dict)
        