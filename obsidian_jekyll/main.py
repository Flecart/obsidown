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
    images: str  # where to store the images
    path: str  # where to store the files
class Config(BaseModel):
    sources: SourcesList

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
    import re
    for file in files:
        # metadata, contents, references = load_contents(file)
        
        with open(file, "r") as f:
            contents = f.read()
        contents = re.sub(r'\*\*+', r'**', contents)
        print(contents)
        # post = frontmatter.Post(contents, **metadata)

        # val = frontmatter.dumps(post)
        with open (file, "w") as f:
            f.write(contents)
        # if (len(references) > 0):
        #     contents = utils.convert_maths(contents)
        #     contents = utils.convert_images(contents)
        #     contents = utils.convert_links(contents)
        #     print(file, metadata, references)
        #     print()
        #     print(contents)
        #     break


if __name__ == "__main__":
    main()