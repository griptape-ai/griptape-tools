from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from schema import Schema, Literal
from typing import Optional, Union
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape import utils
from attr import define, field
import json
import boto3

class BaseAwsClient(BaseTool):
    session: boto3.session = field(default=None, kw_only=True)

@define
class AwsS3(BaseAwsClient):
    session: boto3.session = field(kw_only=True)

    @activity(config={
        "description": "Returns the account and IAM principal of the AWS credentials being used."
    })
    def get_current_aws_identity(self, params: dict) -> BaseArtifact:
        try:
            session = self.session
            sts = session.client('sts')
            return TextArtifact(str(sts.get_caller_identity()))
        except Exception as e:
            return ErrorArtifact(f"error getting current aws caller identity: {e}")

    @activity(config={
        "description": "Lists all aws s3 buckets."
    })
    def list_s3_buckets(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        try:
            session = self.session
            s3 = session.client('s3')
            return s3.list_buckets()
        except Exception as e:
            return ErrorArtifact(f"error listing s3 buckets: {e}")