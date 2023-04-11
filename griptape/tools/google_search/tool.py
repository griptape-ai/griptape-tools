from typing import Optional
import requests
from attr import define, field
from schema import Schema, Literal
from griptape.core import BaseTool, action


@define
class GoogleSearch(BaseTool):
    configs = {
        "search": {
            "name": "search",
            "description": "Used for searching Google.",
            "value_schema": Schema({
                Literal(
                    "value",
                    description="Google search request that returns a list of pages with titles, descriptions, and URLs"
                ): str
            })
        }
    }

    results_count: int = field(default=5, kw_only=True, metadata={"env": "GOOGLE_RESULTS_COUNT"})
    lang: str = field(default="lang_en", kw_only=True, metadata={"env": "GOOGLE_LANG"})
    api_search_key: Optional[str] = field(default=None, kw_only=True, metadata={"env": "GOOGLE_API_SEARCH_KEY"})
    api_search_id: Optional[str] = field(default=None, kw_only=True, metadata={"env": "GOOGLE_API_SEARCH_ID"})
    api_country: str = field(default="us", kw_only=True, metadata={"env": "GOOGLE_API_COUNTRY"})

    @action(config=configs["search"])
    def search(self, value: bytes) -> dict:
        try:
            return {
                "results": self._search_api(value.decode())
            }
        except Exception as e:
            return {
                "error": f"error searching Google: {e}"
            }

    def _search_api(self, query: str) -> list[dict]:
        url = f"https://www.googleapis.com/customsearch/v1?" \
              f"key={self.env_value('GOOGLE_API_SEARCH_KEY')}&" \
              f"cx={self.env_value('GOOGLE_API_SEARCH_ID')}&" \
              f"q={query}&" \
              f"start=0&" \
              f"lr={self.env_value('GOOGLE_LANG')}&" \
              f"num={self.env_value('GOOGLE_RESULTS_COUNT')}&" \
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
