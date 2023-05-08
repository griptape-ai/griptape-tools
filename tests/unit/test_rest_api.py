import pytest
from griptape.artifacts import BaseArtifact
from tests.utils import install_requirements


@pytest.mark.usefixtures("install_requirements")
class TestRestApi:
    @pytest.fixture(scope="class")
    def install_requirements(request):
        install_requirements("rest_api")

    @pytest.fixture
    def client(self):
        from griptape.tools import RestApi

        return RestApi()

    def test_put(self, client):
        assert isinstance(
            client.post({"body": {}}),
            BaseArtifact,
        )

    def test_post(self, client):
        assert isinstance(
            client.post({"body": {}}),
            BaseArtifact,
        )

    def test_get_one(self, client):
        assert isinstance(
            client.get({"pathParams": ["1"]}),
            BaseArtifact,
        )

    def test_get_all(self, client):
        assert isinstance(
            client.get(),
            BaseArtifact,
        )

    def test_get_filtered(self, client):
        assert isinstance(
            client.get({"queryParams": {"limit": 10}}),
            BaseArtifact,
        )

    def test_delete_one(self, client):
        assert isinstance(
            client.delete({"pathParams": ["1"]}),
            BaseArtifact,
        )

    def test_delete_multiple(self, client):
        assert isinstance(
            client.delete({"queryParams": {"ids": [1, 2]}}),
            BaseArtifact,
        )

    def test_patch(self, client):
        assert isinstance(
            client.patch({"pathParams": ["1"], "body": {}}),
            BaseArtifact,
        )
