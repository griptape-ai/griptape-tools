import pytest
from griptape.artifacts import TextArtifact
from griptape.engines import QueryEngine


class TestTextProcessor:
    @pytest.fixture(autouse=True)
    def mock_openai_embedding_create(self, mocker):
        mocker.patch(
            "griptape.summarizers.PromptDriverSummarizer.summarize_text",
            return_value="foobar summary"
        )

    @pytest.fixture
    def processor(self):
        from griptape.tools import TextProcessor

        return TextProcessor(openai_api_key="foobar", query_engine=QueryEngine())

    def test_summarize(self, processor):
        artifact = TextArtifact("foobar")

        assert processor.summarize(
            {"artifacts": {"values": [artifact.to_dict()]}}
        ).value[0].value == "foobar summary"

    def test_query(self, processor):
        artifact = TextArtifact("foobar")

        assert processor.query(
            {"values": {"query": "foobar"}}
        ).value == "text artifacts not found"
