from obsidown import utils
from obsidown.operations.base import MdFile, MdOperations


class RemoveAfterString(MdOperations):
    def __init__(self, string: str):
        self.to_remove = string

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the math equations from the notes into the correct format for the markdown files."""
        contents = utils.remove_after_string(file.contents, self.to_remove)
        return MdFile(
            filename=file.filename,
            metadata=file.metadata,
            contents=contents,
            references=file.references,
        )
