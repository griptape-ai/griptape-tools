import os
from typing import Union
from attr import define, field
from griptape.artifacts import ErrorArtifact, BlobArtifact, ListArtifact, InfoArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


@define
class FileManager(BaseTool):
    dir: str = field(default=os.getcwd(), kw_only=True)

    @activity(config={
        "description": "Can be used to load files",
        "schema": Schema({
            Literal(
                "paths",
                description="Paths to files to be loaded in the POSIX format. "
                            "For example, ['foo/bar/file.txt']"
            ): []
        })
    })
    def load_from_disk(self, params: dict) -> Union[ErrorArtifact, ListArtifact]:
        list_artifact = ListArtifact()

        for path in params["values"]["paths"]:
            file_name = os.path.basename(path)
            dir_name = os.path.dirname(path)
            full_path = os.path.join(self.dir, path)

            try:
                with open(full_path, "rb") as file:
                    list_artifact.value.append(
                        BlobArtifact(
                            file.read(),
                            name=file_name,
                            dir=dir_name
                        )
                    )
            except FileNotFoundError:
                return ErrorArtifact(f"file {file_name} not found")
            except Exception as e:
                return ErrorArtifact(f"error loading file: {e}")

        return list_artifact

    @activity(config={
        "description": "Can be used to save files",
        "schema": Schema({
            Literal(
                "paths",
                description="Destination paths in the POSIX format for each artifact to be stored in a file. "
                            "For example, ['foo/bar/file.txt']"
            ): []
        }),
        "pass_artifacts": True
    })
    def save_to_disk(self, params: dict) -> Union[ErrorArtifact, InfoArtifact]:
        new_paths = params["values"]["paths"]
        artifacts = self.artifacts

        if len(artifacts) == 0:
            return ErrorArtifact("files not found")
        elif len(new_paths) == 0:
            return ErrorArtifact("no paths provided")
        else:
            for i, new_path in enumerate(new_paths):
                try:
                    artifact = artifacts[0] if len(artifacts) == 1 else artifacts[i]
                    full_path = os.path.join(self.dir, new_path)

                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    with open(full_path, "wb") as file:
                        value = artifact.value

                        file.write(value.encode() if isinstance(value, str) else value)
                except Exception as e:
                    return ErrorArtifact(f"error writing file to disk: {e}")

            return InfoArtifact(f"saved successfully")
