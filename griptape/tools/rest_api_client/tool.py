from textwrap import dedent
from typing import Optional
import schema
from schema import Schema, Literal
from attr import define, field
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact


@define
class RestApiClient(BaseTool):
    base_url: str = field(kw_only=True)
    path: str = field(default="", kw_only=True)
    description: Optional[str] = field(default=None, kw_only=True)
    request_path_params_schema: Optional[str] = field(default=None, kw_only=True)
    request_query_params_schema: Optional[str] = field(default=None, kw_only=True)
    request_body_schema: Optional[str] = field(default=None, kw_only=True)
    response_body_schema: Optional[str] = field(default=None, kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "base_url": self.base_url,
            "path": self.path,
            "description": self.description,
            "request_body_schema": self.request_body_schema,
            "request_query_params_schema": self.request_query_params_schema,
            "request_path_params_schema": self.request_path_params_schema,
            "response_body_schema": self.response_body_schema,
        }

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a put request to the rest api url: "{{base_url}}/{{path}}".
                This rest api does the following: "{{description}}".
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema({
                Literal(
                    "body",
                    description="The request body."
                ): dict,
            }),
        }
    )
    def put(self, params: dict) -> BaseArtifact:
        from requests import put, exceptions
        
        values = params["values"]
        base_url = self.base_url
        path = self.path
        body = values.get("body")
        url = f"{base_url}/{path}"

        try:
            response = put(url, data=body, timeout=30)

            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a post request to the rest api url: "{{base_url}}/{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema({
                Literal(
                    "pathParams",
                    description="The request path parameters."
                ): list,
                Literal(
                    "body",
                    description="The request body."
                ): dict,
            }),
        }
    )
    def patch(self, params: dict) -> BaseArtifact:
        from requests import patch, exceptions
        
        input_values = params["values"]
        base_url = self.base_url
        path = self.path
        body = input_values.get("body")
        path_params = input_values.get("pathParams")
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = patch(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a patch request to the rest api url: "{{base_url}}/{{path}}".
                This rest api does the following: "{{description}}".
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema({
                Literal("body", description="The request body."): dict,
            }),
        }
    )
    def post(self, params: dict) -> BaseArtifact:
        from requests import post, exceptions
        
        input_values = params["values"]
        base_url = self.base_url
        path = self.path
        url = f"{base_url}/{path}"
        body = input_values["body"]

        try:
            response = post(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a get request to the rest api url: "{{base_url}}/{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request query parameters must follow this JSON schema: {{request_path_params_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": schema.Optional(
                Schema({
                    schema.Optional(
                        Literal(
                            "queryParams",
                            description="The request query parameters.",
                        )
                    ): dict,
                    schema.Optional(
                        Literal(
                            "pathParams",
                            description="The request path parameters."
                        )
                    ): list,
                })
            ),
        }
    )
    def get(self, params: dict) -> BaseArtifact:
        from requests import get, exceptions
        
        input_values = params["values"]
        base_url = self.base_url
        path = self.path

        query_params = {}
        path_params = []
        if input_values:
            query_params = input_values.get("queryParams", {})
            path_params = input_values.get("pathParams", [])
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = get(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a get request to the rest api url: "{{base_url}}/{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request query parameters must follow this JSON schema: {{request_path_params_schema}}.
                """
            ),
            "schema": Schema({
                schema.Optional(
                    Literal(
                        "queryParams",
                        description="The request query parameters.",
                    )
                ): dict,
                schema.Optional(
                    Literal(
                        "pathParams", description="The request path parameters."
                    )
                ): list,
            }),
        }
    )
    def delete(self, params: dict = None) -> BaseArtifact:
        from requests import delete, exceptions
        
        input_values = params["values"]
        base_url = self.base_url
        path = self.path

        query_params = input_values.get("queryParams", {})
        path_params = input_values.get("pathParams", [])
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = delete(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))
