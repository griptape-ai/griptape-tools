import json
from typing import Optional
from schema import Schema
from griptape.core import BaseTool, action, utils
from attr import define, field


@define
class AwsCli(BaseTool):
    aws_access_key_id: Optional[str] = field(default=None, kw_only=True, metadata={"env": "AWS_ACCESS_KEY_ID"})
    aws_secret_access_key: Optional[str] = field(default=None, kw_only=True, metadata={"env": "AWS_SECRET_ACCESS_KEY"})
    aws_default_region: str = field(default="us-east-1", kw_only=True, metadata={"env": "AWS_DEFAULT_REGION"})
    aws_cli_policy: Optional[str] = field(default=None, kw_only=True, metadata={"env": "AWS_CLI_POLICY"})

    @property
    def schema_template_args(self) -> dict:
        return {
            "policy": json.dumps(utils.minify_json(self.env_value("AWS_CLI_POLICY"))).strip('"')
        }

    @action(config={
        "name": "execute",
        "description": "Can be used to execute AWS CLI v2 commands limited by this policy: {{ policy }}",
        "schema": Schema(
            str,
            description="AWS CLI v2 command"
        )
    })
    def execute(self, value: bytes) -> str:
        result = utils.CommandRunner().run(f"AWS_PAGER='' {value.decode()} --output json")

        if result == "":
            return "[]"
        else:
            try:
                final_result = utils.minify_json(result)
            except Exception:
                final_result = result

            return final_result
