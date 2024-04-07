from obsidown import utils
from obsidown.operations.base import MdFile, MdOperations


class MathConvert(MdOperations):
    def __init__(self, engine: str = "mathjax"):
        self.engine = engine

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the math equations from the notes into the correct format for the markdown files."""
        # TODO: handle the | inside the math equations""

        if self.engine == "katex":
            # TODO: not completely fixed!
            contents = utils.convert_katex(file.contents)
        elif self.engine == "mathjax":  # For kramdown
            contents = utils.convert_maths(file.contents)
        return MdFile(
            metadata=file.metadata,
            contents=contents,
            references=file.references,
            filename=file.filename,
        )
