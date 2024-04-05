from typing import Iterable
import yaml
import os
import frontmatter

from obsidown.config import Config
from obsidown.operations.base import MdFile, _load_contents
from obsidown.operations.dispatch import dispatch
from . import utils


def main(config: str):
    """List of paths"""

    config = yaml.load(open(config, "r"), Loader=yaml.FullLoader)
    config: Config = Config(**config)

    images = []
    for images_path in config.sources.images:
        images += load_images(images_path)

    files = []
    for path in config.sources.paths:
        files += load_files(path)
    image_refs = set()
    for file in files:
        md_file = MdFile.from_filename(file)

        # We need to remove the references that will not be present in the final file
        not_cited_refs = set()
        for ref in md_file.references:
            ref = ref.split("|")[0]  # don't want the aliases!
            if utils.is_image(ref):
                image_refs.add(ref)
            else:
                # here is image ref, we should count only the first part
                ref = ref.split("#")[0]
                found = False
                for f in files:
                    if ref in f:
                        found = True
                        break

                if not found:
                    not_cited_refs.add(ref)

        for operation in config.pipeline:
            operation = dispatch(
                operation.name, config, not_cited_refs, **operation.options
            )
            md_file = operation(md_file)

    # Now write the images on the filesystem
    save_images(image_refs, images, config)

    # Now create index pages
    index_frontmatter = {
        "layout": "page",
        "title": "Notes",
        "permalink": "/notes",
        "tags": "italian",
    }
    index_content = "Here you can find the categories of all the notes on the site: \n"
    index_content += create_table_contents(files, config)
    with open(
        os.path.join(config.output.filesystem, config.output.path, "index.md"), "w"
    ) as f:
        f.write(frontmatter.dumps(frontmatter.Post(index_content, **index_frontmatter)))


def save_images(image_refs: Iterable[str], images: list[str], config: Config):
    """Saves the images in the correct directory."""
    for image in image_refs:
        image_local_path = None
        for img in images:
            if image in img:
                image_local_path = img
                break
        if image_local_path is None:
            print(f"Image {image} not found in the filesystem")
            continue

        # This is to make sure we don't get any overlapping images!
        # Another solution is to change the name of the image...
        dirname = os.path.dirname(image)
        output_dir = os.path.join(
            config.output.filesystem, config.output.images, dirname
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(
            os.path.join(config.output.filesystem, config.output.images, image), "wb"
        ) as f:
            with open(image_local_path, "rb") as i:
                f.write(i.read())


def create_table_contents(files: list[str], config: Config) -> str:
    """Creates the table of contents for the index page."""
    categories = {}
    for file in files:
        _, contents, references = _load_contents(file)
        no_extension = utils.remove_extension(os.path.basename(file))
        target = "/" + utils.to_kebab_case(config.output.path + "/" + no_extension)

        # The name of the directory is the category
        current_category = (
            os.path.basename(os.path.dirname(file)).replace("-", " ").title()
        )
        if current_category not in categories:
            categories[current_category] = f"- [{no_extension}]({target})\n"
        else:
            categories[current_category] += f"- [{no_extension}]({target})\n"

    index_content = "## Table of Contents\n"
    for category in categories:
        index_content += f"- [{category}](#{utils.to_kebab_case(category)})\n"
    index_content += "\n\n"

    for category, content in categories.items():
        index_content += f"## {category}\n"
        index_content += content + "\n\n"

    return index_content


def load_images(filepath: str) -> list[str]:
    """Returns a list of all files in the directory."""
    result = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if utils.is_image(file):
                result.append(os.path.join(root, file))

    return result


def load_files(filepath: str) -> list[str]:
    """Returns a list of all files in the directory."""
    result = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if not utils.is_image(file):
                result.append(os.path.join(root, file))

    return result


if __name__ == "__main__":
    main()
