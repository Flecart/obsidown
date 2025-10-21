import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

def interpolate_weight(dt: datetime) -> float:
    """Interpolates a weight for a given datetime between 2022 and 2030, considering full time granularity."""
    # Define start and end times

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    start_dt = datetime(2017, 1, 1, 0, 0, 0)
    end_dt = datetime(2030, 12, 31, 23, 59, 59)

    # Define corresponding weights
    start_weight, end_weight = 1, 3_000_000

    # Ensure dt is within the valid range
    if dt < start_dt:
        return float(start_weight)
    if dt > end_dt:
        return float(end_weight)

    # Compute interpolation factor based on total seconds elapsed
    total_seconds = (end_dt - start_dt).total_seconds()
    elapsed_seconds = (dt - start_dt).total_seconds()
    factor = elapsed_seconds / total_seconds

    # Linear interpolation
    weight = start_weight + factor * (end_weight - start_weight)
    
    # Now we have to invert the process so that the smaller weight is for the most recent commit
    weight = end_weight - weight + start_weight
    return int(weight)


def parse_datetime(date_str: str):
    """
    Parse the time from the git log.
    date_str = "Mon Apr 8 01:33:22 2024 +0200"
    """
    dt = datetime.strptime(date_str[:-6], "%a %b %d %H:%M:%S %Y")
    offset_sign = 1 if date_str[-5] == '+' else -1
    offset_hours = int(date_str[-4:-2])
    offset_minutes = int(date_str[-2:])
    offset_delta = timedelta(hours=offset_hours, minutes=offset_minutes)
    dt = dt.replace(tzinfo=timezone(offset_sign * offset_delta))

    return dt


def convert_maths(page: str):
    """Convert single dollar sign math expressions to double dollar sign expressions.
    Add newline characters before and after double dollar sign expressions if they are not already present.

    """
    # Add newline characters before and after double dollar sign expressions if they are not already present
    page = re.sub(r"\$\$\n([^\$]+?)\n\$\$", r"\n$$\n\1\n$$\n", page, flags=re.DOTALL)

    # Replace single dollar sign math expressions with double dollar sign expressions
    page = re.sub(r"(?<!\$)\$([^\$]+?)\$(?!\$)", r"$$\1$$", page)

    return page


def convert_katex(page: str):
    """Converts elements found problematic into well formed katex elements

    Example
    -------
    >>> convert_katex("$$x = y \\\\$$ and $a = b$")
    "$$x = y \\\\\\$$ and $$a = b$$"
    >>> convert_katex("$$x = y_{i}$$")
    "$$x = y\\_{i}$$"
    """
    # Replace \\ with \\\\
    dollar_matches = r"\$\$([^\$]+?)\\\\([^\$\\]+?)\$\$"
    while re.search(dollar_matches, page):
        page = re.sub(dollar_matches, r"$$\1\\\\\\\2$$", page)
        print(page)

    # Replace _{ with \_{ and } with }
    substring = r"\$\$([^\$\\]+?)_{([^\$]+?)}\$\$"
    while re.search(substring, page):
        page = re.sub(substring, r"$$\1\\_{\2}$$", page)

    return page


def convert_images(page: str, base: str = ""):
    """Convert image obsidian markdown tags into html tags.
    Args
    ----
    page: str
        The page content to be converted.
    base: str
        The base url for the images.
    """
    # First convert image tags with numbers to html image tags
    page = re.sub(
        r"!\[\[([^\]]+?)(\.jpeg|\.webp|\.png|.jpg)\|([0-9|\s]+)\]\]",
        r'<img src="' + base + "/" + r'\1\2" width="\3" class="center" alt="\1"/>',
        page,
    )

    # Convert image tags with comments to figure tags
    page = re.sub(
        r"!\[\[([^\]]+?)(\.jpeg|\.webp|\.png|.jpg)\|(.+)\]\]",
        r'''<figure class="center">
<img src="''' + base + "/" + r'''\1\2" style="width: 100%"   alt="\1" title="\1"/>
<figcaption><p style="text-align:center;">\3</p></figcaption>
</figure>'''
    , page)

    # Convert markdown image tags to html image tags
    page = re.sub(
        r"!\[\[([^\]]+?)(\.jpeg|\.webp|\.png|.jpg)\]\]",
        r'<img src="' + base + "/" + r'\1\2" style="width: 100%" class="center" alt="\1">',
        page,
    )

    return page


