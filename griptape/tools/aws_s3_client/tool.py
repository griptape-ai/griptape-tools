from __future__ import annotations
import boto3
from schema import Schema, Literal
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core.decorators import activity
from griptape.tools import BaseAwsClient

@define
class AwsS3Client(BaseAwsClient):
    session: boto3.session = field(kw_only=True)
    s3_client: boto3.client = field(
        default=Factory(lambda self: self.session.client("s3"), takes_self=True)
    )

    @activity(config={
        "description": "Retruns the access control list(ACL) of an bucket.",
        "schema": Schema({
            Literal(
                "Bucket",
                description="The bucket name that contains the object for which to get the ACL information."
            ): str
        })
    })
    def get_bucket_acl(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            acl = self.s3_client.get_bucket_acl(
                Bucket=params["values"]["Bucket"]
            )
            return TextArtifact(acl)
        except Exception as e:
            return ErrorArtifact(f"error getting bucket acl: {e}")

    @activity(config={
        "description": "Returns the policy of a specified bucket",
        "schema": Schema({
            Literal(
                "Bucket",
                description="The bucket name for which to get the bucket policy."
            ): str
        })
    })
    def get_bucket_policy(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            policy = self.s3_client.get_bucket_policy(
                Bucket=params["values"]["Bucket"]
            )
            return TextArtifact(policy)
        except Exception as e:
            return ErrorArtifact(f"error getting bucket policy: {e}")

    @activity(config={
        "description":"Retruns the access control list(ACL) of an object.",
        "schema": Schema({
            Literal(
                "Object",
                description="The bucket name that contains the object for which to get the ACL information."
            ): str,
            Literal(
                "Key",
                description="The key of the object for which to get the ACL information."
            ): str
        })
    })
    def get_object_acl(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            acl = self.s3_client.get_object_acl(
                Bucket=params["values"]["Bucket"],
                Key=params["values"]["Key"]
            )
            return TextArtifact(acl)
        except Exception as e:
            return ErrorArtifact(f"error getting object acl: {e}")

    @activity(config={
        "description": "Lists all aws s3 buckets."
    })
    def list_s3_buckets(self, params: dict) -> list[TextArtifact] | ErrorArtifact:
        try:
            buckets = self.s3_client.list_buckets()
            return [TextArtifact(str(b)) for b in buckets["Buckets"]]
        except Exception as e:
            return ErrorArtifact(f"error listing s3 buckets: {e}")

    @activity(config={
        "description": "Lists all objects in an S3 bucket.",
        "schema": Schema({
            Literal(
                "Bucket",
                description="The name of the S3 bucket to list."
            ): str
        })
    })
    def list_objects(self, params: dict) -> list[TextArtifact] | ErrorArtifact:
        try:
            objects = self.s3_client.list_objects_v2(
                Bucket=params["values"]["Bucket"]
            )
            return [TextArtifact(str(o)) for o in objects["Contents"]]
        except Exception as e:
            return ErrorArtifact(f"error listing objects in bucket: {e}")
