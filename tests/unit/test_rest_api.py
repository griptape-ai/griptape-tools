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
            client.post({"values": {"body": {}}}),
            BaseArtifact,
        )

    def test_post(self, client):
        assert isinstance(
            client.post({"values": {"body": {}}}),
            BaseArtifact,
        )

    def test_get_one(self, client):
        assert isinstance(
            client.get({"values": {"pathParams": ["1"]}}),
            BaseArtifact,
        )

    def test_get_all(self, client):
        assert isinstance(
            client.get({"values":{}}),
            BaseArtifact,
        )

    def test_get_filtered(self, client):
        assert isinstance(
            client.get({"values": {"queryParams": {"limit": 10}}}),
            BaseArtifact,
        )

    def test_delete_one(self, client):
        assert isinstance(
            client.delete({"values": {"pathParams": ["1"]}}),
            BaseArtifact,
        )

    def test_delete_multiple(self, client):
        assert isinstance(
            client.delete({"values": {"queryParams": {"ids": [1, 2]}}}),
            BaseArtifact,
        )

    def test_patch(self, client):
        assert isinstance(
            client.patch({"values": {"pathParams": ["1"], "body": {}}}),
            BaseArtifact,
        )
