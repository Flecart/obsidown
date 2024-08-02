import os
import random

from obsidown import utils
from obsidown.config import Config
from obsidown.operations.base import MdFile, MdOperations
import copy


class UpdateFrontMatter(MdOperations):
    def __init__(self, config: Config, frontmatter: dict[str, str]):
        self.config = config

        self.new_metadata = frontmatter
        # TODO: this should be configured from args
        # self.new_metadata = {
        #     "layout": "page",
        #     "title": None,
        #     "permalink": None,
        #     "tags": "italian",
        # }

    def __call__(self, file: MdFile) -> MdFile:
        """Updates the frontmatter of the markdown files."""

        metadata = copy.deepcopy(self.new_metadata)

        if "title" in file.metadata:
            metadata["title"] = file.metadata["title"]
        else:
            no_extension = utils.remove_extension(os.path.basename(file.filename))
            metadata["title"] = no_extension

        if "url" in file.metadata:
            metadata["url"] = file.metadata["url"]
        # metadata["permalink"] = utils.to_kebab_case(
        #     self.config.output.path + "/" + no_extension
        # )

        # metadata["url"] = utils.to_kebab_case(
        #     self.config.output.path + "/" + no_extension
        # )

        if "language" in file.metadata:
            metadata["language"] = file.metadata["language"]

        if "tags" in file.metadata:
            metadata["tags"] = file.metadata["tags"]
        else:
            metadata["tags"] = ["no-tags"]

        if "summary" in file.metadata:
            metadata["summary"] = file.metadata["summary"]
            metadata["description"] = file.metadata["summary"]

        if "weight" in file.metadata:
            metadata["weight"] = file.metadata["weight"]
        else:
            metadata["weight"] = random.randint(1, 50)  # play lottery lol

        print(metadata)

        return MdFile(
            metadata=metadata,
            contents=file.contents,
            references=file.references,
            filename=file.filename,
        )
