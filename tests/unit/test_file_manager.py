import os.path
import tempfile
import pytest
from griptape.artifacts import BlobArtifact, ListArtifact
from tests.utils import install_requirements
from griptape.tools import FileManager


@pytest.mark.usefixtures("install_requirements")
class TestFileManager:
    @pytest.fixture(scope="class")
    def install_requirements(self):
        install_requirements("file_manager")

    def test_load(self):
        result = FileManager(
            dir=os.path.abspath(os.path.dirname(__file__))
        ).load({"values": {"paths": ["resources/bitcoin.pdf"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], BlobArtifact)

    def test_save(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "foobar.txt")
            artifact = BlobArtifact(b"foobar", name="test.txt")
            result = FileManager().save({"values": {"paths": [path]}, "artifacts": {"values": [artifact.to_dict()]}})

            assert result.value == "saved successfully"
