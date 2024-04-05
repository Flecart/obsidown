from obsidown import utils
from obsidown.operations.base import MdFile, MdOperations


class MathConvert(MdOperations):
    def __call__(self, file: MdFile) -> MdFile:
        """Converts the math equations from the notes into the correct format for the markdown files."""
        # TODO: handle the | inside the math equations""
        contents = utils.convert_maths(file.contents)
        return MdFile(
            metadata=file.metadata,
            contents=contents,
            references=file.references,
            filename=file.filename,
        )
