from typing import Union
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal
from attr import define, field
import requests


@define
class ProxycurlClient(BaseTool):
    ENDPOINTS = {
        "profile": "https://nubela.co/proxycurl/api/v2/linkedin",
        "job": "https://nubela.co/proxycurl/api/linkedin/job",
        "company": "https://nubela.co/proxycurl/api/linkedin/company",
        "school": "https://nubela.co/proxycurl/api/linkedin/school",
    }

    proxycurl_api_key: str = field(kw_only = True)
    timeout = field(default = 30, kw_only = True)


    @activity(
        config={
            "description": "Can be used to get LinkedIn profile information from a person's profile",
            "schema": Schema({
                Literal(
                    "profile_id",
                    description="LinkedIn profile ID (i.e., https://www.linkedin.com/in/<profile_id>)"
                ): str
            }),
        }
    )
    def get_profile(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        return self._call_api("profile", params)

    @activity(
        config={
            "description": "Can be used to get LinkedIn job information from a job listing",
            "schema": Schema({
                Literal(
                    "job_id",
                    description="LinkedIn job ID (i.e., https://www.linkedin.com/jobs/view/<job_id>)"
                ): str
            }),
        }
    )
    def get_job(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        return self._call_api("job", params)

    @activity(
        config={
            "description": "Can be used to get LinkedIn company information from a company's profile",
            "schema": Schema({
                Literal(
                    "company_id",
                    description="LinkedIn company ID (i.e., https://www.linkedin.com/company/<company_id>)"
                ): str
            }),
        }
    )
    def get_company(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        return self._call_api("company", params)

    @activity(
        config={
            "description": "Can be used to get LinkedIn school information from a school's profile",
            "schema": Schema({
                Literal(
                    "school_id",
                    description="LinkedIn school ID (i.e., https://www.linkedin.com/school/<school_id>)"
                ): str
            }),
        }
    )
    def get_school(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        return self._call_api("school", params)

    def _call_api(self, endpoint_name: str, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        item_id = params["values"].get(f"{endpoint_name}_id")
        headers = {"Authorization": f"Bearer {self.proxycurl_api_key}"}
        linkedin_url = f"https://www.linkedin.com/{endpoint_name}/{item_id}"

        if endpoint_name == "profile":
            linkedin_url = f"https://www.linkedin.com/in/{item_id}"
        elif endpoint_name == "job":
            linkedin_url = f"https://www.linkedin.com/jobs/view/{item_id}"

        params = {"url": linkedin_url}

        response = requests.get(
            self.ENDPOINTS[endpoint_name], params = params, headers = headers, timeout = self.timeout
        )

        if response.status_code == 200 or response.status_code == 404:
            try:
                return [
                    TextArtifact(str({key: value}))
                    for key, value in response.json().items()
                ]
            except ValueError:
                return ErrorArtifact("Failed to decode JSON from response")

        elif response.status_code == 429:
            return ErrorArtifact('Usage rate limited. Retrying may be necessary.')
        elif response.status_code == 400:
            return ErrorArtifact(f'Invalid parameters provided. Refer to the Proxycurl documentation and message body for more info.\n {response.text}')
        elif response.status_code == 401:
            return ErrorArtifact('Invalid API Key')
        elif response.status_code == 403:
            return ErrorArtifact('You have run out of Proxycurl credits')
        elif response.status_code == 500:
            return ErrorArtifact('There is an error with the API. Please contact Proxycurl for assistance')
        else:
            return ErrorArtifact(f'Unknown error occurred. HTTP Status Code: {response.status_code}')
