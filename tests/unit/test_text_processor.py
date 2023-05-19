import pytest
from griptape.artifacts import TextArtifact
from tests.utils import install_requirements
from tools import TextProcessor


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

    def test_summarize(self):
        artifact = TextArtifact("foobar")

        assert TextProcessor().summarize(
            {"artifacts": {"values": [artifact.to_dict()]}}
        ).value[0].value == "foobar summary"

    def test_query(self):
        artifact = TextArtifact("foobar")

        assert TextProcessor().query(
            {"values": {"query": "foobar"}}
        ).value == "text artifacts not found"
