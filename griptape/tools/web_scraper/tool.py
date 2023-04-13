from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import json
from typing import Union
from attr import define, field
from schema import Schema, Literal
from griptape.core import BaseTool, action

if TYPE_CHECKING:
    import GPTSimpleVectorIndex


@define
class WebScraper(BaseTool):
    openai_api_key: Optional[str] = field(default=None, kw_only=True, metadata={"env": "OPENAI_API_KEY"})
    include_links: bool = field(default=True, kw_only=True, metadata={"env": "INCLUDE_LINKS"})

    @action(config={
        "name": "get_title",
        "description": "Can be used to get the title of a web page",
        "value_schema": Schema({
            Literal(
                "value",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_title(self, value: bytes) -> str:
        return self._load_page(value.decode()).get("title")

    @action(config={
        "name": "get_full_page",
        "description": "Can be used to get all text content of a web page",
        "value_schema": Schema({
            Literal(
                "value",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_full_page(self, value: bytes) -> str:
        return self._load_page(value.decode()).get("text")

    @action(config={
        "name": "search_page",
        "description": "Can be used to search a specific web page",
        "value_schema": Schema({
            "value": {
                Literal(
                    "url",
                    description="Valid HTTP URL"
                ): str,
                Literal(
                    "query",
                    description="Search query"
                ): str
            }
        })
    })
    def search_page(self, value: bytes) -> str:
        params = json.loads(value.decode())
        index = self._to_vector_index(self._load_page(params["url"]).get("text"))

        return str(index.query(params["query"])).strip()

    @action(config={
        "name": "get_authors",
        "description": "Can be used to get a list of web page authors",
        "value_schema": Schema({
            Literal(
                "value",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_authors(self, value: bytes) -> list[str]:
        return [
            self._load_page(value.decode()).get("author")
        ]

    @action(config={
        "name": "get_keywords",
        "description": "Can be used to generate a list of keywords for a web page",
        "value_schema": Schema({
            Literal(
                "value",
                description="Valid HTTP URL"
            ): str
        })
    })
    def get_keywords(self, value: bytes) -> list[str]:
        index = self._to_vector_index(self._load_page(value.decode()).get("text"))
        keywords = str(index.query("Generate a comma-separated list of keywords for the following text"))

        return [w.strip() for w in keywords.split(",")]

    @action(config={
        "name": "summarize_page",
        "description": "Can be used to generate a web page summary",
        "value_schema": Schema({
            Literal(
                "value",
                description="Valid HTTP URL"
            ): str
        })
    })
    def summarize_page(self, value: bytes) -> str:
        index = self._to_vector_index(self._load_page(value.decode()).get("text"))

        return str(index.query("Generate a summary")).strip()

    def _to_vector_index(self, text: str) -> GPTSimpleVectorIndex:
        from llama_index import GPTSimpleVectorIndex, Document

        return GPTSimpleVectorIndex([
            Document(text)
        ])

    def _load_page(self, url: str) -> Union[dict, str]:
        import trafilatura
        from trafilatura.settings import use_config

        config = use_config()
        page = trafilatura.fetch_url(url)

        # This disables signal, so that trafilatura can work on any thread:
        # More info: https://trafilatura.readthedocs.io/en/latest/usage-python.html#disabling-signal
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

        if page is None:
            return "error: can't access URL"
        else:
            return json.loads(
                trafilatura.extract(
                    page,
                    include_links=self.env_value("INCLUDE_LINKS"),
                    output_format="json",
                    config=config
                )
            )
