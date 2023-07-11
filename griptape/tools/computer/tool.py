import logging
import os
import shutil
import tempfile
import stringcase
from typing import Optional
import docker
from attr import define, field, Factory
from docker.errors import NotFound
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


@define
class Computer(BaseTool):
    workdir: Optional[str] = field(default=None, kw_only=True)
    env: dict = field(factory=dict, kw_only=True)
    dockerfile_path = field(
        default=Factory(
            lambda self: f"{os.path.join(self.tool_dir(), 'Dockerfile')}",
            takes_self=True,
        ),
        kw_only=True,
    )
    docker_client: docker.DockerClient = field(
        default=Factory(lambda self: self.default_docker_client(), takes_self=True),
        kw_only=True,
    )

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        self.remove_existing_container(self.container_name(self))
        self.build_image(self)

    @activity(
        config={
            "description": "Can be used to execute Python code in the virtual machine to solve any programmatic task, "
            "access files, and file system. If you need to use code output use `print` statements.",
            "schema": Schema(
                {
                    Literal("code", description="Python code to execute"): str,
                    Literal(
                        "filename",
                        description="name of the file to put the Python code in before executing it",
                    ): str,
                }
            ),
        }
    )
    def execute_code(self, params: dict) -> BaseArtifact:
        code = params["values"]["code"]
        filename = params["values"]["filename"]

        return self.execute_code_in_container(filename, code)

    def execute_code_in_container(self, filename: str, code: str) -> BaseArtifact:
        container_workdir = "/griptape"
        container_file_path = os.path.join(container_workdir, filename)

        if self.workdir:
            tempdir = None
            local_workdir = self.workdir
        else:
            tempdir = tempfile.TemporaryDirectory()
            local_workdir = tempdir.name

        local_file_path = os.path.join(local_workdir, filename)

        try:
            with open(local_file_path, "w") as f:
                f.write(code)

            command = ["python", container_file_path]
            binds = {local_workdir: {"bind": container_workdir, "mode": "rw"}}

            container = self.docker_client.containers.run(
                self.image_name(self),
                environment=self.env,
                command=command,
                name=self.container_name(self),
                volumes=binds,
                stdout=True,
                stderr=True,
                detach=True,
            )

            container.wait()

            stderr = container.logs(stdout=False, stderr=True).decode().strip()
            stdout = container.logs(stdout=True, stderr=False).decode().strip()

            container.stop()
            container.remove()

            if stderr:
                return ErrorArtifact(stderr)
            else:
                return TextArtifact(stdout)
        except Exception as e:
            return ErrorArtifact(f"error executing code: {e}")
        finally:
            if tempdir:
                tempdir.cleanup()

    def default_docker_client(self) -> Optional[docker.DockerClient]:
        try:
            return docker.from_env()
        except Exception as e:
            logging.error(e)

            return None

    def image_name(self, tool: BaseTool) -> str:
        return f"{stringcase.snakecase(tool.name)}_image"

    def container_name(self, tool: BaseTool) -> str:
        return f"{stringcase.snakecase(tool.name)}_container"

    def remove_existing_container(self, name: str) -> None:
        try:
            existing_container = self.docker_client.containers.get(name)
            existing_container.remove(force=True)

            logging.info(f"Removed existing container: {name}")
        except NotFound:
            pass

    def build_image(self, tool: BaseTool) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(self.dockerfile_path, temp_dir)

            image = self.docker_client.images.build(
                path=temp_dir, tag=self.image_name(tool), rm=True, forcerm=True
            )

            response = [line for line in image]

            logging.info(f"Built image: {response[0].short_id}")
