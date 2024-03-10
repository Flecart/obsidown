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
    page = re.sub(r'!\[\[([^\]]+?)(\.jpeg|\.webm|\.png)\|([0-9|\s]+)\]\]', r'<img src="' + base + '/' + r'\1\2" width="\3" alt="\1">', page)
    # Convert markdown image tags to html image tags
    page = re.sub(r'!\[\[([^\]]+?)(\.jpeg|\.webm|\.png)\]\]', r'<img src="' + base + '/' + r'\1\2" alt="\1">', page)

    return page

if __name__ == "__main__":
    print("-" + convert_maths("$$x = y$$") + "-")