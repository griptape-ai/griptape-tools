import json
import boto3
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseAwsClient

@define
class AwsPricingClient(BaseAwsClient):
    session: boto3.session = field(kw_only=True)

    @activity(config={
        "description": "Returns the account and IAM principal of the AWS credentials being used."
    })
    def get_product_pricing(self, params: dict) -> BaseArtifact:
        return TextArtifact("not yet implemented")
