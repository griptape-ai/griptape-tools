from __future__ import annotations
import boto3
from schema import Schema, Literal
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseAwsClient

@define
class AwsIamClient(BaseAwsClient):
    session: boto3.session = field(kw_only=True)
    iam_client: boto3.client = field(
        default=Factory(lambda self: self.session.client("iam"), takes_self=True),
        kw_only=True
    )

    @activity(config={
        "description":"Can be used to list AWS MFA Devices"
    })
    def list_mfa_devices(self, params: dict) -> list[TextArtifact] | ErrorArtifact:
        try:
            devices = self.iam_client.list_mfa_devices()
            return [TextArtifact(str(d)) for d in devices["MFADevices"]]
        except Exception as e:
            return ErrorArtifact(f"error listing mfa devices")

    @activity(config={
        "description":"Can be used to list AWS IAM users."
    })
    def list_users(self, params: dict) -> list[TextArtifact] | ErrorArtifact:
        try:
            users = self.iam_client.list_users()
            return [TextArtifact(str(u)) for u in users["Users"]]
        except Exception as e:
            return ErrorArtifact(f"error listing s3 users")