import json
import os
import pytest
from tests.utils import install_requirements


@pytest.mark.usefixtures("install_requirements")
class TestWebScraper:
    @pytest.fixture(scope="class")
    def install_requirements(request):
        install_requirements("web_scraper")

    @pytest.fixture
    def scraper(self):
        from griptape.tools import WebScraper

        return WebScraper(openai_api_key=os.environ.get("OPENAI_API_KEY"))

    def test_get_title(self, scraper):
        assert isinstance(scraper.get_title(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_get_full_page(self, scraper):
        assert isinstance(scraper.get_full_page(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_get_authors(self, scraper):
        assert isinstance(scraper.get_authors(b"https://github.com/griptape-ai/griptape-tools"), list)

    def test_get_keywords(self, scraper):
        assert isinstance(scraper.get_keywords(b"https://github.com/griptape-ai/griptape-tools"), list)

    def test_summarize_page(self, scraper):
        assert isinstance(scraper.summarize_page(b"https://github.com/griptape-ai/griptape-tools"), str)

    def test_search_page(self, scraper):
        value = {
            "url": "https://github.com/griptape-ai/griptape-tools",
            "query": "what is this page about?"
        }

        assert isinstance(scraper.search_page(json.dumps(value).encode()), str)
