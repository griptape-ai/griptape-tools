import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import MemoryVectorDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestTextMemoryExtractor:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.summarizers.PromptDriverSummarizer.summarize_text",
            return_value="foobar summary"
        )

        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

    @pytest.fixture
    def processor(self):
        from griptape.tools import TextMemoryExtractor

        return TextMemoryExtractor(
            tool_memory=TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_driver=MemoryVectorDriver(
                        embedding_driver=MockEmbeddingDriver())))
        )

    def test_summarize(self, processor):
        processor.tool_memory.query_engine.vector_driver.upsert_text_artifact(
            TextArtifact("foobar"), namespace="foobar"
        )

        assert processor.summarize(
            {"values": {"artifact_namespace": "foobar"}}
        )[0].value == "foobar summary"

    def test_query(self, processor):
        assert processor.search(
            {"values": {"query": "foobar", "artifact_namespace": "foo"}}
        ).value == "foobar"
