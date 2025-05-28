from obsidown import utils
from obsidown.operations.base import MdFile, MdOperations


class RemoveAfterString(MdOperations):
    def __init__(self, string: str, line: bool = False):
        self.to_remove = string
        self.line = line

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the math equations from the notes into the correct format for the markdown files."""
        contents = utils.remove_after_string(file.contents, self.to_remove, line=self.line)
        return MdFile(
            filename=file.filename,
            metadata=file.metadata,
            contents=contents,
            references=file.references,
        )
