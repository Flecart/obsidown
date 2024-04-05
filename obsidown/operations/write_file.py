import os
import frontmatter

from obsidown.config import Config
from obsidown.operations.base import MdFile, MdOperations


class WriteFile(MdOperations):
    def __init__(self, config: Config):
        self.config = config

    def __call__(self, file: MdFile) -> MdFile:
        """Writes the markdown files to the output directory."""

        end_path = os.path.join(
            self.config.output.filesystem,
            self.config.output.path,
            os.path.basename(file.filename),
        )

        end_content = frontmatter.Post(file.contents, **file.metadata)
        with open(end_path, "w") as f:
            f.write(frontmatter.dumps(end_content))

        return file
