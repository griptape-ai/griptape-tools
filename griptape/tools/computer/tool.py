import logging
import os
import shutil
import tempfile
from pathlib import Path
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
    local_workdir: Optional[str] = field(default=None, kw_only=True)
    container_workdir: str = field(default="/griptape", kw_only=True)
    env_vars: dict = field(factory=dict, kw_only=True)
    dockerfile_path: str = field(
        default=Factory(
            lambda self: f"{os.path.join(self.tool_dir(), 'resources/Dockerfile')}",
            takes_self=True,
        ),
        kw_only=True,
    )
    requirements_txt_path: str = field(
        default=Factory(
            lambda self: f"{os.path.join(self.tool_dir(), 'resources/requirements.txt')}",
            takes_self=True,
        ),
        kw_only=True,
    )
    docker_client: docker.DockerClient = field(
        default=Factory(lambda self: self.default_docker_client(), takes_self=True),
        kw_only=True,
    )

    __tempdir: Optional[tempfile.TemporaryDirectory] = field(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        if self.local_workdir:
            Path(self.local_workdir).mkdir(parents=True, exist_ok=True)
        else:
            self.__tempdir = tempfile.TemporaryDirectory()
            self.local_workdir = self.__tempdir.name

    @docker_client.validator
    def validate_docker_client(self, _, docker_client: docker.DockerClient) -> None:
        if not docker_client:
            raise ValueError("Docker client can't be initialized: make sure the Docker daemon is running")

    @property
    def schema_template_args(self) -> dict:
        return {
            "dependencies": self.dependencies()
        }

    def install_dependencies(self, env: Optional[dict[str, str]] = None) -> None:
        super().install_dependencies(env)

        self.remove_existing_container(self.container_name(self))
        self.build_image(self)

    @activity(
        config={
            "description": "Can be used to execute Python code to solve any programmatic tasks and access and analyze"
                           " files in the file system. If you need to use code output use `print` statements. "
                           "You have access to the following external Python libraries: "
                           "{{ dependencies }}",
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

    @activity(
        config={
            "description": "Can be used to execute shell commands in Linux",
            "schema": Schema(
                {
                    Literal("command", description="shell command to execute"): str,
                }
            ),
        }
    )
    def execute_command(self, params: dict) -> BaseArtifact:
        command = params["values"]["command"]

        return self.execute_command_in_container(command)

    def execute_command_in_container(self, command: str) -> BaseArtifact:
        try:
            binds = {self.local_workdir: {"bind": self.container_workdir, "mode": "rw"}}

            container = self.docker_client.containers.run(
                self.image_name(self),
                environment=self.env_vars,
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
            return ErrorArtifact(f"error executing command: {e}")

    def execute_code_in_container(self, filename: str, code: str) -> BaseArtifact:
        container_file_path = os.path.join(self.container_workdir, filename)

        if self.local_workdir:
            tempdir = None
            local_workdir = self.local_workdir
        else:
            tempdir = tempfile.TemporaryDirectory()
            local_workdir = tempdir.name

        local_file_path = os.path.join(local_workdir, filename)

        try:
            with open(local_file_path, "w") as f:
                f.write(code)

            return self.execute_command_in_container(
                f"python {container_file_path}"
            )
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
            shutil.copy(self.requirements_txt_path, temp_dir)

            image = self.docker_client.images.build(
                path=temp_dir, tag=self.image_name(tool), rm=True, forcerm=True
            )

            response = [line for line in image]

            logging.info(f"Built image: {response[0].short_id}")

    def dependencies(self) -> list[str]:
        with open(self.requirements_txt_path, "r") as file:
            return [l.strip() for l in file.readlines()]

    def __del__(self) -> None:
        if self.__tempdir:
            self.__tempdir.cleanup()
