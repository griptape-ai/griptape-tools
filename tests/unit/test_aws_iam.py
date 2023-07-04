from griptape.tools import AwsIamClient
import boto3


class TestAwsIamClient:
    def test_get_user_policy(self):
        value = {
            "user_name": "test_user",
            "policy_name": "test_policy"
        }
        assert "error returning policy document" in AwsIamClient(
            session=boto3.Session()
        ).get_user_policy({"values": value}).value

    def test_list_mfa_devices(self):
        assert "error listing mfa devices" in AwsIamClient(
            session=boto3.Session()
        ).list_mfa_devices({}).value

    def test_list_user_policies(self):
        value = {
            "user_name": "test_user"
        }
        assert "error listing iam user policies" in AwsIamClient(
            session=boto3.Session()
        ).list_user_policies({"values": value}).value

    def test_list_users(self):
        assert "error listing s3 users" in AwsIamClient(
            session=boto3.Session()
        ).list_users({}).value
