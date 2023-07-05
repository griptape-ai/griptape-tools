from abc import ABC
from attr import define, field
from griptape.core import BaseTool

@define
class BaseGoogleClient(BaseTool, ABC):
    service_account_credentials_path: str = field(kw_only=True)
