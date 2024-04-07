from typing import Iterable
from obsidown import utils
from obsidown.config import Config
from obsidown.operations.base import MdFile, MdOperations


class LinkConvert(MdOperations):
    def __init__(self, config: Config, not_cited_refs: Iterable[str]):
        self.config = config
        self.not_cited_refs = not_cited_refs

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the links from the notes into the correct format for the markdown files."""

        contents = utils.convert_external_links(file.contents)
        if len(file.references) > 0:
            contents = utils.filter_link(contents, self.not_cited_refs)
            contents = utils.convert_images(contents, "/" + self.config.output.images)
            contents = utils.convert_links(contents, "/" + self.config.output.base)
        contents = utils.convert_links(contents)

        return MdFile(
            metadata=file.metadata,
            contents=contents,
            references=file.references,
            filename=file.filename,
        )
