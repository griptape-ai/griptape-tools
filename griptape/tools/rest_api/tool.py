from textwrap import dedent
import logging
from schema import Schema, Literal, Optional
from attr import define, field
from requests import post, get, delete, put, patch
from requests import exceptions
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact


@define
class RestApi(BaseTool):
    base_url: str = field(default="", kw_only=True, metadata={"env": "BASE_URL"})
    path: str = field(default="", kw_only=True, metadata={"env": "URL_PATH"})
    description: str = field(
        default="", kw_only=True, metadata={"env": "DESCRIPTION"}
    )
    request_path_params_schema: str = field(
        default="", kw_only=True, metadata={"env": "REQUEST_PATH_PARAMS_SCHEMA"}
    )
    request_query_params_schema: str = field(
        default="", kw_only=True, metadata={"env": "REQUEST_QUERY_PARAMS_SCHEMA"}
    )
    request_body_schema: str = field(
        default="", kw_only=True, metadata={"env": "REQUEST_BODY_SCHEMA"}
    )
    response_body_schema: str = field(
        default="", kw_only=True, metadata={"env": "RESPONSE_BODY_SCHEMA"}
    )

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
            "name": "put",
            "description": dedent(
                """
                This tool can be used to make a put request to the rest api url: "{{base_url}}{{path}}".
                This rest api does the following: "{{description}}".
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema(
                {
                    Literal("body", description="The request body."): dict,
                }
            ),
        }
    )
    def put(self, value: dict) -> BaseArtifact:
        base_url = self.env_value("BASE_URL")
        path = self.env_value("URL_PATH")
        body = value.get("body")
        url = f"{base_url}/{path}"

        try:
            response = put(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(err)

    @activity(
        config={
            "name": "patch",
            "description": dedent(
                """
                This tool can be used to make a post request to the rest api url: "{{base_url}}{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema(
                {
                    Literal(
                        "pathParams", description="The request path parameters."
                    ): list,
                    Literal("body", description="The request body."): dict,
                }
            ),
        }
    )
    def patch(self, value: dict) -> BaseArtifact:
        base_url = self.env_value("BASE_URL")
        path = self.env_value("URL_PATH")
        body = value.get("body")
        path_params = value.get("pathParams")
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = patch(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(err)

    @activity(
        config={
            "name": "post",
            "description": dedent(
                """
                This tool can be used to make a patch request to the rest api url: "{{base_url}}{{path}}".
                This rest api does the following: "{{description}}".
                The request body must follow this JSON schema: {{request_body_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Schema(
                {
                    Literal("body", description="The request body."): dict,
                }
            ),
        }
    )
    def post(self, value: dict) -> BaseArtifact:
        base_url = self.env_value("BASE_URL")
        path = self.env_value("URL_PATH")
        url = f"{base_url}/{path}"
        body = value["body"]

        try:
            response = post(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "name": "get",
            "description": dedent(
                """
                This tool can be used to make a get request to the rest api url: "{{base_url}}{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request query parameters must follow this JSON schema: {{request_path_params_schema}}.
                The response body must follow this JSON schema: {{response_body_schema}}.
                """
            ),
            "schema": Optional(
                Schema(
                    {
                        Optional(
                            Literal(
                                "queryParams",
                                description="The request query parameters.",
                            )
                        ): dict,
                        Optional(
                            Literal(
                                "pathParams", description="The request path parameters."
                            )
                        ): list,
                    }
                )
            ),
        }
    )
    def get(self, value: dict = None) -> BaseArtifact:
        base_url = self.env_value("BASE_URL")
        path = self.env_value("URL_PATH")

        query_params = {}
        path_params = []
        if value:
            query_params = value.get("queryParams", {})
            path_params = value.get("pathParams", [])
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = get(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(err)

    @activity(
        config={
            "name": "delete",
            "description": dedent(
                """
                This tool can be used to make a get request to the rest api url: "{{base_url}}{{path}}".
                This rest api does the following: "{{description}}".
                The request path parameters must follow this JSON schema: {{request_path_params_schema}}.
                The request query parameters must follow this JSON schema: {{request_path_params_schema}}.
                """
            ),
            "schema": Schema(
                {
                    Optional(
                        Literal(
                            "queryParams",
                            description="The request query parameters.",
                        )
                    ): dict,
                    Optional(
                        Literal(
                            "pathParams", description="The request path parameters."
                        )
                    ): list,
                }
            ),
        }
    )
    def delete(self, value: dict = None) -> BaseArtifact:
        base_url = self.env_value("BASE_URL")
        path = self.env_value("URL_PATH")

        query_params = value.get("queryParams", {})
        path_params = value.get("pathParams", [])
        url = f"{base_url}/{path}/{'/'.join(path_params)}"

        try:
            response = delete(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(err)
