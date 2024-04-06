from obsidown.config import Config
from obsidown.operations.base import MdOperations
from obsidown.operations.citations import CitationConvert
from obsidown.operations.link_convert import LinkConvert
from obsidown.operations.math_convert import MathConvert
from obsidown.operations.remove_after_string import RemoveAfterString
from obsidown.operations.update_frontmatter import UpdateFrontMatter
from obsidown.operations.write_file import WriteFile


def dispatch(
    name: str, config: Config, not_cited_refs: list[str], *args, **kwargs
) -> MdOperations:
    """Dispatch the operation to the correct class."""
    match name:
        case "link_convert":
            return LinkConvert(config, not_cited_refs, *args, **kwargs)
        case "remove_after_string":
            return RemoveAfterString(*args, **kwargs)
        case "math_convert":
            return MathConvert(*args, **kwargs)
        case "update_frontmatter":
            return UpdateFrontMatter(config, *args, **kwargs)
        case "write_file":
            return WriteFile(config, *args, **kwargs)
        case "citation_convert":
            return CitationConvert(*args, **kwargs)
        case _:
            raise ValueError(f"Unknown operation: {name}")
