from typing import Optional
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from schema import Schema
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class WebSearch(BaseTool):
    results_count: int = field(default=5, kw_only=True, metadata={"env": "SEARCH_RESULTS_COUNT"})
    google_api_lang: str = field(default="lang_en", kw_only=True, metadata={"env": "GOOGLE_API_LANG"})
    google_api_key: Optional[str] = field(default=None, kw_only=True, metadata={"env": "GOOGLE_API_KEY"})
    google_api_search_id: Optional[str] = field(default=None, kw_only=True, metadata={"env": "GOOGLE_API_SEARCH_ID"})
    google_api_country: str = field(default="us", kw_only=True, metadata={"env": "GOOGLE_API_COUNTRY"})

    @activity(config={
        "name": "search",
        "description": "Can be used for searching the web",
        "schema": Schema(
            str,
            description="Search engine request that returns a list of pages with titles, descriptions, and URLs"
        )
    })
    def search(self, value: str) -> BaseArtifact:
        try:
            return TextArtifact(str(self._search_google(value)))
        except Exception as e:
            return ErrorArtifact(f"error searching Google: {e}")

    def _search_google(self, query: str) -> list[dict]:
        import requests

        url = f"https://www.googleapis.com/customsearch/v1?" \
              f"key={self.env_value('GOOGLE_API_KEY')}&" \
              f"cx={self.env_value('GOOGLE_API_SEARCH_ID')}&" \
              f"q={query}&" \
              f"start=0&" \
              f"lr={self.env_value('GOOGLE_API_LANG')}&" \
              f"num={self.env_value('SEARCH_RESULTS_COUNT')}&" \
              f"gl={self.env_value('GOOGLE_API_COUNTRY')}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            links = [{
                "url": r["link"],
                "title": r["title"],
                "description": r["snippet"],
            } for r in data["items"]]

            return links
        else:
            raise Exception(f"Google Search API returned an error with status code "
                            f"{response.status_code} and reason '{response.reason}'")
