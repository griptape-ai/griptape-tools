import pytest
from griptape.artifacts import TextArtifact


class TestMemoryExtractor:
    @pytest.fixture(autouse=True)
    def mock_summarize_text(self, mocker):
        mocker.patch(
            "griptape.summarizers.PromptDriverSummarizer.summarize_text",
            return_value="foobar summary"
        )

    @pytest.fixture
    def processor(self):
        from griptape.tools import MemoryExtractor

        return MemoryExtractor()

    def test_summarize(self, processor):
        artifact = TextArtifact("foobar")

        assert processor.summarize(
            {"artifacts": {"values": [artifact]}}
        ).value[0].value == "foobar summary"

    def test_query(self, processor):
        assert processor.search(
            {"values": {"query": "foobar"}}
        ).value == "no artifacts found"
