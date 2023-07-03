from griptape.tools import AwsIamClient
import boto3


class TestAwsIamClient:
    def test_list_iam_user(self):
        assert "error listing s3 users" in AwsIamClient(
            session=boto3.Session()
        ).list_users({}).value
