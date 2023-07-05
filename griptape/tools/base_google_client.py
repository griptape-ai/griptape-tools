from abc import ABC
from attr import define, field
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


@define
class BaseGoogleClient(BaseTool, ABC):
    service_account_credentials: str = field(kw_only=True)
