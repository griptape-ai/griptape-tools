import pytest
from griptape.artifacts import TextArtifact
from griptape.engines import VectorQueryEngine
from griptape.tools import KnowledgeBaseClient


class TestKnowledgeBaseClient:
    @pytest.fixture(autouse=True)
    def mock_try_runt(self, mocker):
        mocker.patch(
            "griptape.drivers.OpenAiPromptDriver.try_run",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.drivers.OpenAiEmbeddingDriver.embed_chunk",
            return_value=[0, 1]
        )

    def test_search(self):
        tool = KnowledgeBaseClient(
            description="Test",
            query_engine=VectorQueryEngine()
        )

        assert tool.search({"values": {"query": "test"}}).value == "foobar"
        