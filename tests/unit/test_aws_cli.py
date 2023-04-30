from griptape.artifacts import BaseArtifact

from griptape.tools import AwsCli


class TestAwsCli:
    def test_execute(self):
        assert isinstance(AwsCli().execute("aws help"), BaseArtifact)
