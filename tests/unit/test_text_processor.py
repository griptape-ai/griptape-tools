import pytest
from griptape.artifacts import TextArtifact
from griptape.engines import VectorQueryEngine


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

        return TextProcessor(query_engine=VectorQueryEngine())

    def test_summarize(self, processor):
        artifact = TextArtifact("foobar")

        assert processor.summarize(
            {"artifacts": {"values": [artifact.to_dict()]}}
        ).value[0].value == "foobar summary"

    def test_query(self, processor):
        assert processor.search(
            {"values": {"query": "foobar"}}
        ).value == "no text supplied"
