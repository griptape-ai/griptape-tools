from griptape.tools import WebSearch


class TestWebSearch:
    def test_search(self):
        assert isinstance(WebSearch().search(b"foo bar"), dict)
        