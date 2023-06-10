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
    base_url: str = field(
        factory=str,
    )
    path: Optional[str] = field(
        default=None,
        kw_only=True,
    )
    description: str = field(
        factory=str,
    )
    request_path_params_schema: Optional[str] = field(
        default=None,
        kw_only=True,
    )
    request_query_params_schema: Optional[str] = field(
        default=None,
        kw_only=True,
    )
    request_body_schema: Optional[str] = field(
        default=None,
        kw_only=True,
    )
    response_body_schema: Optional[str] = field(
        default=None,
        kw_only=True,
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
            "description": dedent(
                """
                This tool can be used to make a put request to the rest api url: "{{base_url}}{% if path %}/{{path}}{% endif %}".
                This rest api does the following: "{{description}}".
                {% if request_body_schema %}The request body must follow this JSON schema: {{request_body_schema}}{% endif %}.
                {% if response_body_schema %}The response body must follow this JSON schema: {{response_body_schema}}{% endif %}.
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
        base_url = self.value("base_url")
        path = self.value("path")
        body = values.get("body")
        url = self._build_url(base_url, path=path)

        try:
            response = put(url, data=body, timeout=30)

            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a patch request to the rest api url: "{{base_url}}{% if path %}/{{path}}{% endif %}".
                This rest api does the following: "{{description}}".
                {% if request_path_parameters %}The request path parameters must follow this JSON schema: {{request_path_params_schema}}{% endif %}.
                {% if request_body_schema %}The request body must follow this JSON schema: {{request_body_schema}}{% endif %}.
                {% if response_body_schema %}The response body must follow this JSON schema: {{response_body_schema}}{% endif %}.
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
        base_url = self.value("base_url")
        path = self.value("path")
        body = input_values.get("body")
        path_params = input_values.get("pathParams")
        url = self._build_url(base_url, path=path, path_params=path_params)

        try:
            response = patch(url, data=body, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a post request to the rest api url: "{{base_url}}{% if path %}/{{path}}{% endif %}".
                This rest api does the following: "{{description}}".
                {% if request_body_schema %}The request body must follow this JSON schema: {{request_body_schema}}{% endif %}.
                {% if response_body_schema %}The response body must follow this JSON schema: {{response_body_schema}}{% endif %}.
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
        base_url = self.value("base_url")
        path = self.value("path")
        url = self._build_url(base_url, path=path)
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
                This tool can be used to make a get request to the rest api url: "{{base_url}}{% if path %}/{{path}}{% endif %}".
                This rest api does the following: "{{description}}".
                {% if request_path_parameters %}The request path parameters must follow this JSON schema: {{request_path_params_schema}}{% endif %}.
                {% if request_query_parameters %}The request query parameters must follow this JSON schema: {{request_path_params_schema}}{% endif %}.
                {% if response_body_schema %}The response body must follow this JSON schema: {{response_body_schema}}{% endif %}.
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
        base_url = self.value("base_url")
        path = self.value("path")

        query_params = {}
        path_params = []
        if input_values:
            query_params = input_values.get("queryParams", {})
            path_params = input_values.get("pathParams", [])
        url = self._build_url(base_url, path=path, path_params=path_params)

        try:
            response = get(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": dedent(
                """
                This tool can be used to make a delete request to the rest api url: "{{base_url}}{% if path %}/{{path}}{% endif %}".
                This rest api does the following: "{{description}}".
                {% if request_path_parameters %}The request path parameters must follow this JSON schema: {{request_path_params_schema}}{% endif %}.
                {% if request_query_parameters %}The request query parameters must follow this JSON schema: {{request_path_params_schema}}{% endif %}.
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
        base_url = self.value("base_url")
        path = self.value("path")

        query_params = input_values.get("queryParams", {})
        path_params = input_values.get("pathParams", [])
        url = self._build_url(base_url, path=path, path_params=path_params)

        try:
            response = delete(url, params=query_params, timeout=30)
            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    def _build_url(self, base_url, path=None, path_params=None, query_params=None):
        url = base_url.strip('/')

        if path:
            url = f"{url}/{path.strip('/')}"
        if path_params:
            url = f"{url}/{str.join('/', path_params)}"

        return url
