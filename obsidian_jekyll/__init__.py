import re

def convert_maths(page):
    # Replace single dollar sign math expressions with double dollar sign expressions
    page = re.sub(r'(?<!\$)\$([^\$]+?)\$(?!\$)', r'$$\1$$', page)

    # Add newline characters before and after double dollar sign expressions if they are not already present
    page = re.sub(r'\$\$\n([^\$]+?)\n\$\$', r'\n$$\n\1\n$$\n', page, flags=re.DOTALL)

    return page

if __name__ == "__main__":
    print("-" + convert_maths("$$x = y$$") + "-")