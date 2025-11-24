from obsidown import utils
from obsidown.operations.base import MdFile, MdOperations


class RemoveSingleCharLines(MdOperations):
    """Remove lines entirely composed of a repeated character."""

    def __init__(self, character: str):
        if len(character) != 1:
            raise ValueError("character must be a single character.")
        self.character = character

    def __call__(self, file: MdFile) -> MdFile:
        contents = utils.remove_single_char_lines(file.contents, self.character)
        return MdFile(
            filename=file.filename,
            metadata=file.metadata,
            contents=contents,
            references=file.references,
        )

