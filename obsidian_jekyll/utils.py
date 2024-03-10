import re

def convert_maths(page: str):
    """ Convert single dollar sign math expressions to double dollar sign expressions.
    Add newline characters before and after double dollar sign expressions if they are not already present.
    
    """
    # Replace single dollar sign math expressions with double dollar sign expressions
    page = re.sub(r'(?<!\$)\$([^\$]+?)\$(?!\$)', r'$$\1$$', page)

    # Add newline characters before and after double dollar sign expressions if they are not already present
    page = re.sub(r'\$\$\n([^\$]+?)\n\$\$', r'\n$$\n\1\n$$\n', page, flags=re.DOTALL)

    return page

def convert_images(page: str, base: str = ""):
    """ Convert image obsidian markdown tags into html tags. 
    Args
    ----
    page: str
        The page content to be converted.
    base: str
        The base url for the images.
    """
    # First convert image tags with numbers to html image tags
    page = re.sub(r'!\[\[([^\]]+?)(\.jpeg|\.webp|\.png|.jpg)\|([0-9|\s]+)\]\]', r'<img src="' + base + '/' + r'\1\2" width="\3" alt="\1">', page)
    # Convert markdown image tags to html image tags
    page = re.sub(r'!\[\[([^\]]+?)(\.jpeg|\.webp|\.png|.jpg)\]\]', r'<img src="' + base + '/' + r'\1\2" alt="\1">', page)

    return page

def convert_links(page: str, base: str = ""):
    """ Convert the links to the Jekyll markdown format. 
    # Warning: this assumes images to be links to!
    """
    convert_to_md = lambda x: "[{}]({}/{})".format(x, base, to_kebab_case(x))
    convert_two_to_md = lambda x, y: "[{}]({}/{})".format(y, base, to_kebab_case(x))

    page = re.sub(r'\[\[([^\]]+?)\|([^\]]+)\]\]', lambda x: convert_two_to_md(x.group(1), x.group(2)), page)
    page = re.sub(r'\[\[([^\]]+?)\]\]', lambda x: convert_to_md(x.group(1)), page)
    return page


def extract_links(page: str):
    """ Extract all the links from the page. """
    return re.findall(r'\[\[([^\]]+?)\]\]', page)

def is_image(name: str):
    """ Check if a file is an image. """
    return name.endswith(".jpeg") or name.endswith(".png") or name.endswith(".webp") or name.endswith(".jpg")

def to_kebab_case(name: str):
    """ Convert a string to kebab case. """
    return name.lower().replace("'", " ").replace(" ", "-")