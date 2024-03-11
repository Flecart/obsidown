import yaml
import os
from pydantic import BaseModel
import frontmatter
from . import utils


def convert(content: str):
    """ Converts every content of the page to Jekyll markdown format.
    
    """


def load_contents(filepath: str) -> tuple[dict, str, list[str]]:
    """ Load the contents from the config file.
    
    Returns
    -------
    tuple[str, list[str]
            The contents of the file
        Second dict
            The references of the file
    """

    with open(filepath, "r") as file:
        metadata, contents = frontmatter.parse(file.read())
    return metadata, contents, utils.extract_links(contents)

def load_images(filepath: str) -> list[str]:
    """ Returns a list of all files in the directory.
    """
    result = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if utils.is_image(file):
                result.append(os.path.join(root, file))
    
    return result

def load_files(filepath: str) -> list[str]:
    """ Returns a list of all files in the directory.
    """
    result = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if not utils.is_image(file):
                result.append(os.path.join(root, file))
    
    return result

# def set_front_matter(contents: str) -> str:


class SourcesList(BaseModel):
    paths: list[str]
    images: list[str]

class Destination(BaseModel):
    base: str  # URL base
    path: str  # where to store the files
    images: str  # where to store the images
    filesystem: str  # the location of the jekyll app

class Config(BaseModel):
    sources: SourcesList
    output: Destination

def main():
    """ List of paths 
    
    """
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    config = Config(**config)
    print(config)

    images = []
    for images_path in config.sources.images:
        images += load_images(images_path)

    files = []
    for path in config.sources.paths:
        files += load_files(path)

    image_refs = set()
    for file in files:
        _, contents, references = load_contents(file)
        print(file)
        # post = frontmatter.Post(contents, **metadata)

        # val = frontmatter.dumps(post)
        # We need to remove the references that will not be present in the final file
        not_cited_refs = set()
        for ref in references:
            ref = ref.split("|")[0] # don't want the aliases!
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

        contents = utils.convert_maths(contents)
        contents = utils.convert_external_links(contents)
        if (len(references) > 0):
            contents = utils.filter_link(contents, not_cited_refs)
            contents = utils.convert_images(contents, "/" + config.output.images)
            contents = utils.convert_links(contents, "/" + config.output.path)
        contents = utils.remove_after_string(contents, "# Registro ripassi")
        contents = utils.remove_after_string(contents, "## Note di ripasso")

        no_extension = utils.remove_extension(os.path.basename(file))
        new_metadata = {
            "layout": "page",
            "title": no_extension,
            "permalink": utils.to_kebab_case(config.output.path + "/" + no_extension),
            "tags": "italian"
        }

        post = frontmatter.Post(contents, **new_metadata)
        val = frontmatter.dumps(post)
        dir = os.path.join(config.output.filesystem, config.output.path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(os.path.join(config.output.filesystem, config.output.path, os.path.basename(file)), "w") as f:
            f.write(val)

    # Now write the images on the filesystem
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
        output_dir = os.path.join(config.output.filesystem, config.output.images, dirname)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(os.path.join(config.output.filesystem, config.output.images, image), "wb") as f:
            with open(image_local_path, "rb") as i:
                f.write(i.read())

    # Now create index pages
    index_frontmatter = {
        "layout": "page",
        "title": "Notes",
        "permalink": "/notes",
        "tags": "italian"
    }
    index_content = "Here you can find the categories of all the notes on the site: \n"

    categories = {}
    for file in files:
        _, contents, references = load_contents(file)
        no_extension = utils.remove_extension(os.path.basename(file))
        target = "/" + utils.to_kebab_case(config.output.path + "/" + no_extension)

        # The name of the directory is the category
        current_category = os.path.basename(os.path.dirname(file)).replace("-", " ").title()
        if current_category not in categories:
            categories[current_category] = f"- [{no_extension}]({target})\n"
        else:
            categories[current_category] += f"- [{no_extension}]({target})\n"

    index_content += f"## Table of Contents\n"
    for category in categories:
        index_content += f"- [{category}](#{utils.to_kebab_case(category)})\n"
    index_content += "\n\n"

    for category, content in categories.items():
        index_content += f"## {category}\n"
        index_content += content + "\n\n"
    with open(os.path.join(config.output.filesystem, config.output.path, "index.md"), "w") as f:
        f.write(frontmatter.dumps(frontmatter.Post(index_content, **index_frontmatter)))

if __name__ == "__main__":
    main()