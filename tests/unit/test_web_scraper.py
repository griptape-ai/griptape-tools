import json

import pytest
from tests.utils import install_requirements


@pytest.mark.usefixtures("install_requirements")
class TestWebScraper:
    @pytest.fixture(scope="class")
    def install_requirements(request):
        install_requirements("web_scraper")

    def test_get_title(self):
        from griptape.tools import WebScraper

        assert isinstance(WebScraper().get_title(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_get_full_page(self):
        from griptape.tools import WebScraper

        assert isinstance(WebScraper().get_full_page(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_get_authors(self):
        from griptape.tools import WebScraper

        assert isinstance(WebScraper().get_authors(b"https://github.com/griptape-ai/griptape-tools"), list)

    def test_get_keywords(self):
        from griptape.tools import WebScraper

        assert isinstance(WebScraper().get_keywords(b"https://github.com/griptape-ai/griptape-tools"), list)

    def test_summarize_page(self):
        from griptape.tools import WebScraper

        assert isinstance(WebScraper().summarize_page(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_search_page(self):
        from griptape.tools import WebScraper

        value = {
            "url": "https://github.com/griptape-ai/griptape-tools",
            "query": "what is this page about?"
        }

        assert isinstance(WebScraper().search_page(json.dumps(value).encode()), str)
