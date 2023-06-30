import json
import boto3
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseAwsClient


@define
class AwsS3Client(BaseAwsClient):
    session: boto3.session = field(kw_only=True)

    @activity(config={
        "description": "Lists all aws s3 buckets."
    })
    def list_s3_buckets(self, params: dict) -> BaseArtifact:
        try:
            session = self.session
            s3 = session.client('s3')
            buckets = s3.list_buckets()
            data = [{"{#BUCKET_NAME}": bucket["Name"]} for bucket in buckets['Buckets']]
            data = {"data": data}
            return TextArtifact(json.dumps(data))
        except Exception as e:
            return ErrorArtifact(f"error listing s3 buckets: {e}")

