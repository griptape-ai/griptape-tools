import pytest
from griptape.artifacts import TextArtifact, CsvRowArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.tools import TextMemoryBrowser


class TestTextMemoryBrowser:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.engines.PromptSummaryEngine.summarize_artifacts",
            return_value=TextArtifact("foobar summary")
        )

        mocker.patch(
            "griptape.engines.CsvExtractionEngine.extract",
            return_value=[CsvRowArtifact({"foo": "bar"})]
        )

    @pytest.fixture
    def tool(self):
        return TextMemoryBrowser(
            input_memory=[TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver()
                    )
                )
            )]
        )

    def test_summarize(self, tool):
        assert tool.summarize(
            {"values": {"memory_id": tool.input_memory[0].id, "artifact_namespace": "foo"}}
        ).value == "foobar summary"

    def test_query(self, tool):
        assert tool.search(
            {"values": {"query": "foobar", "memory_id": tool.input_memory[0].id, "artifact_namespace": "foo"}}
        ).value == "foobar"

    def test_extract(self, tool):
        assert tool.extract(
            {"values": {"column_names": "foo", "memory_id": tool.input_memory[0].id, "artifact_namespace": "foo"}}
        )[0].value == {"foo": "bar"}