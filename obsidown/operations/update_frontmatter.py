import os

from obsidown import utils
from obsidown.config import Config
from obsidown.operations.base import MdFile, MdOperations


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

        no_extension = utils.remove_extension(os.path.basename(file.filename))
        metadata = self.new_metadata
        metadata["title"] = no_extension
        metadata["permalink"] = utils.to_kebab_case(
            self.config.output.path + "/" + no_extension
        )

        if "language" in file.metadata:
            metadata["tags"] = file.metadata["language"]

        return MdFile(
            metadata=metadata,
            contents=file.contents,
            references=file.references,
            filename=file.filename,
        )
