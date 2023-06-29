from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from schema import Schema, Literal
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape import utils
from attr import define, field

@define
class AwsCli(BaseTool):
    aws_access_key_id: str = field(kw_only=True)
    aws_secret_access_key: str = field(kw_only=True)
    aws_default_region: str = field(default="us-east-1", kw_only=True)
    aws_cli_policy: str = field(
        default="""{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}""",
        kw_only=True
    )

    @property
    def schema_template_args(self) -> dict:
        return {
            "policy": utils.minify_json(self.aws_cli_policy)
        }

    @activity(config={
        "description": "Can be used to execute AWS CLI v2 commands limited by this policy: {{ policy }}",
        "schema": Schema({
            Literal(
                "command",
                description="AWS CLI v2 command starting with 'aws'"
            ): str
        })
    })
    def execute(self, params: dict) -> BaseArtifact:
        command = params["values"]["command"]
        result = utils.CommandRunner().run(f"AWS_PAGER='' {command} --output json")

        if isinstance(result, ErrorArtifact):
            return result
        else:
            value = result.value

            if value == "":
                final_result = "[]"
            else:
                try:
                    final_result = utils.minify_json(value)
                except Exception:
                    final_result = value

            return TextArtifact(final_result)
