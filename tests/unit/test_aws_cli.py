from griptape.artifacts import BaseArtifact
from griptape.tools import AwsCli


class TestAwsCli:
    def test_execute(self):
        tool = AwsCli(aws_access_key_id="foo", aws_secret_access_key="bar")

        assert isinstance(tool.execute({"values": {"command": "aws help"}}), BaseArtifact)
