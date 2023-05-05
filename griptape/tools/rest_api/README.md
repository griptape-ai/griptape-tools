```python
from json import dumps
import logging
from griptape.drivers import MemoryStorageDriver, OpenAiPromptDriver
from griptape.memory import Memory
from griptape.ramps import StorageRamp
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import RestApi

storage = StorageRamp(driver=MemoryStorageDriver())

posts_client = RestApi(
    base_url="https://jsonplaceholder.typicode.com",
    path="posts",
    ramps={
        'get': [storage],
        'post': [storage],
        'put': [storage],
        'patch': [storage],
        'delete': [storage],
    },
    description="Allows for creating, updating, deleting, patching, and getting posts.",
    request_body_schema=dumps(
        {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "http://example.com/example.json",
            "type": "object",
            "default": {},
            "title": "Root Schema",
            "required": ["title", "body", "userId"],
            "properties": {
                "title": {
                    "type": "string",
                    "default": "",
                    "title": "The title Schema",
                },
                "body": {
                    "type": "string",
                    "default": "",
                    "title": "The body Schema",
                },
                "userId": {
                    "type": "integer",
                    "default": 0,
                    "title": "The userId Schema",
                },
            },
        }
    ),
    request_query_params_schema=dumps(
        {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "http://example.com/example.json",
            "type": "object",
            "default": {},
            "title": "Root Schema",
            "required": ["userId"],
            "properties": {
                "userId": {
                    "type": "string",
                    "default": "",
                    "title": "The userId Schema",
                },
            },
        }
    ),
    request_path_params_schema=dumps(
        {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "http://example.com/example.json",
            "type": "array",
            "default": [],
            "title": "Root Schema",
            "items": {
                "anyOf": [
                    {
                        "type": "string",
                        "title": "Post id",
                    },
                ]
            },
        }
    ),
    response_body_schema=dumps(
        {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "http://example.com/example.json",
            "type": "object",
            "default": {},
            "title": "Root Schema",
            "required": ["id", "title", "body", "userId"],
            "properties": {
                "id": {
                    "type": "integer",
                    "default": 0,
                    "title": "The id Schema",
                },
                "title": {
                    "type": "string",
                    "default": "",
                    "title": "The title Schema",
                },
                "body": {
                    "type": "string",
                    "default": "",
                    "title": "The body Schema",
                },
                "userId": {
                    "type": "integer",
                    "default": 0,
                    "title": "The userId Schema",
                },
            },
        }
    ),
)

pipeline = Pipeline(
    memory=Memory(),
    prompt_driver=OpenAiPromptDriver(
        temperature=0.1
    ),

)

pipeline.add_tasks(
    ToolkitTask(
        "Get the title of post 1.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Get the titles of all posts.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Create a post for user 1 with title 'My First Post' and body 'Hello world!'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Update post 1 with a new body: 'Hello universe!'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Patch post 1 with a new title: 'My First Post, A Journey'.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Delete post 1.",
        tools=[posts_client],
    ),
    ToolkitTask(
        "Get the body of all the comments for post 1.",
        tools=[posts_client],
    ),
)

pipeline.run()
```
```
