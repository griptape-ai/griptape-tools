import pytest
from griptape.artifacts import TextArtifact
from tests.utils import install_requirements


@pytest.mark.usefixtures("install_requirements")
class TestTextProcessor:
    @pytest.fixture(autouse=True)
    def mock_openai_embedding_create(self, mocker):
        mocker.patch(
            "griptape.summarizers.PromptDriverSummarizer.summarize_text",
            return_value="foobar summary"
        )

    @pytest.fixture(scope="class")
    def install_requirements(request):
        install_requirements("text_processor")

    @pytest.fixture
    def processor(self):
        from griptape.tools import TextProcessor

        return TextProcessor()

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