def convert_external_links(page: str):
    """If there is an external link without the markdown format, convert it to the markdown format.

    Example
    -------
    >>> convert_external_links("https://google.com")
    "[https://google.com](https://google.com)"
    >>> convert_external_links("[https://google.com](https://google.com)")
    "[https://google.com](https://google.com)"
    """

    # Questo regex è un po' fragile, ma è difficile da fare, dovresti avere lookahead infinito!
    return re.sub(
        r"(?<!\[)(https?:\/\/[^\s\]\(\)]+)(?!(\)|[a-z]|\.|[0-9]|[A-Z]|\/|_|,|-|=|\?|&|~|#|%|:))",
        r"[\1](\1)",
        page,
    )


def convert_links(page: str, base: str = ""):  #
    """Convert the links to the markdown format.
    # Warning: this assumes images to be links to!

    Example
    -------
    >>> convert_links("hello [[world]]", "https://google.com")
    "hello <a href="https://google.com/world">{world}</a>"
    """
    # first convert hashtag links

    def convert_to_md(x):
        return "[{}]({})".format(x, to_kebab_case(x))

    def convert_two_to_md(x, y):
        return "[{}]({})".format(y, to_kebab_case(x))

    page = re.sub(
        r"\[\[(#[^\]]+?)\|([^\]]+)\]\]",
        lambda x: convert_two_to_md(x.group(1), x.group(2)),
        page,
    )
    page = re.sub(r"\[\[(#[^\]]+?)\]\]", lambda x: convert_to_md(x.group(1)), page)

    # then outer links
    def convert_to_md2(x):
        return "[{}]({}/{})".format(x, base, to_kebab_case(x))

    def convert_two_to_md2(x, y):
        return "[{}]({}/{})".format(y, base, to_kebab_case(x))

    page = re.sub(
        r"\[\[([^\]]+?)\|([^\]]+)\]\]",
        lambda x: convert_two_to_md2(x.group(1), x.group(2)),
        page,
    )
    page = re.sub(r"\[\[([^\]]+?)\]\]", lambda x: convert_to_md2(x.group(1)), page)

    # convert standard links
    def replace_link(match):
        text, url = match.groups()
        full_url = urljoin(base, url)  # Resolve relative URLs if base is provided
        return f'<a href="{full_url}">{text}</a>'
    
    pattern = re.compile(r'\[([^\[\]]*?)\]\((.*?)\)')
    return pattern.sub(replace_link, page)


def filter_link(page: str, links: list[str]):
    """removes the links with  link in the page, making it a normal string

    Example
    -------
    >>> filter_link("hello [[world]]", ["world"])
    "hello world"

    """

    for link in links:
        page = re.sub(r"!?\[\[{}\]\]".format(link), link, page)

    return page


def extract_links(page: str):
    """Extract all the links from the page."""
    return re.findall(r"\[\[(.+?)\]\]", page)


def is_image(name: str):
    """Check if a file is an image."""
    return (
        name.endswith(".jpeg")
        or name.endswith(".png")
        or name.endswith(".webp")
        or name.endswith(".jpg")
    )


def to_kebab_case(name: str):
    """Convert a string to kebab case."""
    return name.lower().replace("'", " ").replace(" ", "-")


def remove_extension(name: str):
    """Remove the extension from a file name."""
    if "." not in name:
        return name
    return ".".join(name.split(".")[:-1])


def remove_after_string(content: str, string: str, line: bool = False) -> str:
    """Remove everything after a string."""
    if not line:
        return content.split(string)[0]
    else:
        # Remove everything after the first occurrence of the string in the line
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if string in line:
                lines[i] = line.split(string)[0]
        return "\n".join(lines)
