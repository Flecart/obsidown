import frontmatter
from pydantic import BaseModel

from obsidown import utils


class MdFile(BaseModel):
    metadata: dict
    contents: str
    references: list[str]
    filename: str

    @classmethod
    def from_filename(cls, filename: str):
        metadata, contents, references = _load_contents(filename)
        new_instance = cls(
            metadata=metadata,
            contents=contents,
            references=references,
            filename=filename,
        )
        return new_instance


class MdOperations:
    """Operations that run on a single markdown file"""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, file: MdFile, *args, **kwargs) -> MdFile:
        pass


def _load_contents(filepath: str) -> tuple[dict, str, list[str]]:
    """Load the contents from the config file.

    Returns
    -------
    tuple[
        dict
            The metadata of the file
        list[str]
            The contents of the file
        Second dict
            The references of the file
    """

    with open(filepath, "r") as file:
        metadata, contents = frontmatter.parse(file.read())
    return metadata, contents, utils.extract_links(contents)
